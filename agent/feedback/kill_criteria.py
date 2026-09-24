"""Evaluate a playbook's kill criteria against run metrics (proposed reading A-010)."""

from __future__ import annotations

import operator

OPS = {">": operator.gt, ">=": operator.ge, "<": operator.lt, "<=": operator.le, "==": operator.eq}


def tripped(criteria: list[dict], metrics: dict) -> list[dict]:
    out = []
    for c in criteria:
        value = metrics.get(c["metric"])
        if value is not None and OPS[c["op"]](value, c["threshold"]):
            out.append({**c, "value": value})
    return out
