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

Modul-Dokumentation (`__init__.py`):

- In jedem Modul übernimmt die zugehörige `__init__.py` eine zentrale, übergeordnete Beschreibung des gesamten
  Modulzwecks, seiner Bestandteile und seiner strukturellen Verantwortlichkeiten.
- Die einzelnen Dateien und Klassen innerhalb des Moduls enthalten anschließend ausschließlich präzise, spezifische
  Docstrings, die nur die Logik und Verantwortung der jeweiligen Klasse oder Funktion erläutern.
- Redundante oder mehrfach vorhandene Erklärungstexte entfallen vollständig, da alle allgemeinen Informationen
  konsolidiert im Modul-Docstring der `__init__.py` abgelegt sind.
- Dies sorgt für klare Trennung zwischen Modulbeschreibung und objektspezifischer Dokumentation, reduziert Pflegeaufwand
  und erhöht die Konsistenz innerhalb der Codebasis.

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

---

## 11. Markdown-Dokumentation

### Grundprinzipien

- **Einzige README.md**: Nur im Projekt-Hauptverzeichnis existiert eine `README.md`
- **Keine Unter-READMEs**: Unterordner (docs/, docs/dev/, etc.) enthalten **keine** eigenen README.md-Dateien
- **Zentrale Navigation**: Die Haupt-README.md verlinkt zu allen relevanten Dokumentations-Kategorien
- **Klare Ordnerstruktur**: Dokumente werden ausschließlich in `docs/` und dessen Unterordnern abgelegt

### Ordnerstruktur und Dokumenten-Kategorien

Alle Markdown-Dokumente (außer der Haupt-README.md) werden in `docs/` abgelegt:

```
docs/
├── dev/               # Entwickler-Dokumentation
├── description/       # Schüler-Dokumentation  
├── planning/          # Planungs- und Tracking-Dokumente
├── specs/             # Architektur-Spezifikationen
└── guidelines/        # Coding-Guidelines
```

#### docs/dev/ – Entwickler-Dokumentation

**Zweck**: Technische Dokumentation für Entwickler und Maintainer

**Dokument-Typen**:

- `changelog.md` – Chronologische Änderungshistorie (einheitliches Format)
- `setup-system.md` – Setup-System-Dokumentation
- `testing-tools.md` – Testing- und Debugging-Tools
- `architecture-decisions.md` – Architektur-Entscheidungen (ADRs)

**Namenskonvention**:

- Kleinbuchstaben mit Bindestrichen: `setup-system.md`, `testing-tools.md`
- Beschreibende Namen, die Inhalt klar kommunizieren
- Keine Abkürzungen, die nicht selbsterklärend sind

**Inhaltliche Struktur**:

```markdown
# Titel des Dokuments

Kurze Beschreibung (1-2 Sätze) des Dokument-Zwecks.

---

## Übersicht

Zusammenfassung des Dokuments.

## Hauptabschnitte

Detaillierte Inhalte mit klarer Gliederung.

## Referenzen

Links zu verwandten Dokumenten.
```

#### docs/description/ – Schüler-Dokumentation

**Zweck**: Anleitungen und Informationen für Schüler/Anwender

**Dokument-Typen**:

- `setup-anleitung.md` – Setup-Anleitung für Schüler
- `schulungsablauf.md` – Übersicht des Schulungsablaufs
- `aufgaben-*.md` – Einzelne Schulungsaufgaben

**Namenskonvention**:

- Kleinbuchstaben mit Bindestrichen
- Deutsche Namen für Schüler-Dokumente
- Präfixe für Aufgaben: `aufgaben-winkelberechnung.md`

**Stil**:

- Anfänger-freundlich, einfache Sprache
- Schritt-für-Schritt Anleitungen
- Viele Beispiele und Screenshots
- Problemlösungs-orientiert

#### docs/planning/ – Planungs-Dokumente

**Zweck**: Ticket-Tracking und Projektplanung

**Dokument-Typen**:

- `implementation-status.md` – Detaillierter Implementierungsstatus
- `refactoring-tracker.md` – Kompakte Ticket-Übersicht
- `_archived/` – Archivierte/obsolete Dokumente

**Namenskonvention**:

