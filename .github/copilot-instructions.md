# Allgemeine Richtlinien – Python-Code und Simulations-/Kernmodule

## Allgemeine Richtlinien und Vorgaben by Tomtastisch

Diese allgemeinen Regeln gelten für alle Projekte und Module, unabhängig vom konkreten Anwendungsfall. Sie sind persönlich festgelegte Zielvorgaben und Rahmenbedingungen, welche sowohl der Sicherstellung der Wiederverwendbarkeit eigener Projekte als solche, sowie auch der Zusammenarbeit mit Dritten dienen.

---

## 1. Allgemeine Ziele

- Schreibe kurzen, klar strukturierten, produktiv nutzbaren Code, kein Demo-/„Script“-Stil.
- Bevorzuge realistische, dynamische Berechnungen statt fixer Inkremente oder Magic Numbers (z. B. physikalisch korrekte Berechnung von Geschwindigkeit, Beschleunigung, Bremsweg statt `+1`/`−1` in Schleifen).
- Gestalte Code so, dass er in komplexeren, modularen Projekten wiederverwendbar und erweiterbar ist (Clean Architecture, Single Responsibility, geringe Kopplung).

---

## 2. Architektur & Struktur

Trennung:

- Domänenlogik / Kernlogik (Simulation, Berechnung, Geschäftslogik),
- I/O und UI/Framework (CLI, PyQt, Logging, Persistence, Netzwerk),
- Konfiguration und Infrastruktur.

Modulare Strukturen:

- Kleine, klar abgegrenzte Klassen und Funktionen.
- Komposition vor Vererbung, wo dies sinnvoll ist.
- Keine „God Objects“, keine Methoden mit zu vielen Zuständigkeiten.

API-Stabilität:

- Öffentlich erwartete Aufrufmuster dürfen nicht ohne Not gebrochen werden.
- Neue Features (z. B. Headless-Modus, Progress-Logik, Autopilot) werden intern integriert, ohne dass Aufrufer zusätzliche `if`/`else`-Pfade pflegen müssen.

Konfiguration:

- Konfigurierbares Verhalten (Headless, Scaling, Destinations, Pfade, Parameter) über:
  - Funktions-/Konstruktorparameter,
  - dedizierte Konfigurationsobjekte,
  - oder Environment-Variablen.
- Keine hartkodierten Magic Numbers im Code, wenn sie fachlich Parameter sind.

---

## 3. Stil, Typisierung & Rückgabeverhalten

PEP-8-konformer Stil:

- `snake_case` für Funktionen/Variablen,
- `CapWords` für Klassen,
- 4 Leerzeichen Einrückung, keine Tabs.

Typisierung:

- Systematischer Einsatz von Type Hints für Parameter und Rückgabewerte.
- `from __future__ import annotations` nutzen, wenn hilfreich.
- Präzise Typen aus `typing` verwenden (z. B. `Optional`, `Literal`, `Union`, `Protocol`, `TypeAlias`).

Rückgaben:

- Möglichst klar strukturierter Kontrollfluss mit gut lesbarem Rückgabepunkt.
- Frühe Rückgaben sind erlaubt, wenn sie die Lesbarkeit durch Guard-Clauses verbessern.

Attribute vs. Getter/Setter:

- `dataclasses` oder schlanke Klassen mit klaren Attributen bevorzugen.
- Properties/Funktionen nur bei zusätzlicher Logik (Validierung, Lazy-Berechnung, Caching).
- Keine rein mechanischen Getter/Setter ohne Mehrwert.

---

## 4. Dokumentation & Kommentare

Docstrings:

- Jede öffentliche Klasse, Funktion und jedes Modul erhält einen präzisen Docstring mit:
  - Kurzbeschreibung des Zwecks,
  - relevanten Parametern und Rückgabewerten,
  - Besonderheiten (Nebenwirkungen, Ausnahmen, Thread-Sicherheit, Performance-Hinweise).

Stil:

- Klare, sachliche, technische Sprache ausschließlich auf Deutsch und innerhalb eines Moduls konsistent eingesetzt.
- Strukturierte Docstrings (z. B. Google- oder NumPy-Stil).

Kommentare:

- Nur nicht offensichtliche Aspekte kommentieren (Numerik, Physik/Geometrie, Zustandsmaschinen, Threading/Concurrency, komplexe Algorithmen).
- Keine Kommentare, die nur den Code „nacherzählen“.

TODOs:

- Nur konkrete, umsetzbare Aufgaben, keine vagen Hinweise.

---

## 5. Fehlerbehandlung, Logging & Beenden

Fehlerbehandlung:

- Spezifische Exceptions verwenden (`ValueError`, `TypeError`, `RuntimeError`, etc.).
- Klare Fehlermeldungen bei falschen Vorbedingungen.
- Kein pauschales `except Exception:` ohne triftigen Grund; wenn nötig, dann mit Logging und Re-Raise.

Logging:

- `logging`-Modul statt `print()` in produktivem Code.
- Log-Ausgaben auf relevante Ereignisse beschränken (Fehler/Warnungen, wichtige Statuswechsel; Debug-Information gezielt).

