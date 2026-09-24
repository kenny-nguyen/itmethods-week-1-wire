"""Route contacts into buyer lanes by job title, without asking them to pick one.

Proposed reading A-011: one brief, routed to a risk lane and an engineering
lane by title. Proposed reading A-032: titles on the playbook's do-not-route
list (for example a CISO for a generic governance message) get nothing.
Lane keywords live in the playbook so the operator can change them as data.
"""

from __future__ import annotations

from agent.input.models import Contact


def route(contacts: list[Contact], lanes: dict[str, list[str]], do_not_route: list[str],
          allowed_lanes: list[str]) -> tuple[dict[str, list[Contact]], list[tuple[Contact, str]]]:
    routed: dict[str, list[Contact]] = {lane: [] for lane in allowed_lanes}
    skipped: list[tuple[Contact, str]] = []
    for c in contacts:
        title = c.title.lower()
        blocked = next((k for k in do_not_route if k.lower() in title), None)
        if blocked:
            skipped.append((c, f"title matches do-not-route '{blocked}'"))
            continue
        lane = next((l for l in allowed_lanes if any(k.lower() in title for k in lanes.get(l, []))), None)
        if lane is None:
            skipped.append((c, "title matches no lane"))
        else:
            routed[lane].append(c)
    return routed, skipped
