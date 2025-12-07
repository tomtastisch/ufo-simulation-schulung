# tools/bootstrap.py
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Iterable

from tools.setup.domain import BootstrapConfig, build_profile, ConfigResolver
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


# ------------------------------------------------------------
# 2a) CLI Argument Parsing
# ------------------------------------------------------------

def parse_args(argv: list[str] | None) -> argparse.Namespace:
    """
    Parst Command-Line-Argumente.

    Unterstützte Optionen:
    --help: Hilfe anzeigen
    --steps: Komma-separierte Step-IDs die ausgeführt werden sollen
    --skip: Komma-separierte Step-IDs die übersprungen werden sollen
    --verbose, -v: Erhöht Verbosity
    commands: Zusätzliche Befehle nach Setup (noch nicht implementiert)

    Args:
        argv: Liste von Argumenten (sys.argv[1:] wenn None)

    Returns:
        Namespace mit geparsten Argumenten
    """
    parser = argparse.ArgumentParser(
        prog="setup_v2.py",
        description="UFO-Simulation Setup System",
        add_help=False,  # Eigenes Help-Handling
    )

    parser.add_argument(
        "--help",
        action="store_true",
        help="Zeige diese Hilfe",
    )

    parser.add_argument(
        "--steps",
        type=str,
        help="Nur diese Steps ausführen (kommagetrennt)",
    )

    parser.add_argument(
        "--skip",
        type=str,
        help="Diese Steps überspringen (kommagetrennt)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Ausführliche Ausgabe",
    )

    parser.add_argument(
        "commands",
        nargs="*",
        help="Zusätzliche Befehle nach Setup (noch nicht unterstützt)",
    )

    return parser.parse_args(argv or [])


def generate_help_text() -> str:
    """
    Generiert Help-Text aus TOML und Step-Metadaten.

    Returns:
        Formatierter Help-Text
    """
    config_path = Path(__file__).parent / "setup" / "ui" / "resources" / "setup_config.toml"
    try:
        resolver = ConfigResolver.from_defaults(config_path)
        steps_meta = resolver.get_steps_metadata()

        # Steps nach Priorität sortieren
        sorted_steps = sorted(
            steps_meta,
            key=lambda s: s.get("prio", 0),
            reverse=True,
        )

        # Steps-Liste formatieren
        steps_lines = []
        for step in sorted_steps:
            step_id = step.get("id", "unknown")
            desc = step.get("description", "Keine Beschreibung")
            enabled = "✓" if step.get("enabled", True) else "✗"
            steps_lines.append(f"  [{enabled}] {step_id:20s} - {desc}")

        steps_list = "\n".join(steps_lines)

        # Template aus Katalog holen
        template = CATALOG.text(
            "help",
            field="usage",
            default="""
Verwendung:
  python setup_v2.py [OPTIONEN]

Verfügbare Steps:
{steps_list}
""",
        )

        return template.format(steps_list=steps_list)
    except Exception as ex:
        # Fallback: Minimaler Help-Text bei Fehlern (z.B. ValueError durch ungültige TOML)
        fallback_steps = "  [!] Step-Informationen konnten nicht geladen werden (Konfigurationsfehler)."
        fallback_template = (
            "Verwendung:\n"
            "  python setup_v2.py [OPTIONEN]\n\n"
            "Verfügbare Steps:\n"
            f"{fallback_steps}\n"
        )
        return fallback_template
def show_help() -> None:
    """Zeigt Help-Text."""
    title = CATALOG.text("help", field="title", default="UFO-Simulation Setup – Hilfe")
    help_text = generate_help_text()

    print(title)
    print("=" * len(title))
    print(help_text)


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
            for cls in sorted(by_stid.values(), key=lambda c: c.prio, reverse=True)
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
    Führt den kompletten Setup-Prozess aus.

    Ablauf:
    1. Parse CLI-Argumente
    2. Zeige --help falls angefordert
    3. Config, Profile, Log, Konsole erzeugen
    4. ConfigResolver für drei-stufiges Fallback nutzen (commands > pyproject > defaults)
    5. Warnungen für unbekannte Config-Keys anzeigen
    6. Header anzeigen
    7. Steps via leaf(ctx) ausführen
    8. ggf. Next-Steps anzeigen

    Args:
        argv: CLI-Argumente (sys.argv[1:] wenn None)

    Returns:
        0 bei Erfolg, 1 bei Fehler
    """
    # 1. Parse CLI-Argumente
    args = parse_args(argv)

    # 2. --help Handler
    if args.help:
        show_help()
        return 0

    # 3. Config und Profile erstellen
    config = BootstrapConfig()
    profile = build_profile(config.repo_root)
    log = _build_log(config)

    console = SetupConsole()

    # 4. ConfigResolver nutzen für drei-stufiges Fallback
    # NOTE: ConfigResolver currently used only for help generation.
    # Full integration with PyProjectProfile pending in future iteration.
    # Rationale: Requires refactoring build_profile() to use ConfigResolver
    # for dynamic CLI arg merging, which is beyond the scope of this PR.
    if args.steps:
        # Override step_include mit CLI-Argumenten
        step_list = [s.strip() for s in args.steps.split(",") if s.strip()]
        # Future work: Integrate ConfigResolver to dynamically modify profile.step_include
        console.warning(
            f"--steps Option erkannt ({', '.join(step_list)}), "
            "aber noch nicht vollständig implementiert. "
            "Verwende [tool.setup].steps in pyproject.toml."
        )

    if args.skip:
        # Override step_exclude mit CLI-Argumenten
        skip_list = [s.strip() for s in args.skip.split(",") if s.strip()]
        # Future work: Integrate ConfigResolver to dynamically modify profile.step_exclude
        console.warning(
            f"--skip Option erkannt ({', '.join(skip_list)}), "
            "aber noch nicht vollständig implementiert. "
            "Verwende [tool.setup].exclude in pyproject.toml."
        )

    # Context für Steps erstellen
    ctx = BaseStepContext(
        config=config,
        profile=profile,
        log=log,
        console=console,
    )

    # 5. Header anzeigen
    seg = Segment.from_catalog(CATALOG)
    if seg.license:
        console.info(seg.license)
    if seg.title:
        console.header(seg.title)
    for part in (seg.intro, seg.body):
        if part:
            console.info(part)

    # 6. Steps ausführen
    ok = leaf(ctx)

    # 7. Next-Steps anzeigen (bei Erfolg)
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
    """Entry-Point für pyproject.toml / setup_v2.py."""
    raise SystemExit(execute(sys.argv[1:]))
