"""Clinic wait-time prototype: public page (GET /) and one-tap staff page (/staff/<token>).

Run:  uv run python app.py   →  http://127.0.0.1:8000  and  http://127.0.0.1:8000/staff/<staff_token>
"""

import secrets
import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

import db
from estimate import (
    NO_ESTIMATE,
    ConfigError,
    View,
    build_view,
    current_interval,
    format_wait,
    load_config,
    minutes_since,
)

HERE = Path(__file__).parent
STAFF_REMINDER = timedelta(
    minutes=12
)  # warn staff before the public page goes stale at 15
FEEDBACK_EVERY = timedelta(hours=1)
ACTIONS = {"plus": +1, "minus": -1, "same": 0}
SAVED = {"update": "✓ Gespeichert", "feedback": "✓ Danke, Rückmeldung gespeichert"}
STAFF_ERRORS = {
    404: "Diese Adresse ist ungültig. Bitte den aktuellen Rezeptions-Link bei der Praxisleitung erfragen.",
    422: "Diese Eingabe wurde nicht erkannt. Bitte zur Rezeptionsseite zurückkehren und noch einmal tippen.",
    503: "Die Einstellungen der Wartezeit-Anzeige sind fehlerhaft. Bitte die Praxis-IT informieren (config.json prüfen).",
}


def create_app(
    config_path: Path = HERE / "config.json",
    db_path: Path = HERE / "wait.db",
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    templates = Jinja2Templates(directory=HERE / "templates")
    db.init(db_path)

    def staff_error(request: Request, status: int, message: str):
        # Staff see a readable page with a way back instead of raw JSON; 404 gets no link (token is wrong).
        parts = request.url.path.split("/")
        back = f"/staff/{parts[2]}" if status != 404 and len(parts) > 2 else None
        response = templates.TemplateResponse(
            request, "error.html", {"message": message, "back": back}, status_code=status
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        if not request.url.path.startswith("/staff/"):
            return await http_exception_handler(request, exc)
        return staff_error(request, exc.status_code, STAFF_ERRORS.get(exc.status_code, "Unerwarteter Fehler."))

    @app.exception_handler(sqlite3.Error)
    async def storage_error(request: Request, exc: sqlite3.Error):
        # The public page catches this itself (E5); here it can only come from a staff route.
        if request.method == "POST":
            message = "Die Eingabe konnte nicht gespeichert werden. Bitte noch einmal tippen. Bleibt der Fehler, die Praxis-IT informieren."
        else:
            message = "Die Daten konnten nicht geladen werden. Bitte die Seite neu laden. Bleibt der Fehler, die Praxis-IT informieren."
        return staff_error(request, 503, message)

    @app.get("/", response_class=HTMLResponse)
    def public(request: Request, auto: str = "1"):
        try:
            config = load_config(config_path)
            view = build_view(config, db.latest_update(db_path), clock())
            hint = config["quiet_hint"]
        except ConfigError, sqlite3.Error:
            # E5: broken storage or config degrades to "no estimate", never a 500.
            view, hint = (
                View("stale", NO_ESTIMATE, "Bitte später noch einmal nachsehen."),
                None,
            )
        response = templates.TemplateResponse(
            request, "public.html", {"view": view, "hint": hint, "auto": auto != "0"}
        )
        response.headers["Cache-Control"] = "public, max-age=30"
        return response

    def staff_config(token: str) -> dict:
        try:
            config = load_config(config_path)
        except ConfigError:
            raise HTTPException(503, "Konfiguration fehlerhaft")
        if not secrets.compare_digest(
            token.encode(), str(config["staff_token"]).encode()
        ):
            raise HTTPException(404)
        return config

    @app.get("/staff/{token}", response_class=HTMLResponse)
    def staff(request: Request, token: str, ok: str | None = None):
        config = staff_config(token)
        now = clock()
        last = db.latest_update(db_path)
        last_feedback = db.latest_feedback_ts(db_path)
        interval = current_interval(config, now)
        patients = last.patients if last else 0
        context = {
            "token": token,
            "patients": patients,
            "preview": format_wait(patients, config["minutes_per_patient"]),
            "age": minutes_since(last.ts, now) if last else None,
            "saved": SAVED.get(ok),
            "is_open": interval is not None,
            "remind": interval is not None
            and (last is None or now - last.ts > STAFF_REMINDER),
            "ask_feedback": interval is not None
            and now - interval[0] >= FEEDBACK_EVERY
            and (last_feedback is None or now - last_feedback >= FEEDBACK_EVERY),
            "verdicts": db.VERDICT_LABELS,
        }
        response = templates.TemplateResponse(request, "staff.html", context)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.post("/staff/{token}/update")
    def update(token: str, action: Annotated[str, Form()]):
        staff_config(token)
        if action not in ACTIONS:
            raise HTTPException(422, "unknown action")
        last = db.latest_update(db_path)
        current = last.patients if last else 0
        # Every tap (also "Stimmt noch") is an update and resets the freshness clock. E6: never below 0.
        db.add_update(db_path, clock(), max(0, current + ACTIONS[action]))
        return RedirectResponse(f"/staff/{token}?ok=update", status_code=303)

    @app.post("/staff/{token}/feedback")
    def feedback(token: str, verdict: Annotated[str, Form()]):
        staff_config(token)
        if verdict not in db.VERDICTS:
            raise HTTPException(422, "unknown verdict")
        db.add_feedback(db_path, clock(), verdict)
        return RedirectResponse(f"/staff/{token}?ok=feedback", status_code=303)

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:create_app", factory=True, host="127.0.0.1", port=8000)
