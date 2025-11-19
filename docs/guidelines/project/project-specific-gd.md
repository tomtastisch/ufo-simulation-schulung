# Spezifische Vorgaben für Simulations- und Kernmodule by Tomtastisch

## 1. Ermittlung des aktuellen Manövers / „Was macht das System gerade?“

- Der aktuelle Zustand bzw. das „Manöver“ eines Simulationsobjekts (z. B. Drohne/UFO) ist kein separater, dauerhaft
  gepflegter Status, sondern wird bei Bedarf berechnet.
- Ablauf (konzeptionell):
    1. Anfrage/Funktionsaufruf (z. B. `get_current_manoeuvre()`),
    2. Funktion liest die relevanten Zustandswerte (und bei Bedarf einen kompakten Verlauf) aus,
    3. logische Auswertung: „Was macht das System gerade?“ (Start, Steigflug, Reise, Kurve, Landung, Idle, Crash etc.),
    4. Rückgabe eines klar definierten, typisierten Ergebnisses (`Enum`/`str`/`Literal`).
- Die Auswertung darf die laufende Simulation nicht blockieren und soll die Physik-/Simulationsschleife nicht stören (
  lesen statt schreiben, möglichst ohne Locking-Hölle).
- Lange, fehleranfällige `if-else`-Ketten oder Switch-Monolithen sind zu vermeiden. Stattdessen sollen datengetriebene,
  dynamische oder tabellenbasierte Ansätze genutzt werden (z. B. Mapping von Zustandsbereichen auf Manöver-Typen,
  Strategie-/State-Pattern o. Ä.).

---

## 2. Saubere Schichten-Trennung (Domäne, I/O, Visualisierung, Cache, Physik)

Es ist strikt zu trennen zwischen:

- Domänenlogik / Kernlogik (Simulation, Physik, Zustandsmodelle),
- I/O, UI und Frameworks (CLI, PyQt, Tkinter, Logging-Konfiguration, Persistence, Netzwerkzugriffe),
- Visualisierung (Rendern, Plotten, GUI-Komponenten),
- Caching/Verlaufsverwaltung (History, Trajektorien, Messreihen).

Weitere Vorgaben:

- Das zentrale Simulationsobjekt (z. B. „Ufo“, „SimulationEngine“) bündelt nur die fachliche Logik und den aktuellen
  Zustand, nicht die GUI oder das Rendering.
- Visualisierungen werden über klar definierte Schnittstellen angebunden und müssen so gestaltet sein, dass das System
  headless (ohne GUI) lauffähig bleibt.

---

## 3. Caching und Zustandsverlauf

- Änderungen des Zustands (Position, Geschwindigkeit, Manöver, Statusflags etc.) sollen – wenn ein Verlauf benötigt
  wird – in einem dedizierten Cache/History-Modul gespeichert werden.
- Das Caching sollte ereignis- oder änderungsgetrieben erfolgen (z. B. bei signifikanten Änderungen oder
  Simulations-Ticks), nicht über komplexe, manuell gepflegte Zusatzlogik.

Verantwortlichkeiten:

- Abfragen des aktuellen Zustands (z. B. aktuelle Position, aktuelle Geschwindigkeit, aktuelles Manöver) gehen an das
  Simulationsobjekt selbst.
- Abfragen des Verlaufs (Trajektorie, Zeitreihen, Historie von Manövern) gehen an den Cache/History-Manager.
- Der Cache folgt denselben Architekturregeln wie andere Komponenten (klare Schnittstelle, testbar, keine UI-Logik).

---

## 4. Visualisierung und Anzeige

Jede Visualisierung (GUI, Plot, Konsole, Live-View) muss die grundlegenden Architekturvorgaben einhalten:

- Trennung zwischen Daten (Zustand/History) und Darstellung,
- keine Vermischung von Rendering und Simulationslogik,
- austauschbare Darstellungsvarianten (z. B. einfache Konsole vs. PyQt-Fenster), ohne die Kern-API zu brechen.

Weitere Anforderungen:

- Die Anzeige muss fachlich korrekt sein und das tatsächliche Simulationsverhalten plausibel widerspiegeln.
- Es muss möglich sein, die Simulation vollständig ohne Visualisierung (headless) zu betreiben; Visualisierung darf nur
  ein optionales Add-on sein.

