"""
Physik-Engine für UFO-Simulation.

Dieses Paket enthält die physikalische Integrationslogik der UFO-Simulation.
Es ist verantwortlich für die Berechnung von Bewegungen, Beschleunigungen und
Landungsbedingungen basierend auf dem aktuellen Zustand und der Konfiguration.

=== ZWECK ===

Das physics-Paket kapselt die gesamte physikalische Berechnungslogik der Simulation
und hält sie unabhängig von Threading-Concerns, Zustandsverwaltung und UI-Komponenten.

=== BESTANDTEILE ===

**engine.py - PhysicsEngine:**
- Hauptklasse für physikalische Integrationsschritte
- Zeitschritt-basierte Integration (dt-basiert)
- 3D-Vektormathematik mit sphärischen Koordinaten
- Physikalische Constraints (Geschwindigkeits- und Beschleunigungsgrenzen)
- Realistische Landungs- und Crash-Kriterien
- Automatische Landungsassistenz

=== VERANTWORTLICHKEITEN ===

**Was das Paket tut:**
- Physikalische Zustandsübergänge berechnen (Position, Geschwindigkeit, Beschleunigung)
- Physikalische Constraints anwenden (z.B. maximale Geschwindigkeit)
- Landungs- und Crash-Bedingungen prüfen
- Landungsassistenz-Logik bereitstellen
- Bewegungsgleichungen integrieren

**Was das Paket NICHT tut:**
- Thread-Management oder Synchronisation (gehört zu StateManager)
- Zustandsspeicherung oder -verwaltung (gehört zu StateManager)
- Command-Verarbeitung (gehört zu CommandExecutor)
- Manöver-Analyse oder Phasen-Erkennung (gehört zu Observer)
- UI-Darstellung (gehört zu View)

=== ABHÄNGIGKEITEN ===

**Erlaubte Abhängigkeiten:**
- SimulationConfig (Konfigurationsparameter)
- UfoState (Zustandsdatenmodell)
- numpy (Numerische Berechnungen)
- logging (Protokollierung)
- dataclasses (Immutable Updates)
- typing (Type Hints)

**Verbotene Abhängigkeiten:**
- StateManager (höhere Schicht)
- CommandQueue, CommandExecutor (höhere Schicht)
- UfoSim (höhere Schicht)
- View-Komponenten (höhere Schicht)
- Observer-Komponenten (parallele Schicht)

=== STRUKTUR ===

Die PhysicsEngine arbeitet nach dem Prinzip der funktionalen Reinheit:
- Alle Methoden sind zustandslos (stateless)
- State wird nie in-place modifiziert (immutable pattern mit dataclasses.replace)
- Keine Seiteneffekte außer Logging
- Thread-sicher durch externes Locking (StateManager)

=== VERWENDUNG ===

    from core.simulation.physics import PhysicsEngine
    from core.simulation.infrastructure import SimulationConfig
    from core.simulation.state import UfoState
    
    # Engine initialisieren
    config = SimulationConfig()
    engine = PhysicsEngine(config)
    
    # Physik-Schritt ausführen
    state = UfoState()
    new_state, continues, landed = engine.integrate_step(state)

=== QUALITÄTSANFORDERUNGEN ===

- **Korrektheit**: Physikalisch plausible Berechnungen
- **Testbarkeit**: Isoliert testbar ohne externe Abhängigkeiten
- **Performance**: NumPy-optimierte Vektoroperationen
- **Wartbarkeit**: Klare Trennung der Berechnungsschritte
- **Dokumentation**: Vollständige Docstrings für alle öffentlichen Methoden
"""

from .engine import PhysicsEngine

__all__ = ['PhysicsEngine']
