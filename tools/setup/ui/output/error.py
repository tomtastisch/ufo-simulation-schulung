# tools/setup/ui/error.py
from __future__ import annotations

from datetime import datetime, timezone


def error(
        *,
        step: str,
        stid: str,
        exc_type: str,
        message: str,
        traceback_text: str,
        timestamp: datetime | None = None,
) -> str:
    ts = timestamp or datetime.now(timezone.utc)
    iso = ts.isoformat(timespec="seconds")

    lines: list[str] = [
        "error:",
        f"  step: {step}",
        f"  stid: {stid}",
        f"  type: {exc_type}",
        f"  message: {message}",
        "  traceback: |",
    ]
    for line in traceback_text.rstrip().splitlines():
        lines.append(f"    {line}")
    lines.append(f"  timestamp: {iso}")
    lines.append("")

    return "\n".join(lines)
