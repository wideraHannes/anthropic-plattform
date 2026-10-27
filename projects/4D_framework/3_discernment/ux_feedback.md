# UX-Feedback: Klinik-Wartezeit-Prototyp

Stand: 2026-10-27

Farben und Aufbau sind gut, alle Kontraste liegen weit über WCAG AA. Die größten Lücken sind Fehlerbehandlung, fehlende Rückmeldung auf der Staff-Seite und der automatische Reload alle 60 s.

Geprüft wurden die öffentliche Seite (`code/templates/public.html`) und die Staff-Seite (`code/templates/staff.html`) gegen die vier Kriterien aus [`design.md`](design.md). Kontraste und Fehlerantworten sind per Skript gemessen, alles andere stammt aus dem Code-Review. Ein Browser-, axe- oder Lighthouse-Lauf steht noch aus.

## Clarity & Mental Model – teilweise erfüllt

Die Sprache passt zum Praxisalltag („Patienten im Wartezimmer“, „Anzeige für Patienten“, „öffnet wieder morgen 08:00“). Drei Beschriftungen führen aber in die Irre.

| Stelle | Problem | Vorschlag |
| --- | --- | --- |
| Button „unverändert“ (`staff.html:32`) | Gemeint ist „Zählung bestätigt“, das Wort klingt nach „nichts tun“ | „Stimmt noch ✓“ |
| Feedback „zu kurz / passt / zu lang“ (`db.py:10`) | Unklar, ob die Schätzung oder die Wartezeit gemeint ist. Ein Missverständnis verfälscht `calibrate.py` | „Wartezeit war länger / passt / kürzer“ |
| „Aktuell keine Schätzung verfügbar“ (öffentlich) | Kein Grund und keine Handlungsoption | Kontakt ergänzen, z. B. „Bei Fragen: Tel. …“ |

## Information Hierarchy – weitgehend erfüllt

Auf beiden Seiten steht das Wichtigste oben. Drei Details fehlen.

- **Öffentliche Seite:** Die Wartezeit ist das erste Element in 2.5rem, das sichern die Tests ab. Das Label „geschätzte Wartezeit“ steht aber erst darunter, ein Screenreader liest als Überschrift nur „15–20 min“.
- **Staff-Seite:** Die Reihenfolge Erinnerung → Zahl (6rem) → Buttons stimmt. Es fehlt eine `<h1>`, die Seite hat nur eine `<h2>` im Feedback-Block.
- **Handy-Layout (geschätzt, nicht im Browser geprüft):** Die Button-Reihe braucht etwa 430 px und bricht nicht um (kein `flex-wrap`). Auf 360 px Breite entsteht wahrscheinlich horizontales Scrollen.

## Accessibility – Kontrast gut, Timing nicht

Alle gemessenen Farbpaare liegen weit über dem AA-Minimum von 4.5:1. Das Problem ist der automatische Reload.

| Element | Farben | Kontrast |
| --- | --- | --- |
| Text hell | #1a1a1a auf #ffffff | 17.4:1 |
| Text dunkel | #f2f2f2 auf #121212 | 16.7:1 |
| Hinweisbox hell | #1a1a1a auf #e8f0fe | 15.2:1 |
| Detailtext dunkel | #d6d6d6 auf #121212 | 12.9:1 |
| Hinweisbox dunkel | #f2f2f2 auf #1f2b40 | 12.7:1 |
| Detail- und Meta-Text hell | #3d3d3d auf #ffffff | 10.9:1 |
| Erinnerung Staff | #7a1410 auf #fde2e1 | 8.9:1 |

- **Gut:** `lang="de"`, `aria-label` auf −/+, große Klickflächen, der Fokusrahmen des Browsers ist nicht entfernt.
- **`meta refresh` 60 s auf beiden Seiten:** Der Reload lässt sich nicht abschalten und verstößt damit gegen WCAG 2.2.1 (Timing Adjustable). Screenreader beginnen jede Minute von vorn, der Tastaturfokus springt zurück.
- **`role="alert"` auf der Erinnerung:** Zusammen mit dem Reload kann sie jede Minute neu angesagt werden.
- **Staff-Seite ohne Dark Mode:** Kein Fehler, aber anders als die öffentliche Seite.

## Feedback & Error Handling – schwächster Punkt

Die Staff-Seite bestätigt keine Eingabe, und Fehler erscheinen als rohes JSON ohne Handlungshinweis.

**Fehlende Rückmeldung**

- Nach einem Tap auf „unverändert“ ändert sich sichtbar nur „Letzte Eingabe vor 0 min“ (gemessen). Die öffentliche Seite zeigt hier „gerade aktualisiert“, eine Meldung wie „✓ Gespeichert“ fehlt.
- „−“ bei 0 Patienten wird still ignoriert, der Button ist nicht deaktiviert.
- Ein Doppeltipp zählt doppelt, es gibt keine Sperre.
- Nach abgegebenem Feedback verschwindet der Block ohne „Danke“.

**Fehlerfälle (gemessen)**

| Fall | Antwort heute | Was fehlt |
| --- | --- | --- |
| Falscher Token | 404 `{"detail":"Not Found"}` | Hinweis, den Link bei der Praxisleitung zu holen |
| Kaputte `config.json` | 503 `{"detail":"Konfiguration fehlerhaft"}` | HTML-Seite mit nächstem Schritt |
| Kaputte DB beim Tap | 500 Internal Server Error | Abfangen wie auf der öffentlichen Seite (E5) |

## Empfohlene Reihenfolge

Zuerst kommen die Fehlerseiten, weil ein 500 oder rohes JSON die Rezeption heute ohne Ausweg lässt.

- [x] Staff-Fehler als verständliche HTML-Seite ausgeben und den 500 bei DB-Fehlern abfangen
- [x] Nach jedem Tap „✓ Gespeichert“ anzeigen, „vor 0 min“ durch „gerade eben“ ersetzen
- [x] „unverändert“ und die Feedback-Buttons umformulieren
- [x] Reload entschärfen: auf der Staff-Seite entfernen oder abschaltbar machen, öffentlich mit Hinweis „aktualisiert sich automatisch“
- [x] `<h1>` auf der Staff-Seite ergänzen, „Wartezeit“ in die öffentliche Überschrift nehmen, `flex-wrap` für die Buttons
- [ ] axe- und Lighthouse-Läufe aus dem README nachholen

Umgesetzt am 2026-10-27, siehe `code/tests/test_acceptance.py` (Abschnitt „UX feedback“). Offen ist nur noch der axe- und Lighthouse-Lauf.
