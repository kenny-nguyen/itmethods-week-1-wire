"""Output gate for briefs: deterministic checks that run on every draft, template or model.

A brief that fails any check is not written, and the failure goes to the error
log. The content rules come from iTmethods' own public pages
(docs/research/itmethods-product-facts.md; operator decision A-029).

Hardened after independent QA (Q-005) and security review (D-020):
- every line is checked, including headings and the Sources section, and the
  Sources section may only contain source lines in the generated format;
- a sentence that mentions Reign, Forge or iTmethods (any case) must restate
  the claim it cites word for word, so the right claim id is needed, not just any;
- there is no negation escape: only the approved claim text itself may use
  words like "certification" (it says iTmethods does not issue one);
- links of any shape that are not approved sources are rejected, as are HTML
  and markdown images, which could leak data when a brief is rendered.

What no word list can catch is a claim that is plausible and false. The named
human approver is the control for that.
"""

from __future__ import annotations

import re

MAX_WORDS = 350  # proposed A-045: a short brief a CAE can read in one sitting
# The structure the operator decided for the SR 26-2 brief (A-044).
REQUIRED_SECTIONS = ["## What changed", "## What is certain for this account", "## What depends on structure (confirm)",
                     "## What we know about the account", "## Where Reign fits", "## Suggested next step",
                     "## Suggested recipients in the existing relationship", "## Open questions for the account owner",
                     "## Sources"]
KNOWN_HEADINGS = set(REQUIRED_SECTIONS)
CONDITIONAL_SECTION = "## What depends on structure (confirm)"
# "Never claim a rule applies" (A-044): applicability wording only inside the conditional section.
APPLIES = re.compile(r"\b(applies|apply to (you|the bank|them)|in scope|subject to|is covered by|falls under)\b", re.IGNORECASE)
# Template sentences about the account that name a product but make no product claim.
ACCOUNT_FACT_SENTENCES = {"existing forge customer."}

CITATION = re.compile(r"\[([A-Za-z0-9][A-Za-z0-9:_/.\-]*)\]")
URL = re.compile(r"https?://[^\s,;)\]]+[^\s,;.)\]]", re.IGNORECASE)
PRODUCT = re.compile(r"\b(reign|forge|itmethods)\b", re.IGNORECASE)
SOURCE_LINE = re.compile(r"^- \[([A-Za-z0-9][A-Za-z0-9:_/.\-]*)\] (.+)$")

# Rule 1: never claim or imply compliance, certification, independent assurance or validation.
CLAIMS = re.compile(
    r"\b(compliant|complian\w*\s+(for|with)\s+you|certif\w*|accredit\w*|attest\w*|audit\s+opinion|soc\s*-?\s*2|"
    r"iso\s*-?\s*\d{4,5}\s+(certified|compliant)|"
    r"(independent|third[\s-]*party)\s*(ly\s+)?(assurance|validation|validat\w*|review\w*|audit\w*)|"
    r"validated\s+by|validat\w*\s+(your|their|the\s+bank)|"
    r"(ensure|ensures|guarantee\w*|achieve\w*|deliver\w*|handles?|provides?)\s+([\w-]+\s+){0,3}compliance|"
    r"in\s+line\s+with\s+(sr|osfi|dora|the\s+guidance|every|all)|"
    r"(satisf\w*|meets?|fulfil\w*)\s+([\w-]+\s+){0,3}(expectation|requirement|obligation|guidance|rule)s?)\b",
    re.IGNORECASE)
# Rule 2: never state a briefing or meeting duration, in digits or words.
NUMBER_WORDS = r"(one|two|three|four|five|ten|fifteen|twenty|thirty|forty|forty[\s-]*five|fifty|sixty|ninety)"
DURATION = re.compile(
    r"\b\d+\s*(?:-|to|–)?\s*\d*\s*(?:m|min|mins|minute|minutes|h|hr|hrs|hour|hours)\b|"
    rf"\b(half|quarter)[\s-]+(an|of\s+an)[\s-]+hour\b|\ban\s+hour\b|\b{NUMBER_WORDS}[\s-]+(minute|minutes|hour|hours)\b",
    re.IGNORECASE)
# Rule 3: never imply CMMC, FedRAMP or CUI capability, and no ITAR claim.
DEFENSE = re.compile(r"(\bc\.?\s?m\.?\s?m\.?\s?c\b|cybersecurity\s+maturity\s+model|\bfed\s*-?\s*ramp\b|"
                     r"\bcui\b|controlled\s+unclassified|\bitar\b|international\s+traffic\s+in\s+arms)", re.IGNORECASE)
SLOP = re.compile(r"(in today's|rapidly evolving|game[- ]changer|\bunlock\w*|\bleverag\w*|seamless\w*|"
                  r"cutting[- ]edge|revolutioni\w+|synerg\w+|\bdelve\w*|hope this finds you|—)", re.IGNORECASE)
