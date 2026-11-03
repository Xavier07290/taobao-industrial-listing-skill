#!/usr/bin/env python3
"""Verify V1.2 independent PNG assets and package them only when checks pass.

Usage:
  python scripts/verify_and_package.py outputs/HSZ --product HSZ
Requires Pillow: python -m pip install -r requirements.txt

Machine checks do not establish product authenticity, factual correctness or visual quality.
Those must be recorded separately in qa_report.md.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys, zipfile
from pathlib import Path
from PIL import Image, ImageChops

Image.MAX_IMAGE_PIXELS = None
MAIN=[f"main_{i:02d}.png" for i in range(1,6)]
DETAIL=[f"detail_{i:02d}.png" for i in range(1,9)]
REQUIRED=MAIN+["white_bg.png"]+DETAIL+["detail_long.png"]

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("directory",type=Path)
    ap.add_argument("--product",default=None)
    args=ap.parse_args()
    folder=args.directory.resolve()
    if not folder.is_dir():
        print(f"ERROR: directory missing: {folder}",file=sys.stderr); return 2
    issues=[]; entries=[]; seen={}; sizes={}
    for name in REQUIRED:
        p=folder/name
        if not p.is_file(): issues.append(f"MISSING: {name}"); continue
        if p.stat().st_size==0: issues.append(f"EMPTY: {name}"); continue
        try:
            with Image.open(p) as im:
                im.verify()
            with Image.open(p) as im:
                if im.format!="PNG": issues.append(f"NOT PNG: {name}")
                w,h=im.size; sizes[name]=(w,h)
        except Exception as exc:
            issues.append(f"INVALID IMAGE: {name}: {exc}"); continue
        if name in MAIN and (w,h)!=(1440,1920):
            issues.append(f"BAD MAIN SIZE: {name} is {w}x{h}, expected 1440x1920")
        if name=="white_bg.png" and (w,h)!=(1440,1440):
            issues.append(f"BAD WHITE SIZE: {w}x{h}, expected 1440x1440")
        if name in DETAIL and (w!=1440 or h<600):
            issues.append(f"BAD DETAIL SIZE: {name} is {w}x{h}; expected width 1440 and height >=600")
        digest=sha256(p)
        if digest in seen: issues.append(f"DUPLICATE FILE: {name} identical to {seen[digest]}")
        else: seen[digest]=name
        entries.append({"name":name,"sha256":digest,"width":w,"height":h,"bytes":p.stat().st_size})
    if all(n in sizes for n in DETAIL+["detail_long.png"]):
        expected=sum(sizes[n][1] for n in DETAIL)
        if sizes["detail_long.png"]!=(1440,expected):
            issues.append(f"LONG SIZE MISMATCH: got {sizes['detail_long.png']}, expected {(1440,expected)}")
        else:
            try:
                y=0
                with Image.open(folder/"detail_long.png") as long_im:
                    long_rgb=long_im.convert("RGB")
                    for n in DETAIL:
                        with Image.open(folder/n) as panel:
                            panel_rgb=panel.convert("RGB")
                            h=panel.height
                            crop=long_rgb.crop((0,y,1440,y+h))
                            diff=ImageChops.difference(crop,panel_rgb)
                            if diff.getbbox() is not None: issues.append(f"LONG CONTENT MISMATCH: {n}")
                        y+=sizes[n][1]
            except Exception as exc: issues.append(f"LONG COMPARE ERROR: {exc}")
    manifest={"version":"1.2.0","status":"FAIL" if issues else "MACHINE_PASS",
              "product":args.product or folder.name,"required_count":len(REQUIRED),
              "verified_count":len(entries),"files":entries,"issues":issues,
              "note":"Machine checks do not verify product authenticity, facts, Chinese text meaning or visual quality."}
    manifest_path=folder/"manifest.json"
    manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    if issues:
        print("MACHINE QA FAILED; ZIP NOT CREATED:")
        for issue in issues: print(" - "+issue)
        print(f"Manifest: {manifest_path}")
        return 1
    safe=re.sub(r"[^A-Za-z0-9_-]+","-",args.product or folder.name).strip("-") or "product"
    archive=folder/f"{safe}_taobao_listing_images.zip"
    optional=["preview_contact_sheet.png","design_master.md","product_facts.md","competitor_analysis.md","qa_report.md","listing.md","manifest.json"]
    include=REQUIRED+[n for n in optional if (folder/n).is_file()]
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for n in include: z.write(folder/n,arcname=n)
    with zipfile.ZipFile(archive,"r") as z:
        bad=z.testzip()
        missing=[n for n in REQUIRED if n not in z.namelist()]
    if bad or missing:
        archive.unlink(missing_ok=True)
        print(f"ZIP QA FAILED: bad={bad}, missing={missing}",file=sys.stderr); return 1
    print(f"MACHINE PASS: {len(REQUIRED)} independent PNG assets.")
    print(f"Manifest: {manifest_path}")
    print(f"ZIP: {archive}")
    print("VISUAL_QA and FACT_QA still require separate human/vision review.")
    return 0
if __name__=="__main__": raise SystemExit(main())
