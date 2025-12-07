"""
Utilities für Task-ID und Display-Name Generierung.

Diese Funktionen werden von TaskList verwendet, um aus beliebigen
Objekten stabile IDs und lesbare Namen zu erzeugen.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def build_task_id(obj: Any) -> str:
    """
    Erzeugt eine eindeutige, stabile Task-ID aus einem Objekt.

    Die ID muss deterministisch sein: für dasselbe Objekt immer dieselbe ID.

    Strategien:
    - Hat obj ein 'task_id' Attribut → direkt verwenden
    - Hat obj einen 'file_relpath' → normalisiert als ID
    - Ist obj ein Path → normalisiert als String
    - Ist obj ein String → direkt als ID
    - Sonst: repr(obj)

    Args:
        obj: Das Objekt, für das eine Task-ID erzeugt werden soll

    Returns:
        Eindeutige, stabile Task-ID als String

    Beispiel:
        >>> build_task_id(TestFile("tests/core/test_foo.py", [...]))
        'tests/core/test_foo.py'
    """
    # Explizites task_id Attribut
    if hasattr(obj, "task_id"):
        return str(obj.task_id)

    # file_relpath (häufig bei Test-/File-Objekten)
    if hasattr(obj, "file_relpath"):
        path = Path(obj.file_relpath)
        return path.as_posix()

    # Path-Objekt
    if isinstance(obj, Path):
        return obj.as_posix()

    # String direkt
    if isinstance(obj, str):
        return obj

    # Fallback: repr
    return repr(obj)


def build_display_name(obj: Any) -> str:
    """
    Erzeugt einen menschenlesbaren, stabilen Namen für die UI.

    Strategien:
    - Hat obj ein 'display_name' Attribut → direkt verwenden
    - Hat obj einen 'file_relpath' → nur Dateiname (letztes Segment)
    - Ist obj ein Path → nur Dateiname
    - Ist obj ein String → Dateiname, falls Pfad-ähnlich
    - Sonst: str(obj)

    Args:
        obj: Das Objekt, für das ein Display-Name erzeugt werden soll

    Returns:
        Menschenlesbarer Name als String

    Beispiel:
        >>> build_display_name(TestFile("tests/core/test_foo.py", [...]))
        'test_foo.py'
    """
    # Explizites display_name Attribut
    if hasattr(obj, "display_name"):
        return str(obj.display_name)

    # file_relpath → nur Dateiname
    if hasattr(obj, "file_relpath"):
        path = Path(obj.file_relpath)
        return path.name

    # Path-Objekt → nur Dateiname
    if isinstance(obj, Path):
        return obj.name

    # String → versuche als Pfad zu interpretieren
    if isinstance(obj, str):
        if "/" in obj or "\\" in obj:
            return Path(obj).name
        return obj

    # Fallback: str
    return str(obj)
