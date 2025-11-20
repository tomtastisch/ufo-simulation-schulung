# Schulungsablauf – UFO-Simulation

Übersicht über den kompletten Schulungsablauf von der Einführung bis zur eigenständigen Autopilot-Programmierung.

---

## Zielgruppe

Schüler mit Grundkenntnissen in Python, die praktisch lernen möchten:

- **Programmierung** anhand realistischer Szenarien
- **Physik** durch 3D-Vektorrechnung
- **Clean Architecture** durch modularen Code
- **Testing** durch automatisierte Tests

---

## Voraussetzungen

### Technische Voraussetzungen

- **Python 3.11+** installiert
- **Internet** für Package-Installation
- **IDE** (empfohlen: PyCharm, VS Code)
- **Git** für Versionskontrolle (optional)

### Vorwissen

- Python-Grundlagen (Variablen, Funktionen, Klassen)
- Grundlegende Mathematik (Vektoren, Trigonometrie)
- Terminal/Kommandozeilen-Grundlagen

---

## Schulungsablauf

### Phase 1: Projekt-Setup (30 Minuten)

**Ziel**: Projekt einrichten und lauffähig machen

**Schritte**:

1. Repository klonen oder Download
2. Setup ausführen: `python setup.py`
3. Virtual Environment aktivieren
4. Demo starten: `python -m core.simulation.ufo_main`

**Lernziele**:

- Virtual Environments verstehen
- Dependency-Management
- Projekt-Struktur kennenlernen

**Dokumentation**: [setup-anleitung.md](setup-anleitung.md)

---

### Phase 2: Simulation verstehen (1 Stunde)

**Ziel**: Verstehen wie die Simulation funktioniert

**Themen**:

- **3D-Koordinatensystem**: x, y, z-Achsen
- **Physikalische Größen**: Position, Geschwindigkeit, Beschleunigung
- **Steuerung**: Schub, Rotation
- **Phasen**: Start, Reiseflug, Landung

**Aktivitäten**:

1. Demo-Autopilot beobachten
2. Simulation pausieren/fortsetzen
3. Parameter in GUI ändern
4. Crash provozieren (verstehen was schief geht)

**Lernziele**:

- Physik-Simulation verstehen
- GUI-Bedienung
- Debug-Ausgaben lesen

---

### Phase 3: Erster eigener Code (2 Stunden)

**Ziel**: Einfache Autopilot-Funktionen schreiben

**Aufgaben**:

#### Aufgabe 1: Vertikaler Start

```python
def takeoff(ufo_state):
    """Lasse das UFO vertikal starten."""
    return Command(CommandType.THRUST, vertical_thrust=1.0)
```

**Lernziele**:

- Command-Pattern verstehen
- Schub-Steuerung
- Return-Werte

#### Aufgabe 2: Ziel ansteuern

```python
def cruise(ufo_state, destination):
    """Fliege zum Ziel."""
    # Berechne Richtung zum Ziel
    # Rotiere UFO in Richtung
    # Gib Schub
```

**Lernziele**:

- Vektor-Berechnung
- Winkel-Berechnung
- Rotation-Steuerung

#### Aufgabe 3: Sanfte Landung

```python
def landing(ufo_state):
    """Lande sanft."""
    # Prüfe Höhe
    # Reduziere Geschwindigkeit
    # Sanft aufsetzen
```

**Lernziele**:

- Geschwindigkeits-Kontrolle
- Verzögerung berechnen
- Crash vermeiden

**Dokumentation**: Aufgaben-Dokumente (folgen)

---

### Phase 4: Fortgeschrittene Themen (3 Stunden)

**Ziel**: Komplexe Autopilot-Logik implementieren

**Themen**:

#### 4.1 Winkelberechnung

- Winkel zwischen Vektoren
- Richtungs-Korrektur
- Drehgeschwindigkeit

#### 4.2 Geschwindigkeits-Kontrolle

- PID-Regler (vereinfacht)
- Schub-Berechnung
- Brems-Manöver

#### 4.3 Höhen-Management

- Höhen-Profil planen
- Steig-/Sinkraten
- Sicherheits-Abstände

#### 4.4 State-Management

- Phasen-Erkennung
- Zustandsübergänge
- Fehler-Behandlung

**Lernziele**:

- Komplexe Algorithmen
- Fehler-Behandlung
- Edge-Cases

---

### Phase 5: Testing & Debugging (1 Stunde)

**Ziel**: Code testen und debuggen

