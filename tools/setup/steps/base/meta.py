# tools/setup/steps/base/meta.py
from __future__ import annotations

import re
from abc import ABCMeta
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from tools.setup.domain import BootstrapConfig, PyProjectProfile
from tools.setup.logging import ErrorLog
from tools.setup.ui import SetupConsole

if TYPE_CHECKING:
    # Nur für Typprüfer; zur Laufzeit kein Import → kein Zirkel.
    from tools.setup.steps.base import BaseStep

_STID_PATTERN = re.compile(r"^[a-z0-9_]+$")


@dataclass(slots=True)
class StepContext:
    """
    Gemeinsamer Ausführungskontext für Setup-Schritte.
    """

    config: BootstrapConfig
    profile: PyProjectProfile
    console: SetupConsole
    log: ErrorLog


class BaseStepMeta(ABCMeta):
    """
    Metaklasse für Setup-Steps.

    Validiert:
    - stid existiert und ist ein String
    - stid erfüllt das Pattern [a-z0-9_]+
    - stid ist über alle Steps eindeutig
    """

    # Für Debug/Inspektion reicht ein „breiter“ Typ:
    _registry: dict[str, type[Any]] = {}

    def __init__(
            cls,
            name: str,
            bases: tuple[type, ...],
            namespace: dict[str, Any],
            **kwargs: Any,  # type: ignore[override]
    ) -> None:
        # WICHTIG: keine @dataclass-Dekoration auf der Metaklasse selbst,
        # damit super().__init__ sauber den ABCMeta/type-MRO-Pfad nutzt.
        super().__init__(name, bases, namespace, **kwargs)

        # Basis-Klasse selbst nicht validieren
        if name == "BaseStep":
            return

        registry = BaseStepMeta._registry

        # ------------------------------------------------------------
        # Sonderfall: dataclass(slots=True) erzeugt Klasse intern neu.
        # Beim zweiten Aufruf kommt eine Klasse mit gleichem Namen und
        # Modul, aber die Attribute (z.B. stid) sind bereits Deskriptoren.
        # -> In diesem Fall NICHT neu validieren, sondern die bereits
        #    registrierte Klasse durch die neue ersetzen.
        # ------------------------------------------------------------
        for existing_stid, existing_cls in list(registry.items()):
            if (
                    existing_cls.__name__ == cls.__name__
                    and existing_cls.__module__ == cls.__module__
                    and existing_cls is not cls
            ):
                registry[existing_stid] = cls
                return

        # Normalfall: erste Definition dieser Step-Klasse
        stid = getattr(cls, "stid", None)

        if not isinstance(stid, str) or not _STID_PATTERN.fullmatch(stid):
            raise ValueError(
                f"Step {name} hat eine ungültige stid {stid!r} – "
                "erlaubt sind nur Kleinbuchstaben, Ziffern und Unterstrich."
            )

        if stid in registry and registry[stid] is not cls:
            other = registry[stid].__name__
            raise ValueError(
                f"Step {name} verwendet stid {stid!r}, "
                f"die bereits von {other} genutzt wird."
            )

        registry[stid] = cls  # type: ignore[assignment]

    @classmethod
    def registry(mcls) -> dict[str, type[Any]]:
        """Optionale Debug-API, falls du die registrierten Steps inspizieren willst."""
        return dict(mcls._registry)
