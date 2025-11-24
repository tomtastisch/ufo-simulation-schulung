# Dokumentationsstruktur für `ufo-simulation-schulung`

Dieses Dokument beschreibt die geplante Zielstruktur der Projektdokumentation sowie die Rolle der einzelnen Ordner und
Dateien.
Ziel ist eine klare Trennung zwischen Richtlinien, Planung, Spezifikationen und technischen Änderungsdokumentationen,
mit konsistenter Verweiskette („eine-Ebene-Regel“).

---

## 1. Zielbild der Dokumentationsstruktur

```text
project-root/
├─ README.md                     # Verweist NUR auf: docs/guidelines, docs/planning, docs/specs, docs/description, docs/dev
└─ docs/
   ├─ guidelines/
   │  └─ general-gd.md          # Globale Richtlinien (Code, Doku, Naming …)
   │
   ├─ planning/
   │  ├─ implementation-status.md   # Status T0–T10 (Quelle: implementation-status.md)
   │  └─ refactoring-tracker.md     # Ablaufplan/Phasen, Tickets T0–T17 (Quelle: refactoring-tracker.md)
   │
   ├─ specs/
   │  ├─ architecture/
   │  │  ├─ core-simulation-zielbild.md      # T0 – Zielbild
   │  │  └─ core-simulation-importregeln.md  # T1 – Importhierarchie
   │  │
   │  └─ notes/
   │     └─ introductions.md                 # Gesamt-Fahrplan Phasen/Tickets
   │
   ├─ description/
   │  ├─ setup-anleitung.md                  # Setup-Anleitung für Nutzer/Studierende
   │  └─ schulungsablauf.md                  # Didaktischer Ablauf der Schulung
   │
   └─ dev/
      ├─ CHANGELOG.md                        # Zentrales, chronologisches Log (unverändert als Master-Log)
      │
      ├─ developer-overview.md               # Hoher Überblick für Devs
      ├─ setup-system-tools.md               # Aufbau & Verwendung des neuen tools/-Systems
      ├─ concurrency-and-testing-tools.md    # Gesamtarchitektur Concurrency/Locks/@conditional + Test-Grundsätze
      ├─ test-architecture-overview.md       # Teststrategie, Testpyramide, Mapping src/ ↔ tests/
      │                                      # Alle diese Dateien VERWEISEN nur auf updates/ und refactoring/, 
      │                                      # enthalten aber keine vollständigen Changelogs.
      │
      ├─ updates/                            # „Was wurde geändert?“ – Spezifikation der Änderungen je Thema
      │  ├─ 2025-11-23-tools-setup-and-rich-ui.md
      │  │     # Bündelt ALLES aus:
      │  │     #   - [2025-11-23] Setup-System, Tools-Struktur und Rich UI Integration (tools/)
      │  │     #   - inkl. Rich-Text/Rich-Konsole + Bugfixes (Textressourcen, Progress-Balken, Error-Logging)
      │  │     #   - Zuordnung zu künftigen Tools-Tickets
      │  │
      │  ├─ 2025-11-22-observer-module-T9.md
      │  │     # Refactoring T9: Observer-Modul (Phase, StateObserver, ManeuverAnalysis)
      │  │     # Quelle: CHANGELOG-Eintrag [2025-11-22] + Ticket T9 aus refactoring-tracker/implementation-status
      │  │
      │  ├─ 2025-11-21-concurrency-locking-and-conditions.md
      │  │     # FASST ZUSAMMEN:
      │  │     #   - [2025-11-21] Lock-Verwendung validiert und verschachtelte Locks behoben
      │  │     #   - [2025-11-21] Zentrale Lock-Wrapper-Utility (DRY-Refactoring)
      │  │     #   - [2025-11-21] Einführung von @conditional Decorator und ConditionWaiter
      │  │     #   → ein gemeinsames Concurrency-Update-File statt 3–4 Einzeldateien
      │  │
      │  ├─ 2025-11-21-test-structure-reorganization.md
      │  │     # [2025-11-21] Test-Struktur-Reorganisation nach Best Practice
      │  │     # Fokus: neue tests/ Struktur, Spiegelung von src/
      │  │
      │  ├─ 2025-11-19-documentation-consolidation.md
      │  │     # [2025-11-19] Dokumentations-Konsolidierung
      │  │     # Neu-/Umverteilung von general-gd.md, planning/*, specs/*, dev/*
      │  │
      │  ├─ 2025-11-19-infrastructure-logging-and-exceptions-T4.md
      │  │     # Deckt T4 ab:
      │  │     # logging_setup.py & exceptions.py (Status: abgeschlossen lt. implementation-status)
      │  │     # Falls kein eigener CHANGELOG-Block existiert → hier sauber beschrieben
      │  │
      │  ├─ 2025-11-18-core-simulation-T0-zielbild.md
      │  │     # [2025-11-18] Refactoring T0: Zielbild dokumentiert
      │  │     # Cross-Ref: core-simulation-zielbild.md
      │  │
      │  ├─ 2025-11-18-core-simulation-T1-importhierarchie.md
      │  │     # [2025-11-18] Refactoring T1: Importhierarchie dokumentiert
      │  │     # Cross-Ref: core-simulation-importregeln.md
      │  │
      │  └─ 2025-11-18-core-simulation-T3-state-refactoring.md
      │        # [2025-11-18] Refactoring T3: UfoState nach state/state.py
      │        # Cross-Ref: implementation-status T3 + code in state/state.py
      │
      └─ refactoring/                        # „Wie wurde refactored?“ – technische Tiefendokus je Themenblock
         ├─ tools-and-rich-ui-refactoring.md
         │   # Technische Details zur neuen tools/ Struktur, Rich-UI-Integration, Textkatalog/TOML
         │   # Baut auf updates/2025-11-23-tools-setup-and-rich-ui.md auf
         │
         ├─ observer-module-T9-refactoring.md
         │   # Interne Struktur observer/: Phase, compute_phase(), StateObserver, ManeuverAnalysis
         │   # Zuordnung zu T9, inkl. Designentscheidungen und Randfälle
         │
         ├─ concurrency-locking-and-conditions-refactoring.md
         │   # Gemeinsames Refactoring-Dokument für:
         │   #   - Lock-Wrapper-Utility
         │   #   - @conditional Decorator
         │   #   - ConditionWaiter
         │   #   - Bereinigte Lock-Patterns (Anti-Pattern-Analyse)
         │   # -> ersetzt frühere Einzelideen wie lock-usage-validation.md, concurrency-condition-waiter-refactoring.md
         │
         ├─ test-structure-reorganization-refactoring.md
         │   # Detaillierte Beschreibung der neuen Testarchitektur:
         │   #   - Mapping tests/ ↔ src/
         │   #   - Konventionen für neue Tests
         │   #   - Migrationsstrategie für Alt-Tests
         │
         ├─ documentation-structure-refactoring.md
         │   # Ergänzung zu 2025-11-19-documentation-consolidation.md
         │   # Begründung der neuen Doku-Ebenen und der „eine-Ebene“-Verweiskette
         │
         ├─ infrastructure-logging-and-exceptions-T4-refactoring.md
         │   # Tiefen-Refactoring-Doku für logging_setup.py, Exception-Hierarchie,
         │   # Thread-Safety, Logging-Konfiguration
         │
         └─ core-simulation-phase0-3-refactoring.md
             # Sammel-Dokument für T0–T3/T4/T5–T8:
             #   - Zielbild (T0)
             #   - Importregeln (T1)
             #   - State/manager/observer Übergang (T3, T8, T9-Referenz)
             #   - Utilities & Physik (T5–T7)
             #   - Infrastruktur-Basics (T4)
             # Dient als „Story“ der gesamten Phase 0–3, referenziert die einzelnen Updates-* Files.

```

