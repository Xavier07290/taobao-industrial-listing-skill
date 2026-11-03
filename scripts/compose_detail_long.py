#!/usr/bin/env python3
"""Losslessly stack detail_01.png ... detail_08.png into detail_long.png."""
from pathlib import Path
import argparse, sys
from PIL import Image

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("directory",type=Path)
    ap.add_argument("--width",type=int,default=1440)
    ap.add_argument("--output",default="detail_long.png")
    args=ap.parse_args()
    files=[args.directory/f"detail_{i:02d}.png" for i in range(1,9)]
    missing=[str(p) for p in files if not p.is_file()]
    if missing: raise FileNotFoundError("Missing detail panels: "+", ".join(missing))
    panels=[]
    for p in files:
        im=Image.open(p).convert("RGB")
        if im.width!=args.width: raise ValueError(f"{p.name}: width {im.width}, expected {args.width}")
        panels.append(im.copy())
    out=Image.new("RGB",(args.width,sum(im.height for im in panels)),"white")
    y=0
    for im in panels:
        out.paste(im,(0,y)); y+=im.height
    target=args.directory/args.output
    out.save(target,"PNG",optimize=True)
    print(f"Created {target}: {out.width}x{out.height}")
if __name__=="__main__":
    try: main()
    except Exception as e: print(f"ERROR: {e}",file=sys.stderr); raise SystemExit(1)
