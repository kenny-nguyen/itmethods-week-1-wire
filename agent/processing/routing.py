"""Route contacts into buyer lanes by job title, without asking them to pick one.

Operator decisions A-011 and A-032: one brief, contacts suggested by lane from their titles; titles on the
playbook's do-not-route list (starting with the CISO) are never suggested. Lane keywords are playbook data.

Titles are normalised before matching (adversarial QA F2): lowercase, dots and other punctuation removed,
hyphens and slashes read as spaces, whitespace collapsed; a keyword also matches with its spaces removed,
so "C.I.S.O.", "Chief Information-Security Officer" and "CISO/VP Engineering" all hit the list.
"""

from __future__ import annotations

import re
import unicodedata

from agent.input.models import Contact


def normalise(title: str) -> str:
    t = unicodedata.normalize("NFKC", title)  # full-width and other compatibility forms (re-test F5)
    t = re.sub(r"[-_/|,;:&+]", " ", t.lower())
    t = re.sub(r"[^a-z0-9 ]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def _matches(keyword: str, title: str) -> bool:
    k, t = normalise(keyword), normalise(title)
    return bool(k) and (re.search(rf"\b{re.escape(k)}\b", t) is not None or k.replace(" ", "") in t.replace(" ", ""))


def route(contacts: list[Contact], lanes: dict[str, list[str]], do_not_route: list[str],
          allowed_lanes: list[str]) -> tuple[dict[str, list[Contact]], list[tuple[Contact, str]]]:
    routed: dict[str, list[Contact]] = {lane: [] for lane in allowed_lanes}
    skipped: list[tuple[Contact, str]] = []
    for c in contacts:
        blocked = next((k for k in do_not_route if _matches(k, c.title)), None)
        if blocked:
            skipped.append((c, f"title matches do-not-route '{blocked}'"))
            continue
        lane = next((l for l in allowed_lanes if any(_matches(k, c.title) for k in lanes.get(l, []))), None)
        if lane is None:
            skipped.append((c, "title matches no lane"))
        else:
            routed[lane].append(c)
    return routed, skipped