---

## 2. Grundprinzipien

1. **Trennung nach Zweck**

    * `guidelines/`: Generelle Regeln und Leitlinien.
    * `planning/`: Ticket- und Implementierungsstatus.
    * `specs/`: Fachliche/architektonische Spezifikation.
    * `description/`: „Benutzernahe“ Beschreibungen (Setup, Schulungsablauf).
    * `dev/`: Technische Entwicklerdokumentation, Änderungs- und Refactoring-Historie.

2. **Eine-Ebene-Regel für Verweise**

    * Jede Ebene verweist nur auf die unmittelbar darunter liegende Ebene.
    * `README.md` verweist ausschließlich auf `docs/<top-level>`.
    * Die erste Ebene unter `docs/` verweist nur auf je ihre eigenen Unterordner/Übersichten.
    * Detaillierte Dateien (z. B. einzelne Updates) werden über Zwischendokumente referenziert, nicht direkt aus dem
      README.

3. **Trennung von „Was“ und „Wie“**

    * `docs/dev/updates/`: „Was wurde geändert?“ – zusammengefasste, thematische CHANGELOG-Einträge.
    * `docs/dev/refactoring/`: „Wie wurde es technisch umgesetzt?“ – Tiefendokumentation der Refactorings.
    * Oberste Ebene in `docs/dev` enthält nur übergreifende, konzeptionelle Dokumente und verweist auf `updates/` und
      `refactoring/`.