---

## A5. Testbarkeit und Testvorbereitung

- Der Code ist von Anfang an so zu strukturieren, dass Unit-Tests und Black-Box-Tests einfach ergänzt werden können.

Voraussetzungen:

- Kernlogik ist in separaten, frameworkfreien Modulen gekapselt.
- Zustände sind über klare APIs lesbar und manipulierbar.
- Es gibt keine harten Abhängigkeiten auf GUI, Netzwerk oder Dateien innerhalb der Domänenschicht.
- Projektseitig sollen die nötigen Testwerkzeuge vorbereitet werden (z. B. `pytest`-Struktur, `tests/`-Ordner,
  Basis-Konfiguration), sodass später nur noch Testfälle ergänzt werden müssen.

---

## 6. Entry-Points, „main“ und Demo-Läufe

- Bibliotheks- und Kernmodule enthalten keine umfangreiche `main`-Logik.

Stattdessen gilt:

- Kernmodule stellen nur Klassen, Funktionen und Konfigurationen bereit.
- Für manuelle Tests oder Demos kann ein separater Entry-Point (z. B. `*_main.py`) angelegt werden, der:
    - eine Simulation instanziiert,
    - Beispiel-Konfigurationen lädt,
    - ggf. Beispiel-Aufrufe (auch zuvor auskommentierte) ausführt,
    - aber keine zusätzliche Fachlogik enthält.
- Dieser Entry-Point ist klar von der eigentlichen Bibliothek getrennt und kann jederzeit entfernt oder ersetzt werden,
  ohne die Kernlogik zu beeinflussen.

---

## A7. Aufräumen und Reduktion auf notwendige Artefakte

- Im Projektverzeichnis sollen nur tatsächlich genutzte Dateien verbleiben.
- Veraltete, nicht mehr verwendete Versionen, Experimente oder Duplikate sind:
    - zu entfernen, oder
    - klar als Legacy/Archiv zu kennzeichnen (z. B. separater `legacy/`-Ordner), wenn sie noch als Referenz dienen.
- Spezialfall: Autopilot-/Strategie-Implementierungen dürfen als separate Modulgruppe bestehen bleiben, solange sie eine
  klare, dokumentierte Schnittstelle nutzen.

---

## 8. Nutzung und Bewertung älterer Implementierungen

- Frühere Implementierungen (z. B. schlankere Versionen mit mehr dynamischer Erkennung, weniger statischen Variablen)
  dürfen als Inspirationsquelle dienen.

Ziel ist, sinnvolle Ansätze zu übernehmen, z. B.:

- Reduktion von Magic Numbers,
- dynamische Ableitung von Zuständen statt starrer Flags,
- kompakter, gut strukturierter Code.

Voraussetzung für jede Übernahme:

- fachliche Korrektheit bleibt gewahrt,
- Visualisierung und externe APIs funktionieren unverändert,
- der Code erfüllt alle nachfolgenden allgemeinen Richtlinien (Abschnitt B).

---

## 9. Didaktische Basisklassen

Basisklassen, die in schulischen/ausbildungsbezogenen Kontexten genutzt werden (z. B. Simulationsgrundlagen für eigene
Autopiloten), erfüllen folgende Anforderungen:

1. Realitätsnahe, aber nicht übermäßig komplexe Physik und Logik – bewusst vereinfachtes, aber plausibles Modell.
2. Erweiterte Features (z. B. dynamische Geschwindigkeitsanpassung in Kurven, komplexe Sensorik) sind optional und
   können in Fortgeschrittenen-Versionen ergänzt werden.
3. Grundlegende physikalische Konsistenz (korrekte Einheiten, plausible Bewegungen) ist zwingend, aber nicht jede
   realweltliche Feinheit muss abgebildet sein.
4. Die Basisklasse dient explizit als stabile Grundlage für Experimente, eigene Autopiloten und Lernprojekte.
5. Die Struktur bleibt übersichtlich, robust und gut dokumentiert, damit spätere Erweiterungen (z. B. komplexere
   Modelle) möglich sind, ohne den Einstieg unnötig zu erschweren.

---
