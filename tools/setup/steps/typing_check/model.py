# tools/setup/steps/typing_check/model.py
from __future__ import annotations

"""
Datenmodelle für den Type Annotation Checker.

Enthält TypeAnnotation für einzelne Findings (fehlende Annotationen).
"""

from dataclasses import dataclass


@dataclass(slots=True)
class TypeAnnotation:
    """
    Einzelner Befund zu einer fehlenden Typannotation.

    Attributes:
        file: Relative Dateipfad
        line: Zeilennummer
        name: Name des Elements (Parameter, Funktion, Variable)
        type: Art des Elements ("parameter", "return", "variable")
    """

    file: str
    line: int
    name: str
    type: str  # "parameter", "return", "variable"
