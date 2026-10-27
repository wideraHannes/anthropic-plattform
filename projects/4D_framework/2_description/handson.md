# Project

## Step 1: Write the product requirement

> One paragraph. Take the user need from your problem brief and scope it into something measurable. Every adjective should be a decision you can defend. If you write “fast,” write how fast. If you write “simple,” describe what simple means for a patient checking from a phone in a parking lot.

Patients can see the clinic's current estimated wait time on a single public web page that loads in under 3 seconds on a 10-year-old smartphone over a weak mobile connection, with no app install, login, or personal data required.
"Simple" means the wait time is the first and largest element on the screen (readable without zooming, minimum 24px),
shown as an honest range (e.g."30–45 min") rather than a falsely precise number, together with "last updated X min ago" so patients can judge freshness.

"Live" means the value is never older than 15 minutes during opening hours; if it is, the page says so instead of showing a stale number. Staff update the wait time with one tap from the reception PC, taking no more than 1 minute per hour in total. Outside opening hours the page shows the next opening time. A short hint ("usually quiet: Tue/Thu after 2 pm") helps patients plan visits at less crowded times, which is the underlying need.

## Step 2: technical spec

> Half a page. Describe what gets built and how it’s structured. Name the pieces. Name how they talk to each other. Use AI in augmentation mode here: share your product requirement, ask it to propose a technical approach, then push back on anything that doesn’t fit your constraints.

**Approach:** A single small Python web app (FastAPI + Jinja templates + SQLite), run locally as a prototype. German UI only.

**Pieces**

1. **Public page** (`GET /`): server-rendered HTML with inline CSS, < 30 KB, auto-reload via `<meta http-equiv="refresh" content="60">`. It renders exactly one of three states:
   - _open + fresh_: wait range in large type (≥ 24px) + "aktualisiert vor X min"
   - _open + stale_ (last update > 15 min): "Aktuell keine Schätzung verfügbar"
   - _closed_: next opening time

   The quiet-times hint is shown in every state.

2. **Staff page** (`GET /staff/<token>`): shows the current patient count as a big number with large `−` / `+` buttons and an "unverändert" button. Every tap counts as an update and resets the freshness clock. A banner warns when the last update is older than 12 min. Once per hour it asks for feedback on the estimate: "zu kurz / passt / zu lang".
3. **Backend**: stores events and computes the estimate:
   - `wait = patients × minutes_per_patient` (default 5)
   - shown as the range `[wait, wait + 15]`, rounded to 5 min
   - 0 patients → "kaum Wartezeit"
   - wait ≥ 120 min → "über 2 Std." instead of a range
4. **Storage**:
   - SQLite, append-only tables `updates(ts, patients)` and `feedback(ts, verdict)`
   - `config.json` with opening hours, `minutes_per_patient`, quiet-times hint text, staff token, timezone `Europe/Berlin`

**How they talk**

- Staff browser → `POST /staff/<token>/update` or `/feedback` (HTML form, redirect back) → SQLite.
- Patient browser → `GET /` → backend reads the latest update + config, decides the state, renders HTML. `Cache-Control: max-age=30`.

**Calibration loop:** Hourly feedback is stored but not applied automatically in the prototype. A script (`calibrate.py`) summarises feedback per weekday/hour and suggests a new `minutes_per_patient`, which a human applies in `config.json`. Automatic correction comes later, once the data shows it is stable.

**Error handling & assumptions**

- If the DB or config can't be read, the public page shows the "keine Schätzung" state, never a 500 error.
- All times are computed in `Europe/Berlin`; holidays are listed manually in the config.
- Security is a secret token URL only: acceptable for a prototype, not for production.
- **Known tension:** `+`/`−` per patient may exceed "1 min/hour" on busy hours. Validate this in the first staff test.

## Step 3: Tighten your tests

> Revisit your acceptance tests from the previous lesson. Rewrite them so each one is something code could pass or fail. Add at least two edge cases: what happens when the clinic is closed, when there's no data, when the wait time is zero.

**After:** Default fixture unless stated otherwise: clinic open, `minutes_per_patient = 5`, last update 2 min ago. "Wait element" = the element with `id="wait"`.

### Acceptance tests

| ID              | Given / When                                                   | Then (pass/fail)                                                                                                        | Checked by                   |
| --------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| A1 Fast         | `GET /` under Lighthouse mobile, "Slow 3G" + 4× CPU throttling | Response ≤ 30 KB, 0 external requests, LCP < 3 s                                                                        | Lighthouse CI                |
| A2 No account   | `GET /` without cookies or auth header                         | `200`; page contains no `<form>` and no login link                                                                      | pytest                       |
| A3 Range        | 6 patients                                                     | Wait element reads `30–45 min`                                                                                          | pytest                       |
| A4 Readable     | Any open + fresh state                                         | Wait element is the first child of `<main>`, `font-size ≥ 24px`; axe-core reports 0 violations (incl. contrast ≥ 4.5:1) | Playwright + axe             |
| A5 Freshness    | Last update 14 min ago / 16 min ago                            | 14 min: range + `aktualisiert vor 14 min`. 16 min: `Aktuell keine Schätzung verfügbar`, no number on the page           | pytest (frozen clock)        |
| A6 Staff effort | Staff taps `+`, `−` or `unverändert`                           | Exactly 1 request per tap, response < 500 ms, update visible on `GET /` immediately                                     | pytest                       |
| A7 Accuracy     | Pilot week, real arrivals logged                               | ≥ 80 % of actual waits fall inside the displayed range                                                                  | `calibrate.py` on pilot data |

### Edge cases

| ID                | Given / When                                    | Then                                                             |
| ----------------- | ----------------------------------------------- | ---------------------------------------------------------------- |
| E1 Closed         | Outside opening hours, even with a fresh update | `Geschlossen – öffnet wieder <Tag> <HH:MM>`; no wait range shown |
| E2 Holiday        | Today is listed in `config.json` holidays       | Same as E1, next opening skips the holiday                       |
| E3 No data        | Clinic open, `updates` table empty              | `200`, `Aktuell keine Schätzung verfügbar`                       |
| E4 Zero wait      | 0 patients                                      | `kaum Wartezeit`, not `0–15 min`                                 |
| E5 Broken storage | DB file missing or `config.json` invalid        | `200` with the E3 message, never a `500`                         |
| E6 Negative count | Count is 0, staff taps `−`                      | Count stays 0, no error                                          |
| E7 Wrong token    | `POST /staff/<wrong>/update`                    | `404`, no row written                                            |
| E8 Very long wait | 23 / 24 / 30 patients                           | 23: `115–130 min`. 24 and 30: `über 2 Std.`, no range shown      |

## Demo It

- Everything works nicely, but one thing. The Staff has to update this screen regulary,
- So the USer Voice: Staff "Dont waste too much time on this tool", is not mapped to requirements correctly.
- We Need after "time_per_patient" the number of patienten im Wartezimmer has to automatically Reduce by 1.
- We need a feedback to intelligently adjust the time_per_patient via a moving avg
