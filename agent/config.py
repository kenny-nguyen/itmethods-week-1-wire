"""Deployment configuration, read from the environment in one place.

| Variable | Default | Meaning |
|---|---|---|
| WIRE_OUT_DIR | <repo>/out | Where runs, the audit trail, the error log and kill switches live. Set once per deployment. |
| WIRE_PROVIDER | (auto) | "offline" (or "template") forces offline test mode, the deterministic CI template; otherwise the direct model-API path is used when a key is set. |
| ANTHROPIC_API_KEY | (unset) | Key for the Claude Messages API. Unset means the template. |
| WIRE_MODEL | claude-opus-5 | Model id for the Claude Messages API. |

Named principals and approvers are deliberately not environment variables: they live in the
reviewed playbook files, so nobody can change who approves by changing a shell (A-053).
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def out_dir() -> Path:
    return Path(os.environ.get("WIRE_OUT_DIR") or ROOT / "out").resolve()
