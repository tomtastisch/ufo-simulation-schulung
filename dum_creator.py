#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import secrets
import yaml
from datetime import datetime, timezone

from pathlib import Path
from typing import Any

EXCLUDES = {".git", ".venv", "__pycache__", "dumps", "dump"}


class LiteralStr(str):
    """Marker für YAML-Block-Strings (|)."""
    pass


def _literal_str_representer(dumper: yaml.Dumper, data: LiteralStr) -> yaml.ScalarNode:
    # Immer als Block-Scalar schreiben: |
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


class LiteralDumper(yaml.SafeDumper):
    """SafeDumper mit Unterstützung für LiteralStr."""
    pass


# Registrieren des Repräsentanten für unseren Typ beim LiteralDumper
LiteralDumper.add_representer(LiteralStr, _literal_str_representer)


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def should_exclude(path: Path) -> bool:
    return any(part in EXCLUDES for part in path.parts)


def _next_dump_code() -> int:
    """Erzeugt eine numerische, zeitbasierte Prüfziffer.

    - Basis: Millisekunden seit einer festen Epoche (2025-01-01 UTC)
    - Monoton wachsend mit der Zeit (unter Annahme monotone Uhr)
    - Unabhängig von Dateien oder Index-Dateien
    - Die Anzahl der Stellen ist mindestens 6, nach oben nicht künstlich begrenzt
    """
    epoch = datetime(2025, 1, 1, tzinfo=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    delta_ms = int((now - epoch).total_seconds() * 1000)

    # Untergrenze 6-stellig sicherstellen
    if delta_ms < 100_000:
        return 100_000 + delta_ms
    return delta_ms


def collect_files(root: Path) -> dict[str, dict[str, Any]]:
    files: dict[str, dict[str, Any]] = {}

    for path in sorted(root.rglob("*")):
        if should_exclude(path):
            continue
        if path.suffix not in {".py", ".toml"}:
            continue

        content = path.read_text(encoding="utf-8")
        digest = hash_bytes(content.encode("utf-8"))
        rel_path = path.relative_to(root).as_posix()

        files[rel_path] = {
            "rel_path": rel_path,
            "hash": digest,
            "content": LiteralStr(content),
        }

    return files


def main() -> None:
    cwd = Path.cwd()

    print("Pfad eingeben, der gedumpt werden soll.")
    print(f"Leer lassen = aktuelles Verzeichnis: {cwd}")
    raw = input("> ").strip()

    print("Name für die YAML-Datei eingeben (ohne .yaml, leer = complete_dump):")
    name_raw = input("> ").strip()

    if not raw:
        target = cwd
    else:
        if raw.startswith("cd "):
            raw = raw[3:].strip()
        target = Path(raw).expanduser()

    target = target.resolve()

    if not target.exists():
        print(f"Fehler: Pfad existiert nicht: {target}")
        raise SystemExit(1)

    if not target.is_dir():
        print(f"Fehler: Pfad ist kein Ordner: {target}")
        raise SystemExit(1)

    print(f"Sammle Python-Dateien unter: {target}\n")

    files = collect_files(target)

    # Verzeichnisliste aus rel_paths ableiten, "." ausblenden
    dir_set: set[str] = set()
    for rel_path in files.keys():
        parent = Path(rel_path).parent
        if str(parent) != ".":
            dir_set.add(parent.as_posix())

    dirs = sorted(dir_set)

    # Stabiler Snapshot-Hash über alle File-Hashes in deterministischer Reihenfolge
    snapshot_hash = hash_bytes(
        "\n".join(files[k]["hash"] for k in sorted(files.keys())).encode("utf-8")
    )

    # Dumps immer in einem Unterordner "dumps" ablegen
    dumps_dir = target / "dumps"
    dumps_dir.mkdir(exist_ok=True)

    # Basisnamen bestimmen (ohne laufende Nummer / Präfix)
    if not name_raw:
        base = secrets.token_urlsafe(5)
    else:
        # Nutzer darf auch schon .yaml/.yml angeben – wir normalisieren auf .yaml
        # und entfernen evtl. vorhandene Endung zuerst.
        base = name_raw
        if base.lower().endswith((".yaml", ".yml")):
            base = Path(base).stem

    # Prüfziffer rein aus der Zeit generieren (unabhängig von Dateien/Index)
    code = _next_dump_code()
    yml = f"{code}_{base if base else "dump"}.yaml"
    out_path = dumps_dir / yml

    dump: dict[str, Any] = {
        "dump_path": str(out_path),
        "root": str(target),
        "hash": snapshot_hash,
        "dirs": dirs,
        "files": [files[k] for k in sorted(files.keys())],
    }

    with out_path.open("w", encoding="utf-8") as fh:
        yaml.dump(
            dump,
            fh,
            Dumper=LiteralDumper,
            sort_keys=False,
            allow_unicode=True,
            width=88,
        )

    print("Fertig. Ausgabe gespeichert in:")
    print(out_path)


if __name__ == "__main__":
    main()
