"""Scrape the public contribution calendar for a GitHub user.

No API token needed: github.com/users/<login>/contributions is public HTML.
Writes data/contributions.json for render_heatmap_svg.py to consume.
"""

import json
import os
import re
import sys
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "schammaahmed")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")

URL = "https://github.com/users/{}/contributions".format(USERNAME)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; profile-art/1.0)",
    "Accept": "text/html",
}

# "3 contributions on July 21st." / "No contributions on July 20th."
COUNT_RE = re.compile(r"^(\d+)\s+contribution")


def fetch_html():
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse(html):
    soup = BeautifulSoup(html, "html.parser")

    # Counts live in <tool-tip for="<cell id>">, not on the cell itself.
    tooltips = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        if not target:
            continue
        m = COUNT_RE.match(tip.get_text(strip=True))
        tooltips[target] = int(m.group(1)) if m else 0

    days = []
    for cell in soup.select("td.ContributionCalendar-day"):
        day = cell.get("data-date")
        if not day:
            continue
        days.append(
            {
                "date": day,
                "level": int(cell.get("data-level", 0)),
                "count": tooltips.get(cell.get("id"), 0),
            }
        )

    if not days:
        raise SystemExit("no contribution cells found - GitHub markup may have changed")

    days.sort(key=lambda d: d["date"])
    return days


def streaks(days):
    """Current and longest run of consecutive days with >= 1 contribution.

    Today is excluded from breaking the current streak: a day that has not
    happened yet in the user's timezone would otherwise reset it to zero.
    """
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)

    today = date.today().isoformat()
    trailing = [d for d in days if d["date"] <= today]
    if trailing and trailing[-1]["date"] == today and trailing[-1]["count"] == 0:
        trailing = trailing[:-1]

    current = 0
    for d in reversed(trailing):
        if d["count"] == 0:
            break
        current += 1

    return current, longest


def main():
    days = parse(fetch_html())
    current, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])

    payload = {
        "username": USERNAME,
        "generated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": [days[0]["date"], days[-1]["date"]],
        "total": sum(d["count"] for d in days),
        "active_days": sum(1 for d in days if d["count"] > 0),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "days": days,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(payload, fh, indent=1)

    print(
        "{} days, {} contributions, streak {}/{} -> {}".format(
            len(days), payload["total"], current, longest, os.path.relpath(OUT)
        ),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