---

## 3. Bedeutung der Hauptordner

### 3.1 `docs/guidelines/`

* Enthält globale Richtlinien, die projektweit gelten (z. B. Coding-Guidelines, Doku-Konventionen, Namensregeln).
* `general-gd.md` dient als zentrale Referenz für:

    * Coding Style und PEP-8/Projekt-spezifische Ergänzungen.
    * Modulare Architektur- und Layering-Regeln auf hoher Ebene.
    * Anforderungen an Tests, Dokumentation und Branch-/Ticket-Konventionen.
* Andere Dokumente verweisen semantisch auf diese Guidelines, implementieren sie aber nicht selbst.

### 3.2 `docs/planning/`

* Spiegelt den Projektstatus aus Ticket-/Refactoring-Sicht:

    * `implementation-status.md`: Übersicht, welche Tickets/TODOS abgeschlossen, in Arbeit oder geplant sind.
    * `refactoring-tracker.md`: Chronologische/Phasen-orientierte Übersicht über Refactorings (z. B. T0–T17).
* Dient als Ausgangspunkt für die Frage: „Wo steht das Projekt aktuell?“ und „Welches Ticket erzeugt welche Änderung in
  `docs/dev/updates/`?".

### 3.3 `docs/specs/`

* Beinhaltet fachliche und architektonische Spezifikation:

    * `architecture/`:

        * `core-simulation-zielbild.md`: Zielbild und Soll-Architektur der Kernsimulation (T0).
        * `core-simulation-importregeln.md`: Import- und Layering-Regeln (T1).
    * `notes/`:

        * `introductions.md`: Einstieg und Gesamtfahrplan der Phasen (z. B. Phase 0–3, T0–T17).
* Diese Dokumente beschreiben den Soll-Zustand und dienen als Referenz für Implementierung und Refactoring-Dokumente.

### 3.4 `docs/description/`

* Fokus auf Nutzung und Schulung, nicht auf Implementierungsdetails:

    * `setup-anleitung.md`: Schritt-für-Schritt-Setup aus Nutzersicht (z. B. Studierende).
    * `schulungsablauf.md`: Didaktischer Ablauf und Einsatz der Simulation im Unterricht/Training.
* Hat vor allem Mehrwert für Lehrende, Studierende und Stakeholder ohne tiefen technischen Fokus.

---

## 4. Rolle von `docs/dev/`

`docs/dev/` ist ausschließlich für Entwickler:innen und fortgeschrittene technische Leser gedacht.

### 4.1 Top-Level in `docs/dev/`

* `CHANGELOG.md`:

    * Zentrales, chronologisches Änderungslog.
    * Dient als Master-Quelle für alle Änderungen, wird aber nicht in unendlich viele kleine Dateien aufgespalten.
    * Thematisch zusammengehörende Einträge (z. B. Rich-UI, Concurrency, Observer) werden in je ein Updates-Dokument
      überführt.

* `developer-overview.md`:

    * Einstiegspunkt für Entwickler:innen.
    * Erklärt den Gesamtaufbau von `docs/dev/` und verweist auf:

        * `setup-system-tools.md`
        * `concurrency-and-testing-tools.md`
        * `test-architecture-overview.md`
        * sowie die relevanten `updates/`- und `refactoring/`-Dokumente.

* `setup-system-tools.md`:

    * Beschreibt Aufbau und Verwendung des Tools-/Setup-Systems.
    * Fokus: CLI-Tools, Setup-Abläufe, Rich-Konsole, Logging-Integration.
    * Verweist auf das thematische Updates-Dokument `2025-11-23-tools-setup-and-rich-ui.md` und das zugehörige
      Refactoring-Dokument `tools-and-rich-ui-refactoring.md`.

* `concurrency-and-testing-tools.md`:

    * Hohe Ebene zu Concurrency-Konzepten (Locks, Decorator, Condition-Waiter) und deren Testabdeckung.
    * Verweist auf:

        * `2025-11-21-concurrency-locking-and-conditions.md`
        * `concurrency-locking-and-conditions-refactoring.md`.

* `test-architecture-overview.md`:

    * High-Level-Testarchitektur, Testpyramide, Konventionen.
    * Verweist auf:

        * `2025-11-21-test-structure-reorganization.md` (Updates)
        * `test-structure-reorganization-refactoring.md`.

### 4.2 `docs/dev/updates/`

* Enthält pro Thema ein gesamthaftes Updates-Dokument, das alle relevanten CHANGELOG-Einträge und Tickets bündelt.

