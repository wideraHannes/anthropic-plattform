# Clinic wait time – prototype

Built from [`../handson.md`](../handson.md): product requirement (Step 1), technical spec (Step 2), tests (Step 3).

## Files

| File | Role |
|---|---|
| `app.py` | FastAPI app: public page `GET /`, staff page `GET /staff/<token>`, `POST …/update`, `POST …/feedback` |
| `estimate.py` | Pure logic: config validation, opening hours, freshness, range (`patients × minutes_per_patient`) |
| `db.py` | SQLite, append-only `updates` and `feedback` tables (timestamps stored in UTC) |
| `templates/` | `public.html` (< 1 KB, no JS, no external requests), `staff.html` (big `−` / `Stimmt noch` / `+`), `error.html` (staff errors) |
| `calibrate.py` | Calibration loop: feedback per weekday/hour → suggested `minutes_per_patient`; A7 check against measured waits |
| `config.json` | Opening hours, holidays, `minutes_per_patient`, quiet-times hint, staff token |
| `tests/test_acceptance.py` | A1–A7, E1–E8 + staff reminder / feedback / calibration + UX fixes from `../3_discernment/ux_feedback.md` |

Own `pyproject.toml`, so the root project stays free of web dependencies.

## Run

```bash
uv run python app.py          # http://127.0.0.1:8000  ·  staff: /staff/demo-token-change-me
uv run pytest -q              # 31 tests
uv run python calibrate.py [--actual waits.csv]
```

## Test coverage

| ID | Automated here | Still needs |
|---|---|---|
| A1 | ≤ 30 KB, no external URLs, `Cache-Control` | Lighthouse "Slow 3G" run for LCP < 3 s: `npx lighthouse http://127.0.0.1:8000 --form-factor=mobile` |
| A2, A3, A5, A6 | fully | – |
| A4 | `#wait` is first child of `<main>`, ≥ 24px, `lang="de"` | axe-core run: `npx @axe-core/cli http://127.0.0.1:8000` |
| A7 | the computation (`accuracy()`) | real arrival data from a pilot week → `calibrate.py --actual` |
| E1–E8 | fully | – |

## Design choices to defend

- **Patient count, not a wait picker.** Staff count, the system estimates; hourly feedback calibrates `minutes_per_patient`, a human applies it.
- **Every tap is an update**, including "Stimmt noch", so freshness measures staff attention, not count changes.
- **Degrade, don't fail.** Broken DB or config → "keine Schätzung", never a 500 on the public page.
- **Post/Redirect/Get on staff actions.** A6 "1 request per tap" is read as one write request; the redirect prevents a reload from counting a patient twice.
- **Token URL only** – fine for a prototype, not for production.
