"""Synthetic engineering fixtures only. No real product or marketing claims."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
NAMES = ([f'main_{i:02}.png' for i in range(1, 6)] + ['white_bg.png']
         + [f'detail_{i:02}.png' for i in range(1, 9)])


def cli(script, *args, ok=True):
    p = subprocess.run([sys.executable, str(ROOT/'scripts'/script), *map(str, args)],
                       cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    if ok and p.returncode:
        raise AssertionError(p.stdout + p.stderr)
    return p


def fixture(folder):
    """Exercise renderer once per independent canvas, at native delivery size."""
    folder.mkdir(parents=True, exist_ok=True)
    source = folder/'synthetic_layer.png'
    im = Image.new('RGBA', (700, 1000))
    d = ImageDraw.Draw(im)
    d.rectangle((100, 100, 600, 900), fill='#b32932')
    d.ellipse((250, 350, 450, 550), fill='#d0d0d0')
    im.save(source)
    for i, name in enumerate(NAMES):
        size = (1440, 1920) if name.startswith('main') else ((1440, 1440) if name == 'white_bg.png' else (1440, 1200 + i*10))
        layout = {'canvas': {'width': size[0], 'height': size[1], 'background': '#ffffff' if name == 'white_bg.png' else '#15171a'},
                  'layers': [{'type': 'image', 'path': str(source), 'x': 300+i*7, 'y': 150,
                              'width': 700, 'height': 1000, 'fit': 'contain'}]}
        if name != 'white_bg.png':
            layout['layers'].append({'type': 'rect', 'x': 40, 'y': 40, 'width': 50+i*45, 'height': 40, 'fill': '#e42226'})
        path = folder/f'{name}.json'
        path.write_text(json.dumps(layout), encoding='utf-8')
        cli('render_layout.py', path, folder/name)
    cli('compose_detail_long.py', folder)
    cli('make_contact_sheet.py', folder)
    for name in ['design_master.md', 'product_facts.md', 'competitor_analysis.md', 'qa_report.md']:
        (folder/name).write_text('TEST ONLY. Synthetic geometric fixtures. VISUAL_QA: PENDING. FACT_QA: NOT APPLICABLE.\n', encoding='utf-8')


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)/'base'
        fixture(cls.base)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.tmpcase = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmpcase.name)/'case'
        shutil.copytree(self.base, self.folder)

    def tearDown(self):
        self.tmpcase.cleanup()

    def verify(self, ok=True):
        return cli('verify_and_package.py', self.folder, '--product', 'TEST', ok=ok)

    def assert_rejected(self, marker):
        p = self.verify(ok=False)
        self.assertNotEqual(p.returncode, 0, p.stdout)
        self.assertIn(marker, p.stdout)

    def test_complete_delivery(self):
        self.verify()
        manifest = json.loads((self.folder/'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['status'], 'MACHINE_PASS')
        self.assertEqual(manifest['verified_count'], 15)
        with zipfile.ZipFile(self.folder/'TEST_taobao_listing_images.zip') as z:
            self.assertIsNone(z.testzip())
            self.assertTrue(set(NAMES+['detail_long.png', 'manifest.json', 'qa_report.md']) <= set(z.namelist()))
        with Image.open(self.folder/'detail_long.png') as long:
            y = 0
            for name in NAMES[6:]:
                with Image.open(self.folder/name) as panel:
                    self.assertEqual(long.crop((0,y,1440,y+panel.height)).tobytes(), panel.convert('RGB').tobytes())
                    y += panel.height
            self.assertEqual(long.height, y)
        with Image.open(self.folder/'white_bg.png') as im:
            self.assertEqual(im.getpixel((0,0)), (255,255,255))

    def test_missing(self):
        (self.folder/'main_01.png').unlink()
        self.assert_rejected('MISSING')

    def test_bad_size(self):
        Image.new('RGB', (1440, 1800)).save(self.folder/'main_01.png')
        self.assert_rejected('BAD MAIN SIZE')

    def test_corrupt(self):
        (self.folder/'main_01.png').write_bytes(b'broken')
        self.assert_rejected('INVALID IMAGE')

    def test_duplicate_bytes(self):
        shutil.copyfile(self.folder/'main_01.png', self.folder/'main_02.png')
        self.assert_rejected('DUPLICATE')

    def test_duplicate_reencoded_pixels(self):
        with Image.open(self.folder/'main_01.png') as im:
            im.save(self.folder/'main_02.png', compress_level=0)
        self.assert_rejected('DUPLICATE')

    def test_long_wrong_pixels(self):
        path = self.folder/'detail_long.png'
        with Image.open(path) as im:
            im.putpixel((0,0), (1,2,3))
            im.save(path)
        self.assert_rejected('LONG CONTENT MISMATCH')

    def test_long_wrong_height(self):
        Image.new('RGB', (1440, 2000)).save(self.folder/'detail_long.png')
        self.assert_rejected('LONG SIZE MISMATCH')

    def test_stale_zip(self):
        self.verify()
        (self.folder/'main_01.png').unlink()
        self.assert_rejected('MISSING')
        self.assertFalse((self.folder/'TEST_taobao_listing_images.zip').exists(), 'Failed run exposes stale delivery ZIP')

    def test_transparent_long_lossless(self):
        path = self.folder/'detail_01.png'
        with Image.open(path) as im:
            im = im.convert('RGBA')
            im.putpixel((0,0), (255,0,0,0))
            im.save(path)
        cli('compose_detail_long.py', self.folder)
        with Image.open(self.folder/'detail_long.png') as im:
            self.assertEqual(im.convert('RGBA').getpixel((0,0)), (255,0,0,0))

    def test_alpha_mismatch_rejected(self):
        path = self.folder/'detail_long.png'
        with Image.open(path) as im:
            im = im.convert('RGBA')
            r,g,b,_ = im.getpixel((0,0))
            im.putpixel((0,0), (r,g,b,0))
            im.save(path)
        self.assert_rejected('LONG CONTENT MISMATCH')

    def test_compose_cannot_overwrite_source(self):
        p = cli('compose_detail_long.py', self.folder, '--output', 'detail_01.png', ok=False)
        self.assertNotEqual(p.returncode, 0)

    def test_preview_cannot_overwrite_source(self):
        p = cli('make_contact_sheet.py', self.folder, '--output', 'main_01.png', ok=False)
        self.assertNotEqual(p.returncode, 0)

    def test_empty_and_wrong_format(self):
        (self.folder/'main_01.png').write_bytes(b'')
        Image.new('RGB', (1440,1920)).save(self.folder/'main_02.png', format='JPEG')
        p = self.verify(ok=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('EMPTY', p.stdout)
        self.assertIn('NOT PNG', p.stdout)

    def test_compose_missing_and_width(self):
        path = self.folder/'detail_01.png'
        path.unlink()
        self.assertNotEqual(cli('compose_detail_long.py', self.folder, ok=False).returncode, 0)
        Image.new('RGB', (1200,1200)).save(path)
        self.assertNotEqual(cli('compose_detail_long.py', self.folder, ok=False).returncode, 0)

    def test_preview_options(self):
        self.assertNotEqual(cli('make_contact_sheet.py', self.folder, '--columns', 0, ok=False).returncode, 0)

    def test_zip_crc_corruption(self):
        self.verify()
        path = self.folder/'TEST_taobao_listing_images.zip'
        with zipfile.ZipFile(path) as z:
            entry = z.getinfo('main_01.png')
        with path.open('r+b') as f:
            f.seek(entry.header_offset+26)
            name_len = int.from_bytes(f.read(2), 'little')
            extra_len = int.from_bytes(f.read(2), 'little')
            offset = entry.header_offset+30+name_len+extra_len+entry.compress_size//2
            f.seek(offset)
            byte = f.read(1)
            f.seek(offset)
            f.write(bytes([byte[0]^255]))
        with zipfile.ZipFile(path) as z:
            try:
                self.assertIsNotNone(z.testzip())
            except Exception as exc:
                self.assertIsInstance(exc, (zipfile.BadZipFile, __import__('zlib').error))


class Renderer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('renderer', ROOT/'scripts/render_layout.py')
        cls.renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.renderer)

    def test_invalid_fit(self):
        with self.assertRaises(ValueError):
            self.renderer.fit_image(Image.new('RGBA', (10,10)), 20, 20, 'typo')

    def test_text_bbox_offset(self):
        font = os.environ.get('TEST_FONT', 'C:/Windows/Fonts/arial.ttf')
        if not Path(font).is_file():
            self.skipTest('Set TEST_FONT to an existing TrueType font')
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            f = ImageFont.truetype(font, size=48)
            bbox = ImageDraw.Draw(Image.new('RGB', (1,1))).multiline_textbbox((0,0), 'Ag', font=f, spacing=8)
            w,h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            layout = {'canvas': {'width': w, 'height': h, 'background': '#000000'},
                      'layers': [{'type':'text','text':'Ag','font':font,'font_size':48,'width':w,'height':h}]}
            p = folder/'layout.json'
            p.write_text(json.dumps(layout), encoding='utf-8')
            cli('render_layout.py', p, folder/'text.png')
            expected = Image.new('RGB',(w,h))
            ImageDraw.Draw(expected).multiline_text((-bbox[0],-bbox[1]), 'Ag', font=f, fill='white', spacing=8)
            with Image.open(folder/'text.png') as result:
                self.assertEqual(result.tobytes(), expected.tobytes())


if __name__ == '__main__':
    unittest.main()
