"""Keep a synthetic delivery on disk for manual inspection and reproducibility."""
import argparse
from pathlib import Path
from test_pipeline import fixture, cli

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('output', type=Path)
    args = ap.parse_args()
    folder = args.output.resolve()
    if folder.exists():
        ap.error('Use a new output directory to preserve existing files')
    fixture(folder)
    (folder/'qa_report.md').write_text(
        '# Synthetic engineering smoke test\n\n'
        'MACHINE_QA: See manifest.json and verified ZIP; geometry fixtures only.\n\n'
        'VISUAL_QA: PENDING for real product use. No real product was tested.\n\n'
        'FACT_QA: NOT APPLICABLE; no product claims or specifications.\n', encoding='utf-8')
    cli('verify_and_package.py', folder, '--product', 'ENGINEERING_TEST')
    print(f'TEST ONLY; synthetic shapes, not real product assets: {folder}')