Beenden:

- Keine `sys.exit()`-Aufrufe in Bibliotheks- oder Kernlogik.
- Sauberes Beenden über Rückgabewerte, Exceptions oder klar definierte API-Methoden (`close()`, `shutdown()`, `terminate()`); der Aufrufer entscheidet über das Prozessende.

---

## 6. Nebenläufigkeit, Simulation & Laufzeitverhalten

Nebenläufigkeit:

- `threading`, `concurrent.futures` oder `asyncio` nur gezielt einsetzen.
- Gemeinsamer Zustand wird entweder:
  - synchronisiert (Locks, Queues),
  - oder auf immutable Strukturen / Message-Passing reduziert.
- Keine stillen Race-Conditions auf gemeinsamem Zustand.

Simulation / physikalische Logik:

- Physikalisch/algorithmisch plausible Berechnungen:
  - korrekte Einheiten (z. B. km/h ↔ m/s),
  - saubere Winkelberechnungen,
  - Vektorgeometrie statt willkürlicher Inkremente.

- Stagnation, Endlosschleifen und Hängenbleiben erkennen:
  - algorithmische Kriterien (Konvergenz, Toleranzen, Zustandsüberwachung),
  - keine reinen Timer-„Notabschaltungen“ als einziges Kriterium.

Landung / Crash-Erkennung (für UAV-/UFO-Kontexte):

- Konsistente, nachvollziehbare Kriterien:
  - sichere Landung → definierter Zustand (`z = 0`, `v ≈ 0`, kein negativer Marker),
  - Crash → klarer Marker (`z < 0` oder expliziter Status) und Logging eines Ereignisses.

Headless vs. GUI:

- API bleibt identisch, egal ob GUI aktiv ist oder nicht.
- Modi (Headless/GUI, Logging an/aus etc.) werden über Konfiguration/Parameter/Environment gesteuert, nicht über andere Aufrufmuster.

---

## 7. Testbarkeit & Qualität

- Kernlogik frameworkfrei halten (keine direkte UI-, OS- oder Netzwerkabhängigkeit in der Domänenschicht).
- Funktionen und Klassen so gestalten, dass Unit-Tests und Black-Box-Tests ohne spezielle Hacks möglich sind.

Tests:

- `pytest`-kompatibler Stil (`test_*.py`, `assert`-basierte Checks).
- Deterministisch und schnell, ohne externe Systeme (Netzwerk, Datenbanken) – außer ausdrücklich spezifiziert.

Für komplexe numerische/physikalische Logik:

- Grenzfälle,
- typische Szenarien,
- Fehlerfälle (z. B. ungültige Parameter) abdecken.

---

## 8. Sicherheits- und Datenschutz-Aspekte

Keine Hardcoded-Secrets:

- Keine Passwörter, Tokens, API-Keys oder sensiblen Daten im Quellcode.

Eingabevalidierung:

- Externe Eingaben (User, Netzwerk, Dateien, Umgebungsvariablen) validieren, bevor sie in:
  - Kernlogik,
  - Datenbanken,
  - OS-Operationen einfließen.

Logging:

- Keine sensiblen Daten loggen (Passwörter, vollständige Tokens, geheime Schlüssel, personenbezogene Daten).

Sicherheitsrelevante Funktionen:

- Für Authentifizierung, Kryptographie und Netzwerk nur Standardbibliotheken oder etablierte, geprüfte Bibliotheken nutzen.
- Keine Eigenbau-Kryptographie.

---

## 9. Abhängigkeiten & Bibliotheken

- Standardbibliothek bevorzugen, wenn sie das Problem angemessen löst.

Zusätzliche Bibliotheken nur bei klarem technischen Mehrwert:

- z. B. `numpy` für numerische Vektorrechnung,
- PyQt/Tkinter für GUI,
- `pydantic` o. Ä. für Validierung/Konfiguration, falls sinnvoll.

Weitere Vorgaben:

- Anzahl externer Abhängigkeiten minimal halten:
  - keine Convenience-Bibliotheken nur für triviale Helferfunktionen.
- Bibliotheken konsistent und bewusst einsetzen (kein „Library-Zoo“).

---

## 10. Gestaltungsspielräume

Innerhalb der genannten Grenzen sind verschiedene Umsetzungen explizit erlaubt, sofern sie:

- Lesbarkeit und Wartbarkeit verbessern,
- das reale/fachliche Verhalten plausibel abbilden,
- testbar und erweiterbar bleiben,
- bestehende öffentliche APIs nicht brechen.

Stilspielräume:

- Funktionaler vs. objektorientierter Stil ist frei wählbar, solange Architekturziele (Trennung, Modularität, Testbarkeit) eingehalten werden.
- Algorithmen dürfen verbessert werden (präzisere Numerik, bessere Konvergenz, bessere Performance), sofern:
  - die API stabil bleibt,
  - definierte fachliche Erwartungen und Tests weiterhin erfüllt werden.