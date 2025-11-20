#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility-Modul für generische, wiederverwendbare Hilfsfunktionen.

Modulzweck
----------
Dieses Modul stellt generische Utility-Funktionen bereit, die keine Abhängigkeiten
zu Simulation-spezifischen Typen haben und projektübergreifend einsetzbar sind.
Es kapselt häufig benötigte mathematische und numerische Operationen in einer
zentralen, gut getesteten Form.

Strukturelle Verantwortlichkeiten
----------------------------------
Das Utils-Modul folgt strikten Architektur-Prinzipien:

1. **Keine Simulationslogik-Abhängigkeiten**: Keine Imports von SimulationConfig,
   UfoState, UfoSim, StateManager oder anderen simulationsspezifischen Klassen.
   Nur Standardbibliothek (math, typing) als Dependencies.

2. **Reine Funktionen**: Alle Funktionen sind zustandslos, haben keine
   Seiteneffekte und sind deterministisch testbar.

3. **Generische Wiederverwendbarkeit**: Funktionen sind so allgemein gehalten,
   dass sie in beliebigen Python-Projekten verwendet werden können.

4. **Vollständige Typisierung**: Alle Parameter und Rückgabewerte sind mit
   Type Hints versehen für statische Analyse und IDE-Unterstützung.

Modul-Bestandteile
------------------
maths.py:
    Numerische Hilfsfunktionen für mathematische Operationen:
    - Trigonometrische Konvertierungen (Grad ↔ Radiant)
    - Winkel-Normalisierung (wrap_angle_deg, wrap_angle_rad)
    - Wert-Begrenzung (clamp)

validation.py:
    Validierungsfunktionen für Wertebereichs-Prüfungen:
    - validate_range: Wirft ValueError wenn Wert außerhalb des Bereichs
    - is_in_range: Boolean-Check für Wertebereich

geometry.py:
    Geometrische Transformationsfunktionen für 3D-Koordinaten:
    - cartesian_to_spherical: Kartesisch → Sphärisch (x,y,z → r,θ,φ)
    - spherical_to_cartesian: Sphärisch → Kartesisch (r,θ,φ → x,y,z)

Öffentliche API
---------------
**Mathematische Funktionen (maths.py):**

deg_to_rad(degrees):
    Konvertiert Winkel von Grad zu Radiant mit math.radians.

rad_to_deg(radians):
    Konvertiert Winkel von Radiant zu Grad mit math.degrees.

wrap_angle_deg(angle, lower=-180.0, upper=180.0):
    Normalisiert Winkel in Grad auf periodischen Bereich [lower, upper).
    Standard-Normalisierung auf [-180°, 180°).

wrap_angle_rad(angle):
    Normalisiert Winkel in Radiant auf [-π, π).

clamp(value, min_value, max_value):
    Begrenzt Wert auf Bereich [min_value, max_value].
    Validiert min_value <= max_value.

**Validierungsfunktionen (validation.py):**

validate_range(value, min_val, max_val, name):
    Validiert Wertebereich, wirft ValueError bei Verletzung.

is_in_range(value, min_val, max_val):
    Prüft ob Wert in Bereich liegt (Boolean).

**Geometrische Transformationen (geometry.py):**

cartesian_to_spherical(x, y, z):
    Konvertiert kartesische zu sphärischen Koordinaten (r, θ, φ).

spherical_to_cartesian(r, theta, phi):
    Konvertiert sphärische zu kartesischen Koordinaten (x, y, z).

Verwendungsbeispiele
--------------------
Trigonometrische Konvertierung:
    >>> from core.simulation.utils.maths import deg_to_rad, rad_to_deg
    >>> import math
    >>>
    >>> # Grad zu Radiant
    >>> angle_rad = deg_to_rad(180.0)  # π
    >>> abs(angle_rad - math.pi) < 1e-10
    True
    >>>
    >>> # Radiant zu Grad (Roundtrip)
    >>> angle_deg = rad_to_deg(angle_rad)  # 180.0
    >>> abs(angle_deg - 180.0) < 1e-10
    True

Winkel-Normalisierung:
    >>> from core.simulation.utils.maths import wrap_angle_deg, wrap_angle_rad
    >>>
    >>> # Heading über 360°-Grenze normalisieren
    >>> heading = wrap_angle_deg(370.0, 0.0, 360.0)  # 10.0
    >>>
    >>> # Standard-Normalisierung auf [-180°, 180°)
    >>> angle = wrap_angle_deg(190.0)  # -170.0
    >>>
    >>> # Radiant-Normalisierung
    >>> angle_rad = wrap_angle_rad(3.5 * math.pi)  # -0.5π

Wert-Begrenzung:
    >>> from core.simulation.utils.maths import clamp
    >>>
    >>> # Geschwindigkeit auf zulässigen Bereich begrenzen
    >>> velocity = clamp(150.0, 0.0, 100.0)  # 100.0
    >>>
    >>> # Neigungswinkel clampen
    >>> inclination = clamp(-95.0, -90.0, 90.0)  # -90.0

Integration in Simulation:
    >>> from core.simulation.utils.maths import wrap_angle_deg, clamp
    >>>
    >>> # Physik-Engine: Geschwindigkeit begrenzen (Pseudocode)
    >>> # new_velocity = calculate_velocity(...)
    >>> # clamped_v = clamp(new_velocity, 0.0, vmax_kmh)
    >>>
    >>> # Observer: Heading-Delta über 360°-Grenze berechnen
    >>> heading1 = wrap_angle_deg(350.0, 0.0, 360.0)  # 350.0
    >>> heading2 = wrap_angle_deg(10.0, 0.0, 360.0)   # 10.0
    >>> delta = heading2 - heading1                   # -340.0 (falsch!)
    >>> # Besser: Auf [-180°, 180°) normalisieren
    >>> norm1 = wrap_angle_deg(heading1)  # -10.0
    >>> norm2 = wrap_angle_deg(heading2)  # 10.0
    >>> delta = norm2 - norm1             # 20.0 (korrekt!)

Architektur-Prinzipien
----------------------
- Keine Abhängigkeiten zu Simulationslogik
- Reine Funktionen ohne Zustand oder Seiteneffekte
- Vollständige Type Hints und Docstrings
- Physikalisch/mathematisch korrekte Implementierungen
- 100% deterministisch testbar
- Generisch wiederverwendbar in beliebigen Projekten
"""

from .geometry import (
    cartesian_to_spherical,
    spherical_to_cartesian,
)
from .maths import (
    clamp,
    deg_to_rad,
    rad_to_deg,
    wrap_angle_deg,
    wrap_angle_rad,
)
from .validation import (
    is_in_range,
    validate_range,
)

__all__ = [
    # maths
    "clamp",
    "deg_to_rad",
    "rad_to_deg",
    "wrap_angle_deg",
    "wrap_angle_rad",
    # validation
    "is_in_range",
    "validate_range",
    # geometry
    "cartesian_to_spherical",
    "spherical_to_cartesian",
]
