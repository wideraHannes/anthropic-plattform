"""Acceptance tests A1–A7 and edge cases E1–E8 from handson.md (Step 3).

Default fixture: clinic open (Mon 2026-10-26, 10:00 Berlin), minutes_per_patient = 5.
"""

import json
import re
import shutil
import time
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

import db
from app import create_app
from calibrate import accuracy, suggest
from estimate import NO_ESTIMATE, Update

BERLIN = ZoneInfo("Europe/Berlin")
CODE = Path(__file__).parents[1]
TOKEN = "test-token"
MONDAY_10 = datetime(2026, 10, 26, 10, 0, tzinfo=BERLIN)


class Clock:
    def __init__(self, now: datetime):
        self.now = now

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture
def env(tmp_path):
    config = json.loads((CODE / "config.json").read_text(encoding="utf-8"))
    config["staff_token"] = TOKEN
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    clock = Clock(MONDAY_10)
    client = TestClient(create_app(config_path, tmp_path / "wait.db", clock))
    return client, clock, tmp_path


def seed(env, patients: int, minutes_ago: float = 2) -> None:
    _, clock, tmp = env
    db.add_update(tmp / "wait.db", clock.now - timedelta(minutes=minutes_ago), patients)


def wait_text(html: str) -> str:
    match = re.search(r'<h1 id="wait"[^>]*>(.*?)</h1>', html, re.S)
    assert match, "wait element missing"
    return match.group(1).strip()


# --- acceptance tests -------------------------------------------------------


def test_a1_small_and_self_contained(env):
    seed(env, 6)
    response = env[0].get("/")
    assert len(response.content) <= 30_000
    assert not re.search(r'(?:src|href)\s*=\s*["\']?(?:https?:)?//', response.text), "no external requests"
    assert response.headers["cache-control"] == "public, max-age=30"


def test_a2_no_account(env):
    seed(env, 6)
    response = env[0].get("/")
    assert response.status_code == 200
    assert "<form" not in response.text
    assert not re.search(r"login|anmelden|passwort", response.text, re.I)


def test_a3_range(env):
    seed(env, 6)
    assert wait_text(env[0].get("/").text) == "30–45 min"


class _FirstChildOfMain(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_main = False
        self.first: dict | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.in_main = True
        elif self.in_main and self.first is None:
            self.first = {"tag": tag, **dict(attrs)}


def test_a4_wait_first_and_large(env):
    seed(env, 6)
    html = env[0].get("/").text
    parser = _FirstChildOfMain()
    parser.feed(html)
    assert parser.first and parser.first.get("id") == "wait"
    size = re.search(r"#wait\{[^}]*font-size:([\d.]+)(rem|px)", html)
    px = float(size.group(1)) * (16 if size.group(2) == "rem" else 1)
    assert px >= 24
    assert '<html lang="de">' in html


def test_a5_freshness(env):
    seed(env, 6, minutes_ago=14)
    html = env[0].get("/").text
    assert wait_text(html) == "30–45 min"
    assert "aktualisiert vor 14 min" in html

    env[1].now += timedelta(minutes=2)  # now 16 min old
    html = env[0].get("/").text
    assert wait_text(html) == NO_ESTIMATE
    assert not re.search(r"\d+\s*min", html)


@pytest.mark.parametrize(("action", "expected"), [("plus", 4), ("minus", 2), ("same", 3)])
def test_a6_one_tap(env, action, expected):
    client, clock, tmp = env
    seed(env, 3, minutes_ago=10)
    rows_before = len(db.all_updates(tmp / "wait.db"))

    start = time.perf_counter()
    response = client.post(f"/staff/{TOKEN}/update", data={"action": action}, follow_redirects=False)
    elapsed = time.perf_counter() - start

    assert response.status_code == 303
    assert elapsed < 0.5
    rows = db.all_updates(tmp / "wait.db")
    assert len(rows) == rows_before + 1 and rows[-1].patients == expected
    assert "gerade aktualisiert" in client.get("/").text


def test_a7_accuracy_check():
    t0 = MONDAY_10
    updates = [Update(t0, 6)]  # shows 30–45 min
    waits = [(t0 + timedelta(minutes=m), w) for m, w in [(1, 30), (2, 40), (3, 45), (4, 35), (5, 60)]]
    assert accuracy(updates, waits, 5) == pytest.approx(0.8)
    # arrivals with no fresh estimate on screen are not counted
    assert accuracy(updates, [(t0 + timedelta(minutes=20), 30)], 5) is None


# --- edge cases ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("now", "expected"),
    [
        (datetime(2026, 10, 26, 19, 0, tzinfo=BERLIN), "öffnet wieder morgen 08:00"),  # Mon evening
        (datetime(2026, 10, 26, 12, 30, tzinfo=BERLIN), "öffnet wieder heute 14:00"),  # lunch break
        (datetime(2026, 10, 30, 13, 0, tzinfo=BERLIN), "öffnet wieder Montag 08:00"),  # Fri afternoon
    ],
)
def test_e1_closed(env, now, expected):
    env[1].now = now
    seed(env, 6, minutes_ago=1)  # fresh data must not leak through
    html = env[0].get("/").text
    assert wait_text(html) == "Geschlossen"
    assert expected in html
    assert "30–45" not in html


def test_e2_holiday(env):
    env[1].now = datetime(2026, 12, 24, 10, 0, tzinfo=BERLIN)  # Thu, 24 + 25 are holidays
    seed(env, 6, minutes_ago=1)
    html = env[0].get("/").text
    assert wait_text(html) == "Geschlossen"
    assert "öffnet wieder Montag 08:00" in html


def test_e3_no_data(env):
    response = env[0].get("/")
    assert response.status_code == 200
    assert wait_text(response.text) == NO_ESTIMATE


