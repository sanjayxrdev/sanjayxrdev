#!/usr/bin/env python3
"""Hand-authored neofetch-style info card SVG.

Each line fades and slides in on a short stagger so the panel prints
itself next to the portrait. STATIC=1 emits a frozen frame."""

import os
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"

STATIC = os.environ.get("STATIC") == "1"

W, H = 490, 252
BG, BORDER = "#0d1117", "#21262d"
FG_NAME, FG_KEY, FG_VAL, FG_MUTED = "#e6edf3", "#39d353", "#c9d1d9", "#8b949e"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

NAME = "sanjayxrdev @ github"
ROWS = [
    ("Now",   "Building local-first tools & med-tech UIs"),
    ("Prev",  "FILE CONV · CT seg experiments · HH Goa '26"),
    ("Stack", "Python · FastAPI · TS · React · Three.js"),
    ("Focus", "ML × Web · shipping fast, breaking nothing"),
]


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

BAR_H = 38.0
PAD_X = 24.0
NAME_Y = BAR_H + 34.0
LINE_H = 27.0
KEY_X, VAL_X = PAD_X, 100.0


def row_anim(idx: int) -> str:
    if STATIC:
        return ""
    delay = 0.15 + idx * 0.09
    return f' class="row" style="animation-delay:{delay:.2f}s"'


def render() -> None:
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" aria-label="neofetch-style info card">']

    if not STATIC:
        p += ["<style>",
              "@keyframes rise{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}",
              ".row{opacity:0;animation:rise .38s ease-out forwards}",
              "@keyframes blink{0%,55%{opacity:1}56%,100%{opacity:0}}",
              ".cursor{animation:blink 1.1s steps(1) infinite}",
              f"text{{font-family:{FONT}}}",
              "</style>"]
    else:
        p += [f"<style>text{{font-family:{FONT}}}</style>"]

    # window frame + title bar
    p.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" '
             f'fill="{BG}" stroke="{BORDER}" stroke-width="2"/>')
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        p.append(f'<circle cx="{22 + i * 18}" cy="19" r="5" fill="{c}"/>')
    p.append(f'<text x="{W / 2}" y="23" font-size="11" fill="{FG_MUTED}" '
             f'text-anchor="middle">sanjayxrdev@github: ~</text>')
    p.append(f'<line x1="1.5" y1="{BAR_H}" x2="{W - 1.5}" y2="{BAR_H}" '
             f'stroke="{BORDER}" stroke-width="1"/>')

    # name header + separator
    p.append(f'<text{row_anim(0)} x="{PAD_X}" y="{NAME_Y}" font-size="16" '
             f'font-weight="bold" fill="{FG_NAME}">{esc(NAME)}</text>')
    sep_y = NAME_Y + 12
    p.append(f'<rect x="{PAD_X}" y="{sep_y}" width="{W - PAD_X * 2}" height="1" fill="{BORDER}"/>')

    # key/value rows
    y = sep_y + LINE_H
    for i, (key, val) in enumerate(ROWS):
        cls = row_anim(i + 1)
        if STATIC:
            p.append(f'<text x="{KEY_X}" y="{y:.1f}" font-size="13"><tspan '
                     f'fill="{FG_KEY}" font-weight="bold">{esc(key)}</tspan></text>')
            p.append(f'<text x="{VAL_X}" y="{y:.1f}" font-size="13" fill="{FG_VAL}">{esc(val)}</text>')
        else:
            p.append(f'<text{cls} x="{KEY_X}" y="{y:.1f}" font-size="13">'
                     f'<tspan fill="{FG_KEY}" font-weight="bold">{esc(key)}</tspan></text>')
            p.append(f'<text{cls} x="{VAL_X}" y="{y:.1f}" font-size="13" fill="{FG_VAL}">{esc(val)}</text>')
        y += LINE_H

    # trailing prompt with blinking cursor
    prompt_y = min(y + 4, H - 14)
    cursor_cls = "" if STATIC else ' class="cursor"'
    p.append(f'<text x="{KEY_X}" y="{prompt_y:.1f}" font-size="13" fill="{FG_MUTED}">'
             f'sanjayxrdev@github:~$</text>')
    p.append(f'<rect{cursor_cls} x="{KEY_X + 172}" y="{prompt_y - 11:.1f}" width="8" height="14" '
             f'fill="{FG_KEY}"/>')

    p.append("</svg>")
    OUT.write_text("\n".join(p))
    print(f"wrote {OUT}{' (static)' if STATIC else ''}")


if __name__ == "__main__":
    render()
