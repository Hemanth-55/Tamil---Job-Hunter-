"""Tamil - Job Hunter · fact check

Every number, percentage, money amount and score in a tailored résumé must already appear in
resume/master.yaml. If the tailoring step invents or changes a figure, the build stops.
It also blocks phrases Hemi never wants on a résumé.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NUM = re.compile(r"[€$]?\d[\d,]*(?:\.\d+)?(?:%|\+|M|k)?")
BANNED = [r"\bformer\b", r"\bBU\b", r"Boston University"]


def numbers(text: str) -> set[str]:
    return {n.rstrip(".,").replace(",", "") for n in NUM.findall(text)}


def flatten(x) -> list[str]:
    if isinstance(x, str):
        return [x]
    if isinstance(x, dict):
        return [s for v in x.values() for s in flatten(v)]
    if isinstance(x, list):
        return [s for v in x for s in flatten(v)]
    return [str(x)] if x is not None else []


def check(tailored: dict) -> list[str]:
    master_text = " ".join(flatten(yaml.safe_load((ROOT / "resume" / "master.yaml").read_text())))
    known = numbers(master_text)
    problems = []
    body = flatten({k: v for k, v in tailored.items() if k != "target"})
    for line in body:
        for n in numbers(line) - known:
            problems.append(f"{n!r} in: {line[:90]}")
        for pat in BANNED:
            if re.search(pat, line, re.I):
                problems.append(f"banned phrase {pat!r} in: {line[:90]}")
    return problems


if __name__ == "__main__":
    import sys
    t = yaml.safe_load(Path(sys.argv[1]).read_text())
    p = check(t)
    print("OK: every figure is in master.yaml" if not p else "\n".join(p))
    sys.exit(1 if p else 0)