Beispiele:

* `2025-11-23-tools-setup-and-rich-ui.md`

    * Bündelt alle Änderungen zum Tools-System, Rich-UI-Integration, Textressourcen, Progress-Balken, Error-Logging.
    * Leitet sich aus mehreren CHANGELOG-Blöcken ab, die inhaltlich zusammengehören (statt mehrere Mikrodokumente).

* `2025-11-22-observer-module-T9.md`

    * Ticket-basiertes Update-Dokument für das Observer-Modul (T9).

* `2025-11-21-concurrency-locking-and-conditions.md`

    * Fasst Änderungen zu Lock-Validierung, Lock-Wrapper, `@conditional` und `ConditionWaiter` in einem Dokument
      zusammen.

* Weitere Dateien (`…-test-structure-reorganization.md`, `…-documentation-consolidation.md`,
  `…-infrastructure-logging-and-exceptions-T4.md`, `…-core-simulation-*.md`) dokumentieren jeweils den „Was wurde
  geändert?“-Aspekt für ihre Themenbereiche.

### 4.3 `docs/dev/refactoring/`

* Enthält vertiefende technische Dokumentation je Themenblock.

Beispiele:

* `tools-and-rich-ui-refactoring.md`

    * Vertiefte Darstellung der neuen `tools/`-Struktur, Rich-UI-Integration, Textkatalog (z. B. TOML),
      Architekturentscheidungen.

* `observer-module-T9-refactoring.md`

    * Technisches Refactoring-Dokument des Observer-Moduls, inklusive State-/Phase-Beziehungen und Designentscheidungen.

* `concurrency-locking-and-conditions-refactoring.md`

    * Detaillierte Analyse von Lock-Patterns, `@conditional`, `ConditionWaiter` und bisherigen Anti-Patterns.

* `test-structure-reorganization-refactoring.md`

    * Wie genau die Tests neu strukturiert wurden, inkl. Migrationsstrategie für Alt-Tests.

* `documentation-structure-refactoring.md`

    * Begründung der neuen Dokumentationsstruktur und der „eine-Ebene“-Verweiskette.

* `infrastructure-logging-and-exceptions-T4-refactoring.md`

    * Detaildoku zu Logging-Setup und Exception-Hierarchie.

* `core-simulation-phase0-3-refactoring.md`

    * Zusammenhängende „Story“ der Refactorings T0–T3 (bzw. T0–T8/T4/T5–T7), referenziert einzelne Updates-Dokumente.

---

## 5. Verweiskonzept („eine-Ebene-Regel“)

1. `README.md`:

    * Verweist nur auf:

        * `docs/guidelines/`
        * `docs/planning/`
        * `docs/specs/`
        * `docs/description/`
        * `docs/dev/`
    * Keine direkten Verweise auf tiefere Ebenen.

2. `docs/<top-level>/`:

    * Jedes Top-Level-Verzeichnis hat eine oder mehrere Übersichtsdateien (z. B. `developer-overview.md`,
      `introductions.md`), die auf die nächste Ebene verweisen.
    * Beispiel: `developer-overview.md` verweist auf `updates/` und `refactoring/`, aber nicht auf einzelne
      Tickets/Commits.

3. `updates/` ↔ `refactoring/`:

    * Jedes `updates/*.md` kann auf das korrespondierende `refactoring/*.md` verweisen (und umgekehrt).
    * Mapping zu Tickets und CHANGELOG-Einträgen erfolgt in diesen Dateien, nicht auf höherer Ebene.

---

## 6. Mapping Tickets und CHANGELOG zu Dokumenten

* Jeder abgeschlossene Ticket-Eintrag in `implementation-status.md` besitzt mindestens:

    * ein thematisch zugeordnetes Dokument in `docs/dev/updates/` (Was wurde geändert?), und
    * falls technisch relevant, ein Dokument in `docs/dev/refactoring/` (Wie genau wurde refactored?).

* Jeder relevante Block aus `CHANGELOG.md` fließt in ein passendes Updates-Dokument ein.
  Mehrere zusammengehörende Einträge (z. B. alle Rich-UI-Anpassungen) werden in einem gemeinsamen Updates-File
  gebündelt, statt fragmentiert vorzuliegen.

Damit entsteht ein konsistentes System, in dem:

* `guidelines/` und `specs/` den Soll-Zustand definieren,
* `planning/` den Projektfortschritt beschreibt,
* `description/` den Anwender-/Schulungsaspekt abdeckt,
* `dev/` alle technischen Änderungen und Refactorings nachvollziehbar und thematisch gebündelt dokumentiert.