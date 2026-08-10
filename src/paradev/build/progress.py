"""Build progress event helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
BuildProgressCallback = Callable[[dict[str, object]], None]


def emit_progress(
    progress: BuildProgressCallback | None,
    phase: str,
    *,
    current: str | None = None,
    detail: str | None = None,
    index: int | None = None,
    label: str | None = None,
    percent: float | int | None = None,
    total: int | None = None,
    counts: Mapping[str, int] | None = None,
) -> None:
    """Emit one JSON-safe compiler progress event."""

    if progress is None:
        return
    event: dict[str, object] = {
        "schema": "paradev.build.progress.v1",
        "phase": phase,
        "percent": _clamp_percent(percent),
    }
    if label:
        event["label"] = label
    if detail:
        event["detail"] = detail
    if current:
        event["current"] = current
    if index is not None:
        event["index"] = max(0, int(index))
    if total is not None:
        event["total"] = max(0, int(total))
    if counts:
        event["counts"] = {str(key): max(0, int(value)) for key, value in counts.items()}
    progress(event)


def scaled_percent(start: int, end: int, index: int, total: int) -> int:
    """Return a bounded integer percent for one indexed step."""

    if total <= 0:
        return end
    span = max(0, end - start)
    return _clamp_percent(start + span * max(0, min(index, total)) / total)


def _clamp_percent(value: float | int | None) -> int:
    if value is None:
        return 0
    return max(0, min(100, round(float(value))))