- Kleinbuchstaben mit Bindestrichen
- Status-orientierte Namen: `implementation-status.md`

#### docs/specs/ – Spezifikationen

**Zweck**: Architektur-Spezifikationen und Design-Dokumente

**Unterordner**:

- `architecture/` – Architektur-Dokumentation
- `notes/` – Design-Notizen und Konzepte

**Namenskonvention**:

- Beschreibende Namen mit Kontext: `core-simulation-zielbild.md`
- Modul- oder Komponenten-Präfixe

#### docs/guidelines/ – Richtlinien

**Zweck**: Coding-Standards und Projektrichtlinien

**Dokument-Typen**:

- `general-gd.md` – Allgemeine Python-Guidelines (dieses Dokument)
- `project/` – Projekt-spezifische Richtlinien

### Namenskonventionen (Zusammenfassung)

**Einheitliche Regeln für alle Dokumente**:

1. **Nur Kleinbuchstaben**: `mein-dokument.md` (nicht `Mein-Dokument.md`)
2. **Bindestriche statt Unterstriche**: `setup-anleitung.md` (nicht `setup_anleitung.md`)
3. **Keine Leerzeichen**: `mein-dokument.md` (nicht `mein dokument.md`)
4. **Beschreibende Namen**: Name muss Inhalt klar kommunizieren
5. **Präfixe für Zugehörigkeit**: `core-simulation-zielbild.md` (Modul-Präfix)
6. **Suffix nur bei Bedarf**: `-guide.md`, `-tutorial.md`, `-reference.md`

**Verbotene Namen**:

- `README.md` in Unterordnern (nur im Projekt-Root erlaubt)
- `TODO.md`, `NOTES.md` (zu vage)
- `doc.md`, `file.md` (nicht beschreibend)
- Versionsnummern im Namen: `setup-v1.md` (Versionierung über Git)

### Inhaltliche Struktur-Vorgaben

**Jedes Dokument folgt diesem Aufbau**:

```markdown
# Titel (# = H1, nur einmal pro Dokument)

Kurze Einleitung (1-3 Sätze): Was ist der Zweck dieses Dokuments?

---

## Abschnitt 1 (## = H2)

Inhalt...

### Unterabschnitt (### = H3)

Inhalt...

## Referenzen / Siehe auch

- [Verwandtes Dokument](pfad/zum/dokument.md)
- [Externes Link](https://example.com)
```

**Pflichtabschnitte**:

1. **Titel (H1)**: Eindeutiger, beschreibender Titel
2. **Einleitung**: 1-3 Sätze zum Dokument-Zweck
3. **Trennlinie** (`---`): Zwischen Einleitung und Hauptinhalt
4. **Hauptinhalt**: Strukturiert in H2-Abschnitte
5. **Referenzen** (optional): Links zu verwandten Dokumenten

**Formatierungs-Standards**:

- **Konsistente Überschriften**: H1 → H2 → H3 (keine Ebenen überspringen)
- **Code-Blöcke**: Immer mit Sprach-Tag: ` ```python `, ` ```bash `
- **Listen**: Konsistent mit `-` für ungeordnet, `1.` für geordnet
- **Hervorhebungen**:
    - `**fett**` für wichtige Begriffe
    - `*kursiv*` für Betonungen
    - `` `code` `` für Code-Snippets
- **Tabellen**: Markdown-Tabellen mit Header-Zeile

### Changelog-Spezifisches Format

Für `docs/dev/changelog.md` gilt ein standardisiertes Format:

```markdown
# Changelog – Projektname

Chronologische Auflistung aller Änderungen (neueste zuerst).

---

## [YYYY-MM-DD] - Kurztitel der Änderung

### Zusammenfassung

Kurze Beschreibung (1-2 Sätze).

### Problem/Motivation

Welches Problem wurde gelöst?

### Lösung/Implementierung

Konkrete technische Umsetzung.

### Betroffene Dateien

- `pfad/zu/datei.py`: Kurzbeschreibung
- `pfad/zu/anderer.py`: Kurzbeschreibung

### Impact

- **Entwickler**: Was müssen Entwickler beachten?
- **Schüler**: Was ändert sich für Schüler?
- **Breaking Changes**: Ja/Nein

### Referenzen

- Related Tickets: T1, T2
- Dokumentation: docs/dev/xxx.md
```