def test_e4_zero_wait(env):
    seed(env, 0)
    html = env[0].get("/").text
    assert wait_text(html) == "kaum Wartezeit"
    assert "0–15" not in html


def test_e5_missing_db(env):
    client, _, tmp = env
    seed(env, 6)
    (tmp / "wait.db").unlink()
    response = client.get("/")
    assert response.status_code == 200
    assert wait_text(response.text) == NO_ESTIMATE


def test_e5_invalid_config(env):
    client, _, tmp = env
    seed(env, 6)
    (tmp / "config.json").write_text("{ not json", encoding="utf-8")
    response = client.get("/")
    assert response.status_code == 200
    assert wait_text(response.text) == NO_ESTIMATE


def test_e6_count_never_negative(env):
    client, _, tmp = env
    seed(env, 0)
    response = client.post(f"/staff/{TOKEN}/update", data={"action": "minus"}, follow_redirects=False)
    assert response.status_code == 303
    assert db.all_updates(tmp / "wait.db")[-1].patients == 0


def test_e7_wrong_token(env):
    client, _, tmp = env
    assert client.post("/staff/wrong/update", data={"action": "plus"}).status_code == 404
    assert client.get("/staff/wrong").status_code == 404
    assert db.all_updates(tmp / "wait.db") == []


@pytest.mark.parametrize(("patients", "expected"), [(23, "115–130 min"), (24, "über 2 Std."), (30, "über 2 Std.")])
def test_e8_long_wait(env, patients, expected):
    seed(env, patients)
    assert wait_text(env[0].get("/").text) == expected


# --- staff page & calibration (spec, not in the test table) -----------------


def test_staff_reminder_after_12_min(env):
    client, clock, _ = env
    seed(env, 3, minutes_ago=12)
    assert "Bitte aktualisieren" not in client.get(f"/staff/{TOKEN}").text
    clock.now += timedelta(minutes=1)
    assert "Bitte aktualisieren" in client.get(f"/staff/{TOKEN}").text


def test_staff_hourly_feedback(env):
    client, clock, tmp = env
    clock.now = datetime(2026, 10, 26, 8, 30, tzinfo=BERLIN)  # opened 30 min ago: too early to ask
    assert "letzten Stunde" not in client.get(f"/staff/{TOKEN}").text
    clock.now = MONDAY_10
    assert "letzten Stunde" in client.get(f"/staff/{TOKEN}").text
    client.post(f"/staff/{TOKEN}/feedback", data={"verdict": "zu kurz"})
    assert db.all_feedback(tmp / "wait.db")[-1][1] == "zu kurz"
    assert "letzten Stunde" not in client.get(f"/staff/{TOKEN}").text
    assert client.post(f"/staff/{TOKEN}/feedback", data={"verdict": "egal"}).status_code == 422


def test_calibrate_suggestion():
    assert suggest([], 5) == 5
    assert suggest(["zu kurz"] * 3 + ["passt"], 5) == 6
    assert suggest(["zu lang"] * 3 + ["passt"], 5) == 4
    assert suggest(["zu kurz", "zu lang", "passt"], 5) == 5


# --- UX feedback (3_discernment/ux_feedback.md) -------------------------------


def test_ux_saved_notice_after_tap(env):
    client, _, _ = env
    response = client.post(f"/staff/{TOKEN}/update", data={"action": "same"})
    assert "✓ Gespeichert" in response.text
    assert "Letzte Eingabe gerade eben" in response.text
    assert "vor 0 min" not in response.text
    assert "✓ Gespeichert" not in client.get(f"/staff/{TOKEN}").text  # notice only right after the tap


def test_ux_feedback_thanks_and_clear_labels(env):
    client, _, _ = env
    html = client.get(f"/staff/{TOKEN}").text
    assert '<button name="verdict" value="zu kurz">Länger gewartet</button>' in html
    response = client.post(f"/staff/{TOKEN}/feedback", data={"verdict": "zu kurz"})
    assert "Danke, Rückmeldung gespeichert" in response.text


def test_ux_minus_disabled_at_zero(env):
    client, _, _ = env
    seed(env, 0)
    assert re.search(r'value="minus"[^>]*disabled', client.get(f"/staff/{TOKEN}").text)
    seed(env, 2, minutes_ago=1)
    assert not re.search(r'value="minus"[^>]*disabled', client.get(f"/staff/{TOKEN}").text)


def test_ux_staff_errors_are_html(env):
    client, _, tmp = env
    response = client.get("/staff/wrong")
    assert response.status_code == 404 and response.headers["content-type"].startswith("text/html")
    assert "Praxisleitung" in response.text and "Zurück" not in response.text

    response = client.post(f"/staff/{TOKEN}/update", data={"action": "egal"})
    assert response.status_code == 422 and f'href="/staff/{TOKEN}"' in response.text

    (tmp / "config.json").write_text("{ not json", encoding="utf-8")
    response = client.get(f"/staff/{TOKEN}")
    assert response.status_code == 503 and "Praxis-IT" in response.text


def test_ux_storage_error_on_tap_is_503_not_500(env):
    client, _, tmp = env
    (tmp / "wait.db").unlink()
    (tmp / "wait.db").mkdir()  # sqlite cannot open a directory
    response = client.post(f"/staff/{TOKEN}/update", data={"action": "plus"})
    assert response.status_code == 503
    assert "nicht gespeichert" in response.text


def test_ux_public_refresh_can_be_switched_off(env):
    client, _, _ = env
    seed(env, 6)
    assert 'http-equiv="refresh"' in client.get("/").text
    html = client.get("/?auto=0").text
    assert 'http-equiv="refresh"' not in html and "Automatische Aktualisierung ist aus" in html
