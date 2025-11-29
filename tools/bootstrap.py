# tools/bootstrap.py
from __future__ import annotations

import sys
from dataclasses import dataclass, fields
from typing import Iterable

from tools.setup.domain import BootstrapConfig, build_profile
from tools.setup.domain import PyProjectProfile
from tools.setup.logging import ErrorLog
from tools.setup.steps import BaseStep  # nur für Typ-Hints
from tools.setup.steps.base import BaseStepContext
from tools.setup.ui import SetupConsole
from tools.setup.ui.resources import CATALOG


# ------------------------------------------------------------
# 1) SETUP HEADER AUFBAUEN
# ------------------------------------------------------------

@dataclass(slots=True)
class Segment:
    license: str
    title: str
    intro: str
    body: str

    def __iter__(self) -> Iterable[str]:
        return (getattr(self, f.name) for f in fields(self))

    @classmethod
    def from_catalog(cls, cat=CATALOG) -> "Segment":
        return cls(
            **{
                f.name: cat.text("setup_header", field=f.name, default="")
                for f in fields(cls)
            }
        )


# ------------------------------------------------------------
# 2) Low-Level-Utility-Funktionen
# ------------------------------------------------------------

def _build_log(config: BootstrapConfig) -> ErrorLog:
    """Bereitet das ErrorLog vor (leert bestehende Datei)."""
    path = config.log_path
    path.write_text("", encoding="utf-8")
    return ErrorLog(path)


def _select_steps(profile: PyProjectProfile) -> tuple[type[BaseStep[object]], ...]:
    """
    Wählt die auszuführenden Steps ausschließlich auf Basis ihrer ``stid``
    und der Konfiguration aus [tool.setup].
    """
    from tools.setup.steps import STEPS  # tatsächliche Klassen

    by_stid: dict[str, type[BaseStep[object]]] = {}
    for cls in STEPS:
        stid = cls.stid
        if stid in by_stid and by_stid[stid] is not cls:
            other = by_stid[stid].__name__
            raise ValueError(
                f"Doppelte stid {stid!r} bei {cls.__name__} und {other}.",
            )
        by_stid[stid] = cls

    if profile.step_include:
        ordered_ids = [stid for stid in profile.step_include if stid in by_stid]

    else:
        ordered_ids = [
            cls.stid
            for cls in sorted(by_stid.values(), key=lambda c: c.priority, reverse=True)
        ]

    exclude_ids = set(profile.step_exclude)
    return tuple(
        by_stid[stid]
        for stid in ordered_ids
        if stid not in exclude_ids
    )


# ------------------------------------------------------------
# 3) Step-Orchestrierung
# ------------------------------------------------------------

def leaf(ctx: BaseStepContext) -> bool:
    """
    Führt alle konfigurierten Setup-Schritte aus und bricht nach dem
    ersten fehlgeschlagenen Step ab.
    """
    process = (cls() for cls in _select_steps(ctx.profile))
    return all((ok := step.run(ctx)) for step in process)


# ------------------------------------------------------------
# 4) High-Level-Orchestrator
# ------------------------------------------------------------

def execute(argv: list[str] | None = None) -> int:
    """
    Führt den kompletten Setup-Prozess aus:

    - Config, Profile, Log, Konsole erzeugen
    - Header anzeigen
    - Steps via leaf(ctx) ausführen
    - ggf. Next-Steps anzeigen

    CLI-Argumente (argv) werden bewusst ignoriert; das Verhalten
    wird ausschließlich über die pyproject.toml gesteuert.
    """
    config = BootstrapConfig()
    profile = build_profile(config.repo_root)
    log = _build_log(config)

    console = SetupConsole()
    ctx = BaseStepContext(
        config=config,
        profile=profile,
        log=log,
        console=console,
    )

    seg = Segment.from_catalog(CATALOG)
    if seg.license:
        console.info(seg.license)
    if seg.title:
        console.header(seg.title)
    for part in (seg.intro, seg.body):
        if part:
            console.info(part)

    ok = leaf(ctx)

    if ok:
        title = CATALOG.text("next", field="title", default="")
        body = CATALOG.text("next", field="body", default="").format(
            activate_cmd=config.activation_command,
        )
        if title:
            console.info(title)
        if body:
            console.info(body)

    return 0 if ok else 1


def console_script() -> None:
    """Entry-Point für pyproject.toml / setup_new.py."""
    raise SystemExit(execute(sys.argv[1:]))
