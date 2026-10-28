"""SQLite storage: two append-only event tables. One connection per call keeps it simple."""

import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from estimate import Update

VERDICTS = ("zu kurz", "passt", "zu lang")
# Stored values stay stable (DB check, calibrate.py); the staff page shows these unambiguous labels.
VERDICT_LABELS = {"zu kurz": "Länger gewartet", "passt": "Passt", "zu lang": "Kürzer gewartet"}

SCHEMA = """
create table if not exists updates (
    ts text not null,
    patients integer not null check (patients >= 0)
);
create table if not exists feedback (
    ts text not null,
    verdict text not null check (verdict in ('zu kurz', 'passt', 'zu lang'))
);
"""


def init(path: Path) -> None:
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.executescript(SCHEMA)


def connect_readonly(path: Path) -> sqlite3.Connection:
    # Read-only: a missing DB file raises instead of silently creating an empty one.
    return sqlite3.connect(f"file:{Path(path).resolve()}?mode=ro", uri=True)


def latest_update(path: Path) -> Update | None:
    with closing(connect_readonly(path)) as conn:
        row = conn.execute("select ts, patients from updates order by ts desc limit 1").fetchone()
    return Update(datetime.fromisoformat(row[0]), row[1]) if row else None


def all_updates(path: Path) -> list[Update]:
    with closing(connect_readonly(path)) as conn:
        rows = conn.execute("select ts, patients from updates order by ts").fetchall()
    return [Update(datetime.fromisoformat(ts), p) for ts, p in rows]


def add_update(path: Path, ts: datetime, patients: int) -> None:
    init(path)
    with closing(sqlite3.connect(path)) as conn, conn:
        # Store UTC so text ordering stays chronological across DST changes.
        conn.execute("insert into updates values (?, ?)", (ts.astimezone(UTC).isoformat(), patients))


def latest_feedback_ts(path: Path) -> datetime | None:
    with closing(connect_readonly(path)) as conn:
        row = conn.execute("select max(ts) from feedback").fetchone()
    return datetime.fromisoformat(row[0]) if row[0] else None


def all_feedback(path: Path) -> list[tuple[datetime, str]]:
    with closing(connect_readonly(path)) as conn:
        rows = conn.execute("select ts, verdict from feedback order by ts").fetchall()
    return [(datetime.fromisoformat(ts), v) for ts, v in rows]


def add_feedback(path: Path, ts: datetime, verdict: str) -> None:
    init(path)
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute("insert into feedback values (?, ?)", (ts.astimezone(UTC).isoformat(), verdict))
