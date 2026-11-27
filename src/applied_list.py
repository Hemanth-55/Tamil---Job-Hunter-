"""Tamil - Job Hunter · Applied Jobs list

Builds "Applied Jobs.md" in the Job Hunts folder from tracker.csv, so Hemi has one clean page
of everything he has applied to (and what was skipped and why). Re-run after every submission.

  python src/applied_list.py "~/Desktop/Job Hunts"
"""
import csv, sys
from collections import Counter
from datetime import date
from pathlib import Path


def build(folder: Path) -> Path:
    rows = list(csv.DictReader(open(folder / "tracker.csv", newline="")))
    applied = sorted((r for r in rows if r["status"] == "applied"), key=lambda r: (r.get("applied_on", ""), r["company"]))
    skipped = [r for r in rows if r["status"].startswith("skipped")]
    by_co = Counter(r["company"] for r in applied)

    out = [
        "# Applied Jobs",
        "",
        f"_Updated {date.today():%d %b %Y} · {len(applied)} applications · {len(by_co)} companies_",
        "",
        "| # | Applied | Company | Role | Location | Status | Folder | Link |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(applied, 1):
        folder_name = r.get("folder", "").split("/")[-1] or "—"
        loc = " ".join(r["location"].split())[:40]
        out.append(f"| {i} | {r.get('applied_on','')} | {r['company']} | {r['role']} | {loc} | Submitted, awaiting reply | {folder_name} | [posting]({r['url']}) |")

    out += ["", "## By company", ""]
    out += [f"- **{c}**: {n}" for c, n in by_co.most_common()]

    if skipped:
        out += ["", "## Skipped (not applied)", "", "| Company | Role | Why |", "|---|---|---|"]
        out += [f"| {r['company']} | {r['role']} | {r['status'].removeprefix('skipped:').strip()} |" for r in skipped]

    out += [
        "",
        "## How to use this page",
        "",
        "- When a company replies, change its Status here (Interview, Rejected, Offer) and tell Tamil, so tracker.csv stays in sync.",
        "- Each role's folder has the exact résumé, cover letter and answers sent (`Submitted.md`).",
        "- Follow up politely 10–14 days after applying if there is no reply.",
        "",
    ]
    path = folder / "Applied Jobs.md"
    path.write_text("\n".join(out))
    return path


if __name__ == "__main__":
    print(build(Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path("~/Desktop/Job Hunts").expanduser()))
