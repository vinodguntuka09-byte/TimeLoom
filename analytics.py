"""
analytics.py
------------
Turns raw entries into useful reports:
  - category-wise summary
  - daily summary
  - a simple text/ASCII bar chart
  - a 7-day activity heatmap (console-based, since this is a console app)
"""

from datetime import datetime, timedelta
from collections import defaultdict


def category_summary(data):
    totals = defaultdict(float)
    for e in data["entries"]:
        totals[e["category"]] += e["duration_minutes"]

    if not totals:
        print("No data to summarize yet.")
        return

    print("\n--- Time by Category ---")
    max_minutes = max(totals.values())
    for category, minutes in sorted(totals.items(), key=lambda x: -x[1]):
        bar_len = int((minutes / max_minutes) * 30) if max_minutes else 0
        bar = "#" * bar_len
        hours = minutes / 60
        print(f"{category:<12} | {bar:<30} {minutes:.1f} min ({hours:.1f} h)")


def daily_summary(data):
    totals = defaultdict(float)
    for e in data["entries"]:
        totals[e["date"]] += e["duration_minutes"]

    if not totals:
        print("No data to summarize yet.")
        return

    print("\n--- Time by Day ---")
    for date_str in sorted(totals.keys()):
        minutes = totals[date_str]
        hours = minutes / 60
        print(f"{date_str}: {minutes:.1f} min ({hours:.1f} h)")


def weekly_heatmap(data):
    """Shows the last 7 days as a row of blocks whose density represents
    how many minutes were logged that day. Pure ASCII, no GUI needed."""
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    totals = defaultdict(float)
    for e in data["entries"]:
        totals[e["date"]] += e["duration_minutes"]

    if not any(totals.get(d.strftime("%Y-%m-%d"), 0) for d in days):
        print("No activity in the last 7 days.")
        return

    blocks = " .:-=+*#%@"  # increasing "density" characters
    max_minutes = max(totals.get(d.strftime("%Y-%m-%d"), 0) for d in days) or 1

    print("\n--- Weekly Heatmap (last 7 days) ---")
    for d in days:
        key = d.strftime("%Y-%m-%d")
        minutes = totals.get(key, 0)
        level = min(int((minutes / max_minutes) * (len(blocks) - 1)), len(blocks) - 1)
        block_char = blocks[level] * 10
        print(f"{d.strftime('%a %Y-%m-%d')} | {block_char} {minutes:.0f} min")


def full_report(data):
    print("\n=========== TIMELOOM REPORT ===========")
    category_summary(data)
    daily_summary(data)
    weekly_heatmap(data)
    total_minutes = sum(e["duration_minutes"] for e in data["entries"])
    print(f"\nTotal tracked time: {total_minutes:.1f} min ({total_minutes/60:.1f} h)")
    print("========================================")
