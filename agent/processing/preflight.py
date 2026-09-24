"""Applicability preflight: does this trigger apply to this account, and may a brief be drafted?

Runs after the ICP filter and before any brief is drafted. Pure function.

Outcomes:
- READY: draft the brief. `applicability` says whether the rule applies or
  "requires confirmation"; the brief must carry that wording.
- HOLD: a human must look first (reason given).
- SKIP: the trigger does not apply to this account.
- BLOCKED: drafting would break a rule (trigger not implemented, unverified
  source, bank outbound before a briefing).

Proposed readings this depends on, set per play in the playbook:
- `unconfirmed_applicability`: "hold" (A-025, the general case) or
  "structured_brief" (A-044, the SR 26-2 bank brief).
- `handoff` (A-043): no new cold outreach until a briefing is booked; on a
  regulatory trigger the brief goes to the named account owner.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agent.input.models import Account, Enrichment, Fact, Trigger

READY, HOLD, SKIP, BLOCKED = "ready", "hold", "skip", "blocked"
APPLIES, REQUIRES_CONFIRMATION, DOES_NOT_APPLY = "applies", "requires_confirmation", "does_not_apply"
CAVEAT = "applicability requires confirmation"


@dataclass
class Preflight:
    status: str
    applicability: str | None = None
    reasons: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)
    context: tuple[Fact, ...] = ()


def check(trigger: Trigger, account: Account, enrichment: Enrichment, play: dict) -> Preflight:
    if not trigger.implemented:
        return Preflight(BLOCKED, reasons=[f"trigger {trigger.id} is not implemented: {trigger.not_implemented_reason}"])

    cited = {f.source for f in trigger.facts}
    bad = [s.id for s in trigger.sources + trigger.context_sources if s.id in cited and not (s.verified and s.url)]
    if not trigger.facts or bad:
        return Preflight(BLOCKED, reasons=[f"trigger {trigger.id} has no verified source for its facts: {bad or 'no facts'}"])

    handoff = play.get("handoff") or {}
    if (play.get("channel") == "sequence" and handoff.get("cold_outreach_until_briefing_booked") is False
            and not account.briefing_scheduled):
        return Preflight(BLOCKED, reasons=["no new cold outreach to this buyer until a briefing is booked (A-043)"])
    if handoff.get("route_to") == "account_owner" and not account.owner:
        return Preflight(HOLD, reasons=["no named iTmethods account owner on record to route the brief to (A-043)"])

    applicability, caveats, reasons = _applicability(trigger, account, enrichment)
    context = trigger.context_by_jurisdiction.get(account.hq_country or "", ())

    if applicability == DOES_NOT_APPLY:
        return Preflight(SKIP, applicability, reasons)
    if applicability == REQUIRES_CONFIRMATION and play.get("unconfirmed_applicability", "hold") == "hold":
        return Preflight(HOLD, applicability, reasons + ["held for a human: applicability unconfirmed (A-025)"],
                         caveats, context)
    # "structured_brief" (A-044): the brief states what changed, what is certain, and what depends on
    # structure, each marked "confirm". It never says the rule applies.
    return Preflight(READY, applicability, reasons, caveats, context)


def _applicability(trigger: Trigger, account: Account, e: Enrichment) -> tuple[str, list[str], list[str]]:
    """Jurisdiction first, then the relevance threshold. Never asserts more than the record shows."""
    caveats: list[str] = []
    if trigger.jurisdiction is None:
        return REQUIRES_CONFIRMATION, [CAVEAT], ["trigger has no jurisdiction on record"]

    in_jurisdiction = account.hq_country == trigger.jurisdiction
    if trigger.regulator == "Federal Reserve":
        # SR 26-2 reaches a non-US bank only through a US entity regulated by the Federal Reserve.
        # US headquarters alone does not establish Federal Reserve regulation: only a recorded
        # Federal Reserve-regulated banking organization does (independent grader).
        if e.us_fed_regulated_entity is True:
            reason = "has a Federal Reserve-regulated banking organization on record"
        elif e.us_fed_regulated_entity is False and not in_jurisdiction:
            return DOES_NOT_APPLY, [], [f"{account.hq_country} bank with no US Federal Reserve-regulated entity"]
        else:
            return (REQUIRES_CONFIRMATION, [CAVEAT],
                    [f"{account.hq_country} bank; a Federal Reserve-regulated banking organization is not established"])
    elif in_jurisdiction:
        reason = f"in {trigger.jurisdiction} jurisdiction"
    else:
        return REQUIRES_CONFIRMATION, [CAVEAT], [f"account is outside {trigger.jurisdiction}"]

    threshold = trigger.relevance_threshold_total_assets_usd
    if threshold:
        if account.total_assets_usd is None:
            caveats.append("total assets not on record; the letter is most relevant above the stated threshold")
        elif account.total_assets_usd < threshold:
            caveats.append("total assets are below the threshold at which the letter says it is most relevant")
    return APPLIES, caveats, [reason]
