#!/usr/bin/env python3
"""Convert source-prepped.png into a self-typing monochrome ASCII SVG.

The image is downsampled to a character grid; each cell's brightness picks
a glyph from a density ramp. Each row is wrapped in a horizontal clip that
wipes left-to-right (a small cursor block rides the wipe edge), staggered
top to bottom. The portrait prints once and freezes — no looping.
Because it's SMIL inside the SVG, GitHub plays it in <img> contexts.

Usage: python scripts/make_ascii_svg.py  [input] [-o out.svg]
Expects scripts/../source-prepped.png by default."""

import argparse
import sys
from pathlib import Path

import numpy as np

RAMP = " .`:-=+*cs#%@"          # bright (sparse) -> dark (dense)
GRID_W = 100                     # character columns
ASPECT = 0.55                    # char cells are ~2x taller than wide
FONT_SIZE = 13.0
ADV = FONT_SIZE * 0.60           # monospace advance
ROW_H = FONT_SIZE * 1.05
FILL = "#b6c2cf"                 # one light-gray fill — monochrome stays clean
BG = "#0d1117"
PAD = 14.0

ROOT = Path(__file__).resolve().parent.parent


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ascii_rows(path: Path):
    from PIL import Image

    img = Image.open(path).convert("L")
    grid_h = max(1, round(GRID_W * img.height / img.width * ASPECT))
    small = np.asarray(
        img.resize((GRID_W, grid_h), Image.LANCZOS), dtype=np.float32) / 255.0

    rows = []
    for r in small:
        idx = np.round((1.0 - r) * (len(RAMP) - 1)).astype(int)
        rows.append("".join(RAMP[i] for i in idx))
    return rows


def render(rows, out: Path) -> None:
    n = len(rows)
    width = GRID_W * ADV + PAD * 2
    height = n * ROW_H + PAD * 2

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" '
         f'height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" role="img">',
         f'<rect width="{width:.0f}" height="{height:.0f}" fill="{BG}"/>']

    start = 0.2
    stagger = 0.028
    wipe_dur = 0.05
    total = start + n * stagger + wipe_dur

    for i, text in enumerate(rows):
        y = PAD + i * ROW_H + FONT_SIZE
        begin = f"{start + i * stagger:.3f}s"
        p.append(f'<clipPath id="rc{i}"><rect x="{PAD}" y="{PAD + i * ROW_H:.2f}" '
                 f'width="0" height="{ROW_H + 1:.2f}">'
                 f'<animate attributeName="width" from="0" to="{width:.0f}" '
                 f'begin="{begin}" dur="{wipe_dur}s" fill="freeze"/></rect></clipPath>')
        p.append(f'<g clip-path="url(#rc{i})"><text x="{PAD}" y="{y:.2f}" '
                 f'font-family="Menlo,Consolas,\'DejaVu Sans Mono\',monospace" '
                 f'font-size="{FONT_SIZE}" fill="{FILL}" '
                 f'xml:space="preserve">{esc(text)}</text></g>')

    # cursor block rides the last wipe edge, then hides
    end = f"{total:.3f}s"
    p.append(f'<rect x="{PAD}" y="{PAD}" width="9" height="{ROW_H:.2f}" fill="{FILL}" '
             f'opacity="1">'
             f'<animate attributeName="x" from="{PAD}" to="{width - PAD - 9:.0f}" '
             f'begin="{start:.3f}s" dur="{total - start:.3f}s" fill="freeze"/>'
             f'<animate attributeName="opacity" from="1" to="0" begin="{end}" '
             f'dur="0.01s" fill="freeze"/></rect>')

    p.append("</svg>")
    out.write_text("\n".join(p))
    print(f"wrote {out} ({GRID_W}x{n} chars, prints over {total:.2f}s)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", nargs="?", default=str(ROOT / "source-prepped.png"))
    ap.add_argument("-o", "--out", default=str(ROOT / "ascii-portrait.svg"))
    args = ap.parse_args()

    src = Path(args.input)
    if not src.exists():
        sys.exit(f"{src} not found — run scripts/prep_photo.py on your photo first")
    rows = ascii_rows(src)
    if not any(line.strip() for line in rows):
        sys.exit("converted image is blank — photo may be too flat; check prep output")
    render(rows, Path(args.out))


if __name__ == "__main__":
    main()
