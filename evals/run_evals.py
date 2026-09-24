"""Run the brief-gate evals: `python -m evals.run_evals` prints one line per case and exits 1 on any miss."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from agent.processing.checks import check_brief
from evals.golden import golden_brief

CASES = Path(__file__).with_name("brief_cases.json")


def _apply(text: str, edit: dict | None) -> str:
    if not edit:
        return text
    if "remove_section" in edit:
        head, _, rest = text.partition(edit["remove_section"])
        return head + rest[rest.index("\n## "):] if "\n## " in rest else head
    addition = edit.get("text") or "\n".join([edit["text_repeat"]] * edit["times"])
    return text.replace(edit["append_to"] + "\n", edit["append_to"] + "\n" + addition + "\n", 1)


def run() -> list[tuple[str, bool, list[str]]]:
    spec = json.loads(CASES.read_text(encoding="utf-8"))
    results = []
    text, ctx, caveat = golden_brief(caveat=False)
    kwargs = dict(allowed_ids=ctx.allowed_ids(), allowed_urls=ctx.allowed_urls(), claim_texts=ctx.claim_texts())
    for case in spec["cases"]:
        problems = check_brief(_apply(text, case["edit"]), caveat_required=caveat, **kwargs)
        ok = (not problems) if case["expect"] is None else any(case["expect"] in p for p in problems)
        results.append((case["name"], ok, problems))
    text, ctx, caveat = golden_brief(caveat=True)
    kwargs = dict(allowed_ids=ctx.allowed_ids(), allowed_urls=ctx.allowed_urls(), claim_texts=ctx.claim_texts())
    for case in spec["caveat_cases"]:
        variant = text.replace("applicability requires confirmation", "may apply") if case["remove_caveat"] else text
        problems = check_brief(variant, caveat_required=caveat, **kwargs)
        ok = (not problems) if case["expect"] is None else any(case["expect"] in p for p in problems)
        results.append((case["name"], ok, problems))
    return results


def main() -> int:
    results = run()
    for name, ok, problems in results:
        print(f"{'PASS' if ok else 'MISS'}  {name}" + ("" if ok else f"  -> {problems}"))
    misses = sum(not ok for _, ok, _ in results)
    print(f"{len(results) - misses}/{len(results)} eval cases behaved as expected")
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
