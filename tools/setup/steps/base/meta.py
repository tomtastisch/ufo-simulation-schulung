# tools/setup/steps/base/meta.py
from __future__ import annotations

import re
from abc import ABCMeta, ABC
from dataclasses import dataclass
from typing import Any, ClassVar, NoReturn

from tools.setup.domain import BootstrapConfig, PyProjectProfile
from tools.setup.logging import ErrorLog
from tools.setup.ui import SetupConsole

_STID_PATTERN = re.compile(r"^[a-z0-9_]+$")


@dataclass(slots=True)
class BaseStepContext:
    config: BootstrapConfig
    profile: PyProjectProfile
    console: SetupConsole
    log: ErrorLog


class BaseStepCore(ABC):
    """Minimale gemeinsame Basis für alle Steps, nur für Typen/Registry."""
    stid: ClassVar[str]
    prio: ClassVar[int]


class BaseStepMeta(ABCMeta):
    """
    Metaklasse für Setup-Steps.

    Validiert:
    - stid existiert und ist ein String
    - stid erfüllt das Pattern [a-z0-9_]+
    - stid ist über alle Steps eindeutig
    """

    _registry: dict[str, type[Any]] = {}

    @staticmethod
    def throw(
            name: str,
            stid: object,
            reason: str | None = None,
            obj: str | None = None,
            exc: type[Exception] = ValueError,
    ) -> NoReturn:
        msg = "Step {name} mit stid {id} ist ungültig{reason}{obj}.".format(
            name=name,
            id=stid,
            reason=f", weil diese {reason}" if reason else "",
            obj=f" [{obj}]" if obj else "",
        )
        raise exc(msg)


    def __init__(
            cls,
            name: str,
            bases: tuple[type, ...],
            namespace: dict[str, Any],
            **kwargs: Any,  # type: ignore[override]
    ) -> None:
        super().__init__(name, bases, namespace, **kwargs)

        # Basis-Klasse selbst nicht validieren
        if name == "BaseStep":
            return

        registry = BaseStepMeta._registry

        # dataclass(slots=True)-Sonderfall: Klasse wird neu erzeugt
        for existing_stid, existing_cls in list(registry.items()):
            if (
                    existing_cls.__name__ == cls.__name__
                    and existing_cls.__module__ == cls.__module__
                    and existing_cls is not cls
            ):
                registry[existing_stid] = cls
                return

        stid = getattr(cls, "stid", None)

        rsn: str = ""
        obj: str = ""
        err: type[Exception] | None = None

        if not isinstance(stid, str) or not stid:
            rsn = "leer ist"
            obj = "BaseStep.stid"
            err = TypeError
        else:
            if not _STID_PATTERN.fullmatch(stid):
                rsn = f"nicht dem Pattern {_STID_PATTERN.pattern} entspricht"
                obj = f"BaseStep.stid={stid!r}"
                err = ValueError
            elif stid in registry and registry[stid] is not cls:
                rsn = "bereits genutzt wird"
                obj = registry[stid].__name__
                err = ValueError

        if err is not None:
            BaseStepMeta.throw(
                name=name,
                stid=stid,
                reason=rsn,
                obj=obj,
                exc=err,
            )

        registry[stid] = cls

    @classmethod
    def registry(mcls) -> dict[str, type[Any]]:
        """Optionale Debug-API, falls du die registrierten Steps inspizieren willst."""
        return dict(mcls._registry)