"""Pure wait-time logic: config, opening hours, freshness and the displayed estimate.

No I/O apart from reading the config file, so every rule in the spec is unit-testable.
"""

import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

STALE_AFTER = timedelta(minutes=15)  # requirement: never older than 15 min
RANGE_WIDTH = 15  # displayed range is [wait, wait + 15]
LONG_WAIT = 120  # at or above this, show "über 2 Std." instead of a range
NO_ESTIMATE = "Aktuell keine Schätzung verfügbar"

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
WEEKDAYS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
REQUIRED_KEYS = ("timezone", "minutes_per_patient", "staff_token", "quiet_hint", "opening_hours", "holidays")


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Update:
    ts: datetime  # timezone-aware
    patients: int


@dataclass(frozen=True)
class View:
    state: str  # "fresh" | "stale" | "closed"
    headline: str
    detail: str | None = None


def load_config(path: Path) -> dict:
    """Read and validate config.json; any problem becomes a ConfigError."""
    try:
        config = json.loads(Path(path).read_text(encoding="utf-8"))
        missing = [k for k in REQUIRED_KEYS if k not in config]
        if missing:
            raise ConfigError(f"missing keys: {missing}")
        ZoneInfo(config["timezone"])
        if not config["minutes_per_patient"] > 0:
            raise ConfigError("minutes_per_patient must be > 0")
        for day, intervals in config["opening_hours"].items():
            if day not in WEEKDAYS:
                raise ConfigError(f"unknown weekday: {day}")
            for start, end in intervals:
                if time.fromisoformat(start) >= time.fromisoformat(end):
                    raise ConfigError(f"empty interval on {day}: {start}-{end}")
        for holiday in config["holidays"]:
            date.fromisoformat(holiday)
    except ConfigError:
        raise
    except Exception as e:  # missing file, bad JSON, bad types, bad times
        raise ConfigError(str(e)) from e
    return config


# --- estimate ---------------------------------------------------------------


def displayed_range(patients: int, minutes_per_patient: float) -> tuple[int, int | None]:
    """(low, high) in minutes; high is None for the open-ended long-wait case."""
    if patients <= 0:
        return 0, RANGE_WIDTH
    wait = int(patients * minutes_per_patient / 5 + 0.5) * 5  # rounded to the nearest 5 min
    if wait >= LONG_WAIT:
        return LONG_WAIT, None
    return wait, wait + RANGE_WIDTH


def format_wait(patients: int, minutes_per_patient: float) -> str:
    if patients <= 0:
        return "kaum Wartezeit"
    low, high = displayed_range(patients, minutes_per_patient)
    if high is None:
        return "über 2 Std."
    return f"{low}–{high} min"


# --- opening hours ----------------------------------------------------------


def opening_intervals(config: dict, day: date) -> list[tuple[datetime, datetime]]:
    if day.isoformat() in config["holidays"]:
        return []
    tz = ZoneInfo(config["timezone"])
    return [
        (datetime.combine(day, time.fromisoformat(a), tz), datetime.combine(day, time.fromisoformat(b), tz))
        for a, b in config["opening_hours"].get(WEEKDAYS[day.weekday()], [])
    ]


def current_interval(config: dict, now: datetime) -> tuple[datetime, datetime] | None:
    now = now.astimezone(ZoneInfo(config["timezone"]))
    for start, end in opening_intervals(config, now.date()):
        if start <= now < end:
            return start, end
    return None


def next_opening(config: dict, now: datetime) -> datetime | None:
    now = now.astimezone(ZoneInfo(config["timezone"]))
    for offset in range(15):
        for start, _ in opening_intervals(config, now.date() + timedelta(days=offset)):
            if start > now:
                return start
    return None


def format_opening(opening: datetime, now: datetime) -> str:
    days = (opening.date() - now.astimezone(opening.tzinfo).date()).days
    clock = opening.strftime("%H:%M")
    if days == 0:
        return f"heute {clock}"
    if days == 1:
        return f"morgen {clock}"
    if days < 7:
        return f"{WEEKDAYS_DE[opening.weekday()]} {clock}"
    return f"{WEEKDAYS_DE[opening.weekday()]}, {opening:%d.%m.} {clock}"


# --- public view ------------------------------------------------------------


def minutes_since(ts: datetime, now: datetime) -> int:
    return max(0, int((now - ts).total_seconds() // 60))


def build_view(config: dict, update: Update | None, now: datetime) -> View:
    """Decide which of the three states the public page shows."""
    if current_interval(config, now) is None:
        opening = next_opening(config, now)
        return View("closed", "Geschlossen", f"öffnet wieder {format_opening(opening, now)}" if opening else None)
    if update is None or now - update.ts > STALE_AFTER:
        return View("stale", NO_ESTIMATE, "Die Rezeption hat die Zahl gerade nicht aktualisiert. Bitte in ein paar Minuten noch einmal nachsehen.")
    age = minutes_since(update.ts, now)
    updated = f"aktualisiert vor {age} min" if age else "gerade aktualisiert"
    return View("fresh", format_wait(update.patients, config["minutes_per_patient"]), f"geschätzte Wartezeit · {updated}")
