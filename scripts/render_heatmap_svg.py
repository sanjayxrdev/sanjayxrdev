#!/usr/bin/env python3
"""Render data/contributions.json as an animated contribution heatmap SVG.

The grid reveals once with a diagonal, column-after-column slide-down
(CSS keyframes that play on load, then freeze — no looping)."""

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG = "#010409"
FG_MUTED = "#8b949e"
FG_BRIGHT = "#e6edf3"

CELL, GAP = 12.0, 3.0
STEP = CELL + GAP
LEFT, TOP = 38.0, 26.0          # room for weekday / month labels
WEEKS = 53

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}


def build_weeks(days):
    """Group days into GitHub-style columns (weeks) starting on Sunday."""
    first = date.fromisoformat(days[0]["date"])
    pad_left = (first.weekday() + 1) % 7  # days until Sunday-start column fills
    cols = []
    col = [None] * pad_left
    for d in days:
        col.append(d)
        if len(col) == 7:
            cols.append(col)
            col = []
    if col:
        col += [None] * (7 - len(col))
        cols.append(col)
    return cols[-WEEKS:]


def month_labels(cols):
    labels = []
    prev = None
    for i, col in enumerate(cols):
        d = next((x["date"] for x in col if x), None)
        if not d:
            continue
        m = int(d[5:7])
        if m != prev and (not labels or i - labels[-1][0] >= 3):
            labels.append((i, MONTHS[m - 1]))
        prev = m
    return labels


def render():
    payload = json.loads(DATA.read_text())
    days = payload["days"]
    stats = payload["stats"]
    cols = build_weeks(days)

    n_cols = len(cols)
    grid_w = n_cols * STEP - GAP
    grid_h = 7 * STEP - GAP
    width = LEFT + grid_w + 20
    footer_y = TOP + grid_h + 34
    height = footer_y + 14

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" '
        f'height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" role="img">',
        "<style>",
        f".col{{opacity:0;animation:drop .4s cubic-bezier(.2,.7,.3,1) forwards}}",
        *[f".c{i}{{animation-delay:{0.05 + i * 0.013:.3f}s}}" for i in range(n_cols)],
        ".meta{opacity:0;animation:fade .6s ease-out forwards;"
        f"animation-delay:{0.05 + n_cols * 0.013 + 0.15:.3f}s}}",
        "@keyframes drop{from{opacity:0;transform:translateY(-14px)}to{opacity:1;transform:none}}",
        "@keyframes fade{to{opacity:1}}",
        "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}",
        "</style>",
        f'<rect width="{width:.0f}" height="{height:.0f}" fill="{BG}"/>',
    ]

    # weekday labels
    for row, label in WEEKDAY_LABELS.items():
        y = TOP + row * STEP + CELL - 2.5
        parts.append(
            f'<text x="{LEFT - 8}" y="{y:.1f}" font-size="10" fill="{FG_MUTED}" '
            f'text-anchor="end">{label}</text>')

    # month labels
    for i, name in month_labels(cols):
        x = LEFT + i * STEP
        parts.append(
            f'<text x="{x:.1f}" y="{TOP - 9}" font-size="10" fill="{FG_MUTED}">{name}</text>')

    # day cells, one animated group per week-column -> diagonal reveal
    for ci, col in enumerate(cols):
        parts.append(f'<g class="col c{ci}">')
        for ri, d in enumerate(col):
            if d is None:
                continue
            color = PALETTE[min(d["level"], len(PALETTE) - 1)]
            x = LEFT + ci * STEP
            y = TOP + ri * STEP
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" '
                f'rx="2.5" fill="{color}"/>')
        parts.append("</g>")

    # footer stats + legend
    total = f"{stats['total']:,}"
    best = stats.get("best_day") or {}
    meta_tail = (f" contributions in the last year"
                 f" · longest streak {stats['longest_streak']}d"
                 f" · current streak {stats['current_streak']}d"
                 f" · best day {best.get('count', 0)}")
    parts.append(
        f'<g class="meta"><text x="{LEFT}" y="{footer_y}" font-size="12">'
        f'<tspan fill="{FG_BRIGHT}" font-weight="bold">{total}</tspan>'
        f'<tspan fill="{FG_MUTED}">{meta_tail}</tspan></text>')

    # right-aligned legend:  Less [sq sq sq sq sq] More
    more_end = width - 16
    last_sq_x = more_end - 30 - GAP
    first_sq_x = last_sq_x - (len(PALETTE) - 2) * (9 + 4)
    for li, color in enumerate(PALETTE[1:]):
        lx = first_sq_x + li * (9 + 4)
        parts.append(f'<rect x="{lx:.1f}" y="{footer_y - 8.5}" width="9" height="9" '
                     f'rx="2" fill="{color}"/>')
    parts.append(f'<text x="{first_sq_x - 6:.1f}" y="{footer_y}" font-size="10" '
                 f'fill="{FG_MUTED}" text-anchor="end">Less</text>')
    parts.append(f'<text x="{more_end}" y="{footer_y}" font-size="10" '
                 f'fill="{FG_MUTED}">More</text></g>')

    parts.append("</svg>")
    OUT.write_text("\n".join(parts))
    print(f"wrote {OUT} ({width:.0f}x{height:.0f}, {n_cols} week columns)")


if __name__ == "__main__":
    render()
