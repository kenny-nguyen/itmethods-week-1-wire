"""Structured error log, separate from the R-17 audit trail.

The audit trail records what the agent did to a prospect. This log records
what went wrong while trying: a failed adapter read, a gate that rejected a
brief, an audit write that failed. One JSON object per line.

Writing here must never hide the original failure, so if the log file itself
cannot be written the entry is printed to stderr instead of raising.
"""

from __future__ import annotations

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


class ErrorLog:
    def __init__(self, path: str | Path, run_id: str | None = None):
        self.path = Path(path)
        self.run_id = run_id

    def record(self, stage: str, error: BaseException | str, *, context: dict | None = None,
               severity: str = "error") -> dict:
        if isinstance(error, BaseException):
            error_type = type(error).__name__
            message = str(error)
            trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        else:
            error_type, message, trace = "Message", error, None
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "stage": stage,
            "severity": severity,
            "error_type": error_type,
            "message": message,
            "context": context or {},
        }
        if trace:
            entry["traceback"] = trace
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, sort_keys=True) + "\n")
        except OSError as exc:  # never swallow: fall back to stderr
            print(json.dumps({"error_log_write_failed": str(exc), "entry": entry}), file=sys.stderr)
        return entry
