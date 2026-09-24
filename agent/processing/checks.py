"""Output gate for briefs: deterministic checks that run on every draft, template or model.

A brief that fails any check is not written, and the failure goes to the error
log. The content rules come from iTmethods' own public pages
(docs/research/itmethods-product-facts.md); proposed reading A-029.
"""

from __future__ import annotations

import re

MAX_WORDS = 300
REQUIRED_SECTIONS = ["## Why now", "## Applicability", "## What we know about the account",
                     "## Where Reign fits", "## Routing", "## Open questions for the approver", "## Sources"]

CITATION = re.compile(r"\[([A-Za-z0-9][A-Za-z0-9:_/.\-]*)\]")
URL = re.compile(r"https?://[^\s,;)\]]+[^\s,;.)\]]")
PRODUCT = re.compile(r"\b(Reign|Forge|iTmethods)\b")
NEGATION = re.compile(r"\b(not|no|never|without|doesn't|does not|nor)\b", re.IGNORECASE)

# Rule 1: never claim compliance, certification, independent assurance or validation.
CLAIM_WORDS = re.compile(
    r"\b(compliant|certified|certification|certify|certifies|attest\w*|audit opinion|"
    r"independent(ly)?\s+(assurance|validation|validate\w*|review\w*)|validat(e|es|ed|ion)\s+(your|their|the bank)|"
    r"(ensure|ensures|guarantee\w*|achieve\w*|deliver\w*)\s+(\w+\s+){0,3}compliance)\b", re.IGNORECASE)
# Rule 2: never state a briefing duration.
DURATION = re.compile(r"\b\d+\s*(?:-|to|–)?\s*\d*\s*(?:min|mins|minute|minutes|hour|hours|hr|hrs)\b", re.IGNORECASE)
# Rule 3: never imply CMMC, FedRAMP or CUI capability (and no ITAR claim).
DEFENSE = re.compile(r"\b(CMMC|FedRAMP|CUI|ITAR|controlled unclassified)\b", re.IGNORECASE)
SLOP = re.compile(r"(in today's|rapidly evolving|game[- ]changer|\bunlock\w*|\bleverag\w*|seamless\w*|"
                  r"cutting[- ]edge|revolutioni\w+|synerg\w+|\bdelve\w*|hope this finds you|\u2014)", re.IGNORECASE)


def _sentences(text: str) -> list[str]:
    lines = [l.strip(" -*") for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    return [s for line in lines for s in re.split(r"(?<=[.!?])\s+", line) if s.strip()]


def check_brief(text: str, *, allowed_ids: set[str], allowed_urls: set[str], product_ids: set[str],
                caveat_required: bool) -> list[str]:
    problems: list[str] = []
    body, _, sources = text.partition("## Sources")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            problems.append(f"missing section '{section}'")
    words = len(re.findall(r"\b\w+\b", CITATION.sub("", body)))
    if words > MAX_WORDS:
        problems.append(f"brief body is {words} words; limit is {MAX_WORDS}")

    cited = set(CITATION.findall(text))
    if not cited:
        problems.append("brief cites no sources")
    for cid in sorted(cited - allowed_ids):
        problems.append(f"cites unknown source id [{cid}]")
    for cid in sorted(set(CITATION.findall(body)) - set(CITATION.findall(sources))):
        problems.append(f"[{cid}] is cited but not listed under Sources")
    for url in sorted(set(URL.findall(text)) - allowed_urls):
        problems.append(f"contains a URL that is not an approved source: {url}")

    for sentence in _sentences(body):
        if PRODUCT.search(sentence) and not (set(CITATION.findall(sentence)) & product_ids):
            problems.append(f"product mention without an approved claim id: {sentence[:80]!r}")
        if CLAIM_WORDS.search(sentence) and not NEGATION.search(sentence):
            problems.append(f"claims compliance, certification, assurance or validation: {sentence[:80]!r}")
    if DURATION.search(body):
        problems.append("states a duration")
    if DEFENSE.search(text):
        problems.append("mentions CMMC, FedRAMP, CUI or ITAR")
    slop = SLOP.findall(text)
    if slop:
        problems.append(f"filler or banned phrasing: {sorted({s if isinstance(s, str) else s[0] for s in slop})}")

    if caveat_required and "applicability requires confirmation" not in body.lower():
        problems.append("preflight requires the phrase 'applicability requires confirmation'")
    return problems