**Aktivitäten**:

1. Unit-Tests schreiben
2. Edge-Cases testen
3. Debugging mit Print-Statements
4. Logging nutzen

**Lernziele**:

- Test-Driven Development
- Debugging-Strategien
- Logging best practices

---

### Phase 6: Optimierung & Erweiterung (2 Stunden)

**Ziel**: Code verbessern und erweitern

**Themen**:

- Code-Refactoring
- Performance-Optimierung
- Neue Features (z.B. Hindernisse)
- Dokumentation schreiben

**Lernziele**:

- Clean Code Prinzipien
- Performanz-Analyse
- Feature-Entwicklung

---

## Zeitplan (Beispiel)

### Tag 1 (4 Stunden)

- **09:00-09:30**: Einführung & Setup (Phase 1)
- **09:30-10:30**: Simulation verstehen (Phase 2)
- **10:30-12:30**: Erste Aufgaben (Phase 3, Aufgabe 1-2)

### Tag 2 (4 Stunden)

- **09:00-10:00**: Aufgabe 3 abschließen (Phase 3)
- **10:00-13:00**: Fortgeschrittene Themen (Phase 4)

### Tag 3 (3 Stunden)

- **09:00-10:00**: Testing (Phase 5)
- **10:00-12:00**: Optimierung (Phase 6)
- **12:00-13:00**: Präsentation & Abschluss

---

## Lernziel-Katalog

Nach Abschluss der Schulung können Schüler:

### Programmierung

- ✓ Python-Funktionen mit Type Hints schreiben
- ✓ Command-Pattern anwenden
- ✓ State-Management implementieren
- ✓ Fehlerbehandlung umsetzen

### Mathematik/Physik

- ✓ 3D-Vektoren berechnen
- ✓ Winkel zwischen Vektoren bestimmen
- ✓ Physikalische Größen (v, a, F) verstehen
- ✓ Bewegungsgleichungen anwenden

### Software-Engineering

- ✓ Clean Architecture Prinzipien
- ✓ Unit-Tests schreiben
- ✓ Code dokumentieren
- ✓ Debugging-Strategien

### Tools

- ✓ Virtual Environments nutzen
- ✓ Git Basics (optional)
- ✓ IDE effektiv nutzen
- ✓ pytest für Testing

---

## Bewertungs-Kriterien (Optional)

Falls Bewertung gewünscht:

### Funktionalität (40%)

- Start funktioniert
- Ziel wird erreicht
- Landung erfolgreich
- Keine Crashes

### Code-Qualität (30%)

- Lesbarkeit
- Dokumentation
- Type Hints
- Fehlerbehandlung

### Mathematik (20%)

- Korrekte Berechnungen
- Winkel richtig
- Geschwindigkeit kontrolliert

### Tests (10%)

- Unit-Tests vorhanden
- Edge-Cases abgedeckt
- Tests passieren

---

## Tipps für Lehrer

### Vorbereitung

1. Setup selbst durchlaufen
2. Alle Aufgaben selbst lösen
3. Häufige Fehler identifizieren
4. Hilfestellungen vorbereiten

### Während der Schulung

1. Live-Coding Sessions
2. Pair Programming fördern
3. Regelmäßige Code-Reviews
4. Debugging gemeinsam

### Nach der Schulung

1. Code der Schüler reviewen
2. Feedback geben
3. Best Practices zeigen
4. Weiterführende Themen vorschlagen

---

## Weiterführende Themen

Nach Abschluss der Schulung:

- **Erweiterte Physik**: Luftwiderstand, Wind
- **Mehrere UFOs**: Formation flying
- **Hindernisse**: Kollisions-Vermeidung
- **GUI-Entwicklung**: Eigene Controls
- **Netzwerk**: Multiplayer
- **AI**: Machine Learning für Autopilot

---

## Ressourcen

### Dokumentation

- [Setup-Anleitung](setup-anleitung.md)
- [Architektur-Spezifikationen](../specs/architecture/)
- [Coding-Guidelines](../guidelines/general-gd.md)

### Externe Links

- [Python Tutorial](https://docs.python.org/3/tutorial/)
- [NumPy Tutorial](https://numpy.org/doc/stable/user/quickstart.html)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)

### Troubleshooting

- [Setup-Probleme](setup-anleitung.md#probleme-beheben)
- [Testing-Tools](../dev/testing-tools.md)
- [Setup-System](../dev/setup-system.md)

---

**Viel Erfolg bei der Schulung! 🚀**

