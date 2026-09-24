"""Write run artifacts atomically (temp file, then rename), so a crash never leaves half a brief."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunPaths:
    out: Path
    run_id: str

    @property
    def run_dir(self) -> Path:
        return self.out / "runs" / self.run_id

    @property
    def briefs(self) -> Path:
        return self.run_dir / "briefs"

    @property
    def approvals(self) -> Path:
        return self.run_dir / "approvals"

    @property
    def audit(self) -> Path:
        return self.out / "audit.jsonl"

    @property
    def errors(self) -> Path:
        return self.out / "errors.jsonl"

    @property
    def state(self) -> Path:
        return self.out / "state"


def _safe_name(object_id: str) -> str:
    return object_id.replace(":", "_").replace("/", "_")


def write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)
    return path


def write_json(path: Path, data: dict) -> Path:
    return write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


def brief_path(paths: RunPaths, object_id: str) -> Path:
    return paths.briefs / f"{_safe_name(object_id)}.md"


def approval_path(paths: RunPaths, object_id: str) -> Path:
    return paths.approvals / f"{_safe_name(object_id)}.json"
