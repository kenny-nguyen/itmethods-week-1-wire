"""Evaluate a playbook's kill criteria against run metrics (proposed reading A-010)."""

from __future__ import annotations

import operator

OPS = {">": operator.gt, ">=": operator.ge, "<": operator.lt, "<=": operator.le, "==": operator.eq}
MIN_RATIO_SAMPLE = 5  # assumption to confirm with sales leadership (A-049)


def ratio(part: int, whole: int) -> float | None:
    """A quality ratio, or None (not measured, so it cannot trip) until the sample reaches MIN_RATIO_SAMPLE."""
    return part / whole if whole >= MIN_RATIO_SAMPLE else None


def tripped(criteria: list[dict], metrics: dict) -> list[dict]:
    out = []
    for c in criteria:
        value = metrics.get(c["metric"])
        if value is not None and OPS[c["op"]](value, c["threshold"]):
            out.append({**c, "value": value})
    return out
