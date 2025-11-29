# tools/setup/steps/base/result.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

V = TypeVar("V", covariant=True)


@dataclass(slots=True)
class _BaseResult:
    """
    Standardisiertes Ergebnis von Einheiten
    innerhalb eines Arneitsschrittes.

    - ok         → fachliches Ergebnis
    - cause      → technischer Grund (Error-Code / Kategorie)
    - details    → Rohdetails (z. B. CLI-Output, Traceback-Auszug)
    - label      → für Progress/Statusanzeige (Testname, Paketname, Contract)
    """
    ok: bool
    cause: str = ""
    details: str = ""
    error_hint: str = ""


@dataclass(slots=True)
class PrepareResult(_BaseResult, Generic[V]):
    """Ergebnis eines prepare(...)-Aufrufs."""

    payload: V | object = object()


@dataclass(slots=True)
class StepResult(_BaseResult):
    """Standardisiertes Ergebnis eines Steps."""
    label: str = ""
