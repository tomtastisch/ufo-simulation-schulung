# Richtlinien für umzusetzen­den Code (Tomtastisch)

Für alle von mir erwarteten Implementierungen gelten folgende Vorgaben:

- Produktiv nutzbarer, klar strukturierter Code, kein Demo-/Script-Stil; realistische, dynamische Berechnungen statt
  Magic Numbers oder `+1/-1`-Inkremente.
- Klare Trennung von:
    - Kernlogik / Domäne,
    - I/O und UI/Framework,
    - Konfiguration und Infrastruktur.
- Kleine, fokussierte Klassen/Funktionen; Komposition vor Vererbung; keine „God Objects“ und keine Methoden mit zu
  vielen Zuständigkeiten.
- Orientierung an der bestehenden Architektur und Modulen; öffentliche APIs möglichst stabil halten, neue Features
  intern integrieren statt zusätzliche `if`/`else`-Pflege beim Aufrufer zu erzwingen.
- Konfigurierbares Verhalten (Headless, Scaling, Destinations, Pfade, Parameter) über Funktions-/Konstruktorparameter,
  Config-Objekte oder Environment-Variablen; fachliche Parameter nicht hartkodiert.
- Konsequente Nutzung von Typannotationen (inkl. `from __future__ import annotations`) mit präzisen Typen aus `typing`;
  keine unnötigen `Any`-Typen oder untypisierte Sammelparameter.
- PEP-8-konformer Stil:
    - `snake_case` für Funktionen/Variablen,
    - `CapWords` für Klassen,
    - 4 Leerzeichen Einrückung, keine Tabs.
- Sprechende, konsistente Namen; möglichst geringe Komplexität pro Funktion, Vermeidung von Redundanz.
- Öffentliche Module/Klassen/Funktionen mit präzisen, deutschen Docstrings (Zweck, Parameter, Rückgabewerte,
  Besonderheiten); Modul-Übersichten zentral im jeweiligen `__init__.py` statt redundanter Wiederholungen in allen
  Dateien.
- Kommentare nur für nicht offensichtliche Aspekte (z. B. Numerik, Physik/Geometrie, Zustandsmaschinen,
  Threading/Concurrency, komplexe Algorithmen); keine Codebeispiele, kein Pseudocode und keine How-To-Anleitungen in
  Kommentaren.
- Fehlerbehandlung mit spezifischen Exceptions (`ValueError`, `TypeError`, `RuntimeError`, …) und klaren
  Fehlermeldungen; kein pauschales `except Exception` ohne triftigen Grund, kein `sys.exit()` in Kernlogik.
- Logging über das `logging`-Modul statt `print()`; Fokus auf relevante Ereignisse (Fehler/Warnungen, wichtige
  Statuswechsel, gezielte Debug-Information).
- Nebenläufigkeit (`threading`, `concurrent.futures`, `asyncio`) nur gezielt einsetzen; gemeinsam genutzter Zustand wird
  synchronisiert oder über immutable Strukturen / Message-Passing gehandhabt; keine stillen Race-Conditions.
- Vermeidung von Endlosschleifen, Stagnation und „Hängern“ durch klare Abbruchkriterien (Konvergenz, Toleranzen,
  Zustandsüberwachung), nicht nur durch reine Timer-Notabschaltungen.
- Physikalisch/algorithmisch plausible Simulationen mit korrekten Einheiten, sauberer Winkel- und Vektorgeometrie; klare
  Kriterien für Zustände wie Landung/Crash.
- Headless- und GUI-Modus teilen sich dieselbe API; Unterschiede werden über Konfiguration/Parameter/Environment
  gesteuert, nicht über unterschiedliche Aufrufmuster.
- Testbare Struktur:
    - Kernlogik frameworkfrei halten,
    - Unit-Tests und Black-Box-Tests ohne spezielle Hacks möglich machen,
    - `pytest`-kompatible Tests (Dateinamen `test_*.py`, `assert`-basierte Checks), deterministisch und schnell.
- Sicherheitsvorgaben:
    - Keine Secrets (Passwörter, Tokens, API-Keys, personenbezogene Daten) im Code,
    - Eingaben validieren, bevor sie in Kernlogik, DB oder OS-Operationen fließen,
    - Keine sensiblen Daten im Logging,
    - Für Auth/Krypto/Netzwerk nur etablierte Standard- oder geprüfte Bibliotheken, keine Eigenbau-Kryptographie.
- Externe Abhängigkeiten minimal und bewusst wählen:
    - Standardbibliothek bevorzugen,
    - zusätzliche Libraries nur bei klarem technischen Mehrwert,
    - kein „Library-Zoo“ für triviale Hilfsfunktionen.
- Kein toter Code, keine ungenutzten Parameter, keine leeren Platzhalter; TODO-Kommentare nur als konkrete, umsetzbare
  Aufgaben.
- Innerhalb dieser Grenzen sind verschiedene Stile (funktional vs. objektorientiert, alternative Algorithmen)
  ausdrücklich erlaubt, solange:
    - Lesbarkeit und Wartbarkeit verbessert werden,
    - fachliches Verhalten plausibel bleibt,
    - Tests bestehen und
    - bestehende öffentliche APIs nicht ohne Not gebrochen werden.