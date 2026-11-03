#!/usr/bin/env python3
"""Create an optional contact sheet from already-exported final images. Never use it as source assets."""
from pathlib import Path
import argparse, math
from PIL import Image, ImageOps, ImageDraw

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("directory",type=Path)
    ap.add_argument("--output",default="preview_contact_sheet.png")
    ap.add_argument("--columns",type=int,default=3)
    ap.add_argument("--thumb-width",type=int,default=360)
    args=ap.parse_args()
    names=[f"main_{i:02d}.png" for i in range(1,6)]+["white_bg.png"]+[f"detail_{i:02d}.png" for i in range(1,9)]
    files=[args.directory/n for n in names if (args.directory/n).is_file()]
    if not files: raise FileNotFoundError("No final image files found.")
    thumbs=[]
    for p in files:
        im=Image.open(p).convert("RGB")
        h=round(im.height*args.thumb_width/im.width)
        im=im.resize((args.thumb_width,h),Image.Resampling.LANCZOS)
        tile=Image.new("RGB",(args.thumb_width,h+44),"white")
        tile.paste(im,(0,0)); ImageDraw.Draw(tile).text((8,h+12),p.name,fill="#111111")
        thumbs.append(tile)
    cell_h=max(t.height for t in thumbs); rows=math.ceil(len(thumbs)/args.columns)
    sheet=Image.new("RGB",(args.columns*args.thumb_width,rows*cell_h),(225,225,225))
    for i,t in enumerate(thumbs): sheet.paste(t,((i%args.columns)*args.thumb_width,(i//args.columns)*cell_h))
    out=args.directory/args.output; sheet.save(out,"PNG",optimize=True); print(out)
if __name__=="__main__": main()
