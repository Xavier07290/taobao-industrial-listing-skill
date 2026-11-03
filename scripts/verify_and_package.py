#!/usr/bin/env python3
"""Check that all Taobao image deliverables are standalone high-resolution PNGs, then ZIP them.

Usage:
  python scripts/verify_and_package.py outputs/HSZ --product HSZ
Requires Pillow: pip install pillow
Fails without packaging if mandatory files are absent, malformed, wrong size, duplicates or
the stitched detail long image does not match the eight separate detail pages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageChops

Image.MAX_IMAGE_PIXELS = None
MAIN = [f"main_{i:02d}.png" for i in range(1, 6)]
DETAIL = [f"detail_{i:02d}.png" for i in range(1, 9)]
REQUIRED = MAIN + ["white_bg.png"] + DETAIL + ["detail_long.png"]


def checksum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--product", default=None, help="Product identifier for ZIP naming")
    args = parser.parse_args()

    folder = args.directory.resolve()
    if not folder.is_dir():
        print(f"ERROR: output folder missing: {folder}", file=sys.stderr)
        return 2
    issues = []
    entries = []
    sha_to_file = {}
    sizes = {}

    for name in REQUIRED:
        path = folder / name
        if not path.is_file():
            issues.append(f"MISSING: {name}")
            continue
        if path.stat().st_size == 0:
            issues.append(f"EMPTY: {name}")
            continue
        try:
            with Image.open(path) as img:
                img.verify()
            with Image.open(path) as img:
                if img.format != "PNG":
                    issues.append(f"NOT PNG: {name}")
                width, height = img.size
                sizes[name] = (width, height)
                if name in MAIN and (width, height) != (1440, 1920):
                    issues.append(f"BAD MAIN SIZE: {name}: {width}x{height}, expected 1440x1920")
                if name == "white_bg.png" and (width, height) != (1440, 1440):
                    issues.append(f"BAD WHITE SIZE: {name}: {width}x{height}, expected 1440x1440")
                if name.startswith("detail_") and width != 1440:
                    issues.append(f"BAD DETAIL WIDTH: {name}: {width}, expected 1440")
        except Exception as exc:
            issues.append(f"BAD IMAGE: {name}: {exc}")
            continue
        digest = checksum(path)
        if digest in sha_to_file:
            issues.append(f"DUPLICATE BYTES: {name} identical to {sha_to_file[digest]}")
        else:
            sha_to_file[digest] = name
        entries.append({"name": name, "sha256": digest, "width": width, "height": height, "bytes": path.stat().st_size})

    if all(name in sizes for name in DETAIL + ["detail_long.png"]):
        expected = sum(sizes[name][1] for name in DETAIL)
        if sizes["detail_long.png"] != (1440, expected):
            issues.append(
                f"LONG HEIGHT DOES NOT MATCH 8 PANELS: {sizes['detail_long.png'][1]} != {expected}"
            )
        else:
            # Spot-check exact image alignment where possible; avoids claiming a composition check
            # when only matching dimensions exist.
            try:
                y = 0
                with Image.open(folder / "detail_long.png") as whole:
                    whole_rgb = whole.convert("RGB")
                    for name in DETAIL:
                        with Image.open(folder / name) as panel:
                            panel_rgb = panel.convert("RGB")
                            w, h = panel_rgb.size
                            patch = whole_rgb.crop((0, y, w, y + h))
                            if ImageChops.difference(patch, panel_rgb).getbbox() is not None:
                                issues.append(f"LONG IMAGE MISMATCH: segment {name} not pixel-equal")
                        y += sizes[name][1]
            except Exception as exc:
                issues.append(f"LONG COMPARE ERROR: {exc}")

    manifest = {"status": "FAIL" if issues else "PASS",
                "product": args.product or folder.name,
                "required_count": len(REQUIRED),
                "verified_count": len(entries),
                "files": entries,
                "issues": issues}
    manifest_path = folder / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    if issues:
        print("DELIVERY FAILED; archive NOT created:\n" + "\n".join("- " + s for s in issues), file=sys.stderr)
        print(f"Report: {manifest_path}")
        return 1

    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", args.product or folder.name).strip("-") or "product"
    archive = folder / f"{safe}_taobao_listing_images.zip"
    optional = ["preview_contact_sheet.png", "qa_report.md", "listing.md", "design_master.md"]
    include = REQUIRED + ["manifest.json"] + [name for name in optional if (folder / name).is_file()]
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in include:
            z.write(folder / name, arcname=name)

    with zipfile.ZipFile(archive, "r") as z:
        test = z.testzip()
        if test is not None or any(name not in z.namelist() for name in REQUIRED):
            print("ZIP INTEGRITY FAILED", file=sys.stderr)
            archive.unlink(missing_ok=True)
            return 1

    print(f"PASS: verified {len(REQUIRED)} independent PNG files.")
    print(f"Manifest: {manifest_path}")
    print(f"ZIP: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
