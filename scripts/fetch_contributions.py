#!/usr/bin/env python3
"""Fetch the public contribution calendar for a GitHub user (no token needed)
and write data/contributions.json with raw days plus derived stats."""

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = sys.argv[1] if len(sys.argv) > 1 else "sanjayxrdev"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"

HEADERS = {"User-Agent": "profile-art/1.0 (+https://github.com/sanjayxrdev)"}

TOOLTIP_RE = re.compile(r"(\d+)\s+contributions?\s+on", re.IGNORECASE)


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")

    counts = {}
    for tip in soup.find_all("tool-tip"):
        m = TOOLTIP_RE.search(tip.get_text(" ", strip=True))
        if m:
            counts[tip.get("for", "")] = int(m.group(1))

    days = []
    for td in soup.find_all("td", class_="ContributionCalendar-day"):
        d = td.get("data-date")
        if not d:
            continue
        level = int(td.get("data-level", "0") or 0)
        count = counts.get(td.get("id", ""))
        if count is None:
            count = 0 if level == 0 else level * 2  # sane fallback
        days.append({"date": d, "count": count, "level": level})
    return days


def derive_stats(days):
    total = sum(d["count"] for d in days)

    best = max(days, key=lambda d: (d["count"], d["date"]), default=None)

    by_date = {d["date"]: d["count"] for d in days}

    def active(d: date) -> bool:
        return by_date.get(d.isoformat(), 0) > 0

    today = date.today()
    cur = today
    if not active(cur):
        cur -= timedelta(days=1)  # streak survives until yesterday is also empty
    current_streak = 0
    while active(cur):
        current_streak += 1
        cur -= timedelta(days=1)

    longest = run = 0
    prev = None
    for d in sorted(d["date"] for d in days if d["count"] > 0):
        dt = date.fromisoformat(d)
        run = run + 1 if prev is not None and (dt - prev).days == 1 else 1
        longest = max(longest, run)
        prev = dt

    monthly = {}
    for d in days:
        key = d["date"][:7]
        monthly[key] = monthly.get(key, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest,
        "best_day": best,
        "monthly_totals": monthly,
    }


def main():
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    days = parse_days(resp.text)
    if len(days) < 300:
        raise SystemExit(f"only parsed {len(days)} day cells — GitHub markup changed?")

    payload = {
        "username": USERNAME,
        "fetched_at": resp.headers.get("date"),
        "days": days,
        "stats": derive_stats(days),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1))
    s = payload["stats"]
    print(f"{len(days)} days -> {OUT}")
    print(f"total={s['total']} current_streak={s['current_streak']} "
          f"longest_streak={s['longest_streak']} best_day={s['best_day']['date']} ({s['best_day']['count']})")


if __name__ == "__main__":
    main()