### Qualitätskriterien

**Vor dem Commit eines Dokuments prüfen**:

- ✅ **Dateiname**: Kleinbuchstaben, Bindestriche, beschreibend
- ✅ **Ablageort**: Korrekt in docs/-Unterordner einsortiert
- ✅ **Struktur**: Titel (H1), Einleitung, Trennlinie, Hauptinhalt
- ✅ **Überschriften**: Hierarchie korrekt (H1 → H2 → H3)
- ✅ **Code-Blöcke**: Mit Sprach-Tag versehen
- ✅ **Links**: Relativ und funktionsfähig
- ✅ **Markdown-Validierung**: Keine Syntax-Fehler
- ✅ **Redundanz**: Keine Duplikate zu anderen Dokumenten

### Dokumentations-Workflow

**Neue Dokumentation erstellen**:

1. **Zweck definieren**: Entwickler, Schüler, Planung, Spec, Guideline?
2. **Ordner wählen**: Entsprechend docs/-Unterordner
3. **Namen vergeben**: Nach Namenskonventionen
4. **Struktur aufbauen**: Template mit H1, Einleitung, Hauptinhalt
5. **Inhalt schreiben**: Gemäß Zielgruppe und Stil
6. **Referenzen hinzufügen**: Links zu verwandten Dokumenten
7. **Qualitätsprüfung**: Checkliste durchgehen
8. **Haupt-README aktualisieren**: Link zur neuen Dokumentation hinzufügen (falls relevant)

**Bestehende Dokumentation aktualisieren**:

1. **Changelog-Eintrag**: Bei Code-Änderungen in `docs/dev/changelog.md`
2. **Betroffene Docs identifizieren**: Welche Dokumente sind betroffen?
3. **Inhalte aktualisieren**: Änderungen einpflegen
4. **Datum aktualisieren**: "Letzte Aktualisierung" falls vorhanden
5. **Referenzen prüfen**: Links noch gültig?

**Dokumentation konsolidieren**:

1. **Duplikate identifizieren**: Welche Dokumente behandeln das Gleiche?
2. **Bestes Dokument wählen**: Welches ist strukturell am besten?
3. **Inhalte zusammenführen**: Einzigartige Inhalte übernehmen
4. **Obsolete löschen**: Alte Dokumente nach `_archived/` verschieben
5. **Links aktualisieren**: Verweise auf alte Dokumente anpassen

### Haupt-README.md

Die einzige `README.md` im Projekt-Root dient als Einstiegspunkt:

**Zweck**:

- Projekt kurz beschreiben (für Schüler verständlich)
- Quick Start mit minimalem Setup
- Links zu detaillierten Dokumentations-Kategorien
- Troubleshooting für häufige Probleme

**Inhalt (nicht zu überfrachten)**:

1. **Projekt-Titel und Kurzbeschreibung** (2-3 Sätze)
2. **Quick Start** (5 Schritte maximal)
3. **Installation** (Links zu `docs/description/setup-anleitung.md`)
4. **Weiterführende Dokumentation** (Links zu docs/-Kategorien)
5. **Troubleshooting** (Nur häufigste 3-5 Probleme)

**Was NICHT in die Haupt-README gehört**:

- Detaillierte Entwickler-Dokumentation → `docs/dev/`
- Architektur-Details → `docs/specs/`
- Vollständige Anleitung → `docs/description/`
- Changelogs → `docs/dev/changelog.md`

### Migration bestehender Dokumente

**Wenn alte Struktur vorhanden (z.B. Unter-READMEs)**:

1. **Inventar erstellen**: Alle bestehenden MD-Dateien auflisten
2. **Kategorisieren**: Entwickler / Schüler / Planung / Spec / Guideline?
3. **Umbenennen**: Nach Namenskonventionen
4. **Verschieben**: In korrekten docs/-Unterordner
5. **Konsolidieren**: Duplikate zusammenführen
6. **Haupt-README anpassen**: Links aktualisieren
7. **Unter-READMEs löschen**: Nur eine README.md im Root behalten

---