# Links and markup that are not approved sources.
MARKUP = re.compile(r"(<\s*[a-z!/]|!\[|\]\()", re.IGNORECASE)
BARE_LINK = re.compile(r"(//[a-z0-9-]+\.[a-z0-9.-]+|\bwww\.[a-z0-9-]+|"
                       r"\b(?:[a-z0-9-]+\.)+(?:com|net|org|io|ai|gov|ca|co|dev|app|info|biz|us|uk|eu|xyz|site|example)\b)",
                       re.IGNORECASE)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", CITATION.sub("", text)).strip().rstrip(".").strip().lower()


def _sentences(lines: list[str]) -> list[str]:
    out = []
    for line in lines:
        line = line.strip()
        if not line or line in KNOWN_HEADINGS:
            continue
        line = line.lstrip("#").strip().lstrip("-*").strip()
        out += [s for s in re.split(r"(?<=[.!?])\s+(?!\[)", line) if s.strip()]
    return out


def check_brief(text: str, *, allowed_ids: set[str], allowed_urls: set[str], claim_texts: dict[str, str],
                caveat_required: bool) -> list[str]:
    problems: list[str] = []
    body, sep, sources = text.partition("\n## Sources")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            problems.append(f"missing section '{section}'")
    # The word limit covers the forwardable part; recipients and open questions are notes for the owner.
    forwardable = body.split("\n## Suggested recipients in the existing relationship")[0]
    words = len(re.findall(r"\b\w+\b", CITATION.sub("", forwardable)))
    if words > MAX_WORDS:
        problems.append(f"forwardable brief is {words} words; limit is {MAX_WORDS}")

    # Sources: only generated source lines, each for an id the body cites.
    listed = set()
    for line in sources.splitlines():
        if not line.strip():
            continue
        m = SOURCE_LINE.match(line.strip())
        if not m:
            problems.append(f"unexpected text in Sources: {line.strip()[:80]!r}")
        else:
            listed.add(m.group(1))

    cited = set(CITATION.findall(text))
    if not cited:
        problems.append("brief cites no sources")
    for cid in sorted(cited - allowed_ids):
        problems.append(f"cites unknown source id [{cid}]")
    for cid in sorted(set(CITATION.findall(body)) - listed):
        problems.append(f"[{cid}] is cited but not listed under Sources")
    for url in sorted({u.rstrip(".") for u in URL.findall(text)} - allowed_urls):
        problems.append(f"contains a URL that is not an approved source: {url}")
    stripped = URL.sub(" ", text)
    for hit in sorted({m.group(0) for m in BARE_LINK.finditer(stripped)}):
        problems.append(f"contains a link or domain that is not an approved source: {hit}")
    if MARKUP.search(text):
        problems.append("contains HTML or markdown links or images")

    section = ""
    for line in body.splitlines():
        if line.startswith("## "):
            section = line.strip()
            continue
        if not line.strip().startswith("- "):
            if APPLIES.search(line):
                problems.append(f"says a rule applies outside the conditional section: {line.strip()[:80]!r}")
            continue
        if section == CONDITIONAL_SECTION:
            if not line.strip()[2:].lower().startswith("confirm"):
                problems.append(f"every line in '{CONDITIONAL_SECTION}' must start with 'Confirm': {line.strip()[:80]!r}")
        elif APPLIES.search(line):
            problems.append(f"says a rule applies outside the conditional section: {line.strip()[:80]!r}")

    approved = {cid: _norm(t) for cid, t in claim_texts.items()}
    for sentence in _sentences(body.splitlines()):
        plain = _norm(sentence)
        ids = set(CITATION.findall(sentence))
        is_claim_text = any(plain and plain in approved[i] for i in ids if i in approved)
        if PRODUCT.search(CITATION.sub("", sentence)) and not is_claim_text and plain + "." not in ACCOUNT_FACT_SENTENCES:
            problems.append(f"product sentence does not restate its cited approved claim: {sentence[:80]!r}")
        if CLAIMS.search(sentence) and not is_claim_text:
            problems.append(f"claims or implies compliance, certification, assurance or validation: {sentence[:80]!r}")
    if DURATION.search(text):
        problems.append("states a duration")
    if DEFENSE.search(text):
        problems.append("mentions CMMC, FedRAMP, CUI or ITAR")
    slop = SLOP.findall(text)
    if slop:
        problems.append(f"filler or banned phrasing: {sorted({s if isinstance(s, str) else s[0] for s in slop})}")

    if caveat_required and "applicability requires confirmation" not in body.lower():
        problems.append("preflight requires the phrase 'applicability requires confirmation'")
    return problems
