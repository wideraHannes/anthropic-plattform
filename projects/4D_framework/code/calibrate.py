"""Calibration loop (human in the loop): summarise staff feedback, suggest minutes_per_patient,
and optionally check A7 against measured real waits.

  uv run python calibrate.py                     # feedback per weekday/hour + suggestion
  uv run python calibrate.py --actual waits.csv  # A7: share of real waits inside the shown range

waits.csv columns: arrival (ISO datetime, local clinic time if naive), actual_wait_min
"""

import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import db
from estimate import STALE_AFTER, WEEKDAYS_DE, Update, displayed_range, load_config

HERE = Path(__file__).parent
A7_TARGET = 0.8
SHIFT_THRESHOLD = 0.2  # net share of "zu kurz" vs "zu lang" before we suggest a change


def suggest(verdicts: list[str], current: float) -> float:
    """+1 min if staff mostly say "zu kurz", −1 min if mostly "zu lang", else keep."""
    if not verdicts:
        return current
    counts = Counter(verdicts)
    net = (counts["zu kurz"] - counts["zu lang"]) / len(verdicts)
    if net > SHIFT_THRESHOLD:
        return current + 1
    if net < -SHIFT_THRESHOLD:
        return max(1, current - 1)
    return current


def accuracy(updates: list[Update], waits: list[tuple[datetime, int]], minutes_per_patient: float) -> float | None:
    """Share of real waits inside the range the page showed at arrival. Arrivals without a fresh estimate are skipped."""
    hits = total = 0
    for arrival, actual in waits:
        shown = [u for u in updates if u.ts <= arrival and arrival - u.ts <= STALE_AFTER]
        if not shown:
            continue
        low, high = displayed_range(shown[-1].patients, minutes_per_patient)
        total += 1
        hits += low <= actual and (high is None or actual <= high)
    return hits / total if total else None


def read_waits(path: Path, tz: ZoneInfo) -> list[tuple[datetime, int]]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    waits = []
    for row in rows:
        arrival = datetime.fromisoformat(row["arrival"])
        waits.append((arrival if arrival.tzinfo else arrival.replace(tzinfo=tz), int(row["actual_wait_min"])))
    return waits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", type=Path, default=HERE / "wait.db")
    parser.add_argument("--config", type=Path, default=HERE / "config.json")
    parser.add_argument("--actual", type=Path, help="CSV of measured waits for the A7 check")
    args = parser.parse_args()

    config = load_config(args.config)
    tz = ZoneInfo(config["timezone"])
    current = config["minutes_per_patient"]
    feedback = db.all_feedback(args.db)

    by_slot: dict[tuple[int, int], Counter] = defaultdict(Counter)
    for ts, verdict in feedback:
        local = ts.astimezone(tz)
        by_slot[(local.weekday(), local.hour)][verdict] += 1

    print(f"Feedback ({len(feedback)} entries)")
    print(f"{'slot':<16}{'zu kurz':>9}{'passt':>7}{'zu lang':>9}")
    for (weekday, hour), counts in sorted(by_slot.items()):
        print(f"{WEEKDAYS_DE[weekday][:2]} {hour:02d}–{hour + 1:02d} Uhr  {counts['zu kurz']:>9}{counts['passt']:>7}{counts['zu lang']:>9}")

    suggestion = suggest([v for _, v in feedback], current)
    verb = "keep" if suggestion == current else "change to"
    print(f"\nminutes_per_patient: {current} → {verb} {suggestion}  (apply by hand in config.json)")

    if args.actual:
        share = accuracy(db.all_updates(args.db), read_waits(args.actual, tz), current)
        if share is None:
            print("\nA7: no arrivals with a fresh estimate shown")
        else:
            verdict = "PASS" if share >= A7_TARGET else "FAIL"
            print(f"\nA7: {share:.0%} of real waits inside the shown range (target ≥ {A7_TARGET:.0%}) → {verdict}")


if __name__ == "__main__":
    main()
