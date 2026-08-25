#!/usr/bin/env python3
"""Prep a photo for ASCII conversion.

A flatly-lit face converts to a dark, unreadable blob, so:
  1. remove the background with rembg (subject isolated)
  2. boost local contrast with CLAHE (real highlights and shadows)
  3. composite onto pure white so the background maps to the blank
     end of the density ramp

Usage: python scripts/prep_photo.py [input] [-o out.png]
Output: grayscale source-prepped.png next to the input.
Default input: pfp.jpeg in the repo root."""

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("photo", nargs="?", default=str(ROOT / "pfp.jpeg"), help="input photo (jpg/png)")
    ap.add_argument("-o", "--out", default=None, help="output png path")
    args = ap.parse_args()

    src = Path(args.photo)
    if not src.exists():
        sys.exit(f"not found: {src}")

    from PIL import Image
    from rembg import remove, new_session

    print("[1/3] removing background (rembg)...")
    raw = Image.open(src).convert("RGBA")
    session = new_session("u2net")
    cut = remove(raw, session=session)

    # crop to the subject with a small margin
    alpha = np.asarray(cut)[:, :, 3]
    ys, xs = np.where(alpha > 8)
    if len(xs) == 0:
        sys.exit("background removal produced an empty subject — try another photo")
    m = int(0.06 * max(xs.max() - xs.min(), ys.max() - ys.min()))
    box = (max(xs.min() - m, 0), max(ys.min() - m, 0),
           min(xs.max() + m, cut.width), min(ys.max() + m, cut.height))
    cut = cut.crop(box)

    print("[2/3] compositing onto white...")
    white = Image.new("RGB", cut.size, (255, 255, 255))
    white.paste(cut, mask=cut.split()[3])

    print("[3/3] boosting local contrast (CLAHE)...")
    import cv2
    gray = cv2.cvtColor(np.asarray(white), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    out_img = Image.fromarray(clahe.apply(gray))

    out = Path(args.out) if args.out else src.with_name("source-prepped.png")
    out_img.save(out)
    print(f"wrote {out} ({out_img.size[0]}x{out_img.size[1]} grayscale)")


if __name__ == "__main__":
    main()
