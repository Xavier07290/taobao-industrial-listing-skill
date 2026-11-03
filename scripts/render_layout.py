#!/usr/bin/env python3
"""Render a single product image from a JSON layer manifest using Pillow.

Usage: python scripts/render_layout.py examples/layout-example.json outputs/demo.png
Layer types: image, text, rect, line, ellipse. Image layers support contain/cover/stretch.
This renderer does not generate or cut out product photos; supply authentic transparent PNG layers.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def color(v):
    if isinstance(v, list): return tuple(v)
    return v

def load_font(path, size):
    p = Path(path) if path else None
    if not p or not p.is_file():
        raise FileNotFoundError(f"Font file missing: {path}. Provide a real CJK font; do not render tofu glyphs.")
    return ImageFont.truetype(str(p), size=size)

def fit_image(src, w, h, mode):
    src = src.convert("RGBA")
    if mode == "stretch":
        return src.resize((w,h), Image.Resampling.LANCZOS)
    ratio = min(w/src.width,h/src.height) if mode == "contain" else max(w/src.width,h/src.height)
    nw,nh=max(1,round(src.width*ratio)),max(1,round(src.height*ratio))
    src=src.resize((nw,nh),Image.Resampling.LANCZOS)
    if mode == "cover":
        x=(nw-w)//2; y=(nh-h)//2
        return src.crop((x,y,x+w,y+h))
    layer=Image.new("RGBA",(w,h),(0,0,0,0))
    layer.alpha_composite(src,((w-nw)//2,(h-nh)//2))
    return layer

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("layout",type=Path); ap.add_argument("output",type=Path)
    args=ap.parse_args()
    data=json.loads(args.layout.read_text(encoding="utf-8"))
    cw,ch=int(data["canvas"]["width"]),int(data["canvas"]["height"])
    canvas=Image.new("RGBA",(cw,ch),color(data["canvas"].get("background","#FFFFFF")))
    for i,layer in enumerate(data.get("layers",[]),1):
        t=layer["type"]; x=int(layer.get("x",0)); y=int(layer.get("y",0))
        if t=="image":
            p=Path(layer["path"])
            if not p.is_file(): raise FileNotFoundError(f"Layer {i}: {p}")
            w=int(layer["width"]); h=int(layer["height"])
            im=fit_image(Image.open(p),w,h,layer.get("fit","contain"))
            canvas.alpha_composite(im,(x,y))
        elif t in ("rect","ellipse","line"):
            d=ImageDraw.Draw(canvas)
            box=(x,y,x+int(layer.get("width",0)),y+int(layer.get("height",0)))
            fill=color(layer.get("fill","#000000"))
            if t=="rect": d.rectangle(box,fill=fill,outline=color(layer.get("outline")) if layer.get("outline") else None,width=int(layer.get("stroke_width",1)))
            elif t=="ellipse": d.ellipse(box,fill=fill,outline=color(layer.get("outline")) if layer.get("outline") else None,width=int(layer.get("stroke_width",1)))
            else: d.line((x,y,x+int(layer["x2"]),y+int(layer["y2"])),fill=fill,width=int(layer.get("stroke_width",2)))
        elif t=="text":
            d=ImageDraw.Draw(canvas)
            font=load_font(layer.get("font"),int(layer.get("font_size",48)))
            text=layer["text"]; w=int(layer.get("width",cw-x)); h=int(layer.get("height",100))
            bbox=d.multiline_textbbox((0,0),text,font=font,spacing=int(layer.get("spacing",8)),stroke_width=int(layer.get("stroke_width",0)))
            tw,th=bbox[2]-bbox[0],bbox[3]-bbox[1]
            if tw>w or th>h: raise ValueError(f"Text overflow in layer {i}: text {tw}x{th}, box {w}x{h}")
            align=layer.get("align","left"); valign=layer.get("valign","top")
            tx=x if align=="left" else (x+(w-tw)//2 if align=="center" else x+w-tw)
            ty=y if valign=="top" else (y+(h-th)//2 if valign=="middle" else y+h-th)
            d.multiline_text((tx,ty),text,font=font,fill=color(layer.get("color","#FFFFFF")),spacing=int(layer.get("spacing",8)),align=align,stroke_width=int(layer.get("stroke_width",0)),stroke_fill=color(layer.get("stroke_fill","#000000")))
        else: raise ValueError(f"Unsupported layer type: {t}")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    canvas.convert("RGB").save(args.output,format="PNG",optimize=True)
    print(f"Rendered {args.output} ({cw}x{ch})")

if __name__=="__main__":
    try: main()
    except Exception as exc:
        print(f"ERROR: {exc}",file=sys.stderr); raise SystemExit(1)
