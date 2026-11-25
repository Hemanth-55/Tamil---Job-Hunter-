"""Tamil - Job Hunter · package a job into Hemi's "Job Hunts" folder

For one approved role it creates:
  Job Hunts/<YYYY-MM-DD> · <Company> · <Role>/
      Hemanth Kumar Gopi - Resume - <Company>.docx   tailored résumé (Word, his layout)
      Hemanth Kumar Gopi - Resume - <Company>.pdf    same, for upload portals
      Job.md                                         the posting: link, verification, why it fits, next steps
and adds a row to Job Hunts/tracker.csv (his private application tracker).

Usage:
  python src/package.py resume/tailored/<file>.yaml  "<Job Hunts folder>"
The tailored YAML's `target` block must hold company, role, url, and the verification notes.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from build_resume import build, to_pdf          # noqa: E402
from check_facts import check                   # noqa: E402

TRACKER_COLS = ["found", "company", "role", "location", "fit", "url", "verified_on", "folder", "status", "applied_on", "notes"]


def safe(s: str) -> str:
    return re.sub(r"[/\\:*?\"<>|]+", "-", s).strip()


def posting(url: str) -> dict:
    inbox = ROOT / "data" / "inbox.json"
    if inbox.exists():
        for j in json.loads(inbox.read_text())["jobs"]:
            if j["url"] == url:
                return j
    return {}


def main(tailored_path: Path, hunts: Path):
    t = yaml.safe_load(tailored_path.read_text())
    problems = check(t)
    if problems:
        sys.exit("Blocked by fact check:\n  " + "\n  ".join(problems))
    tg = t["target"]
    today = dt.date.today().isoformat()
    folder = hunts / safe(f"{today} · {tg['company']} · {tg['role']}")
    folder.mkdir(parents=True, exist_ok=True)

    name = f"Hemanth Kumar Gopi - Resume - {safe(tg['company'])}"
    docx = build(t, folder / f"{name}.docx")
    try:
        pdf, pages = to_pdf(docx)
        if pages != 1:
            print(f"WARNING: résumé is {pages} pages; trim before sending.")
    except Exception as e:                       # no LibreOffice on this machine: Word file is still there
        print(f"(PDF skipped: {e.__class__.__name__}; open the .docx and Save As PDF if a portal needs it)")

    j = posting(tg["url"])
    lines = [f"# {tg['role']} · {tg['company']}", "",
             f"**Apply:** {tg['url']}", f"**Location:** {tg.get('location') or j.get('location') or '—'}",
             f"**Fit score:** {j.get('score', tg.get('fit', '—'))}/100" + (f"  ({'; '.join(j.get('why', []))})" if j.get('why') else ""),
             f"**Posted:** {j.get('posted') or tg.get('posted') or '—'}", "",
             "## Verified", tg.get("verified", f"Live on the employer's own job board ({j.get('source', 'employer site')}), checked {today}."), "",
             "## Why it fits", tg.get("why_fit", ""), "",
             "## Gaps to be honest about", tg.get("gaps", "None flagged."), "",
             "## Next steps", "- [ ] Read the résumé once and approve it",
             "- [ ] Apply on the link above (Tamil never submits for you)",
             "- [ ] Tell Tamil \"applied\" so the tracker updates", ""]
    if j.get("description"):
        lines += ["## Posting (as published)", j["description"][:3500], ""]
    (folder / "Job.md").write_text("\n".join(lines))
    shutil.copy(tailored_path, folder / "resume-content.yaml")

    tracker = hunts / "tracker.csv"
    new = not tracker.exists()
    rows = list(csv.DictReader(tracker.open())) if not new else []
    if not any(r["url"] == tg["url"] for r in rows):
        with tracker.open("a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=TRACKER_COLS)
            if new:
                w.writeheader()
            w.writerow({"found": today, "company": tg["company"], "role": tg["role"],
                        "location": tg.get("location") or j.get("location", ""), "fit": j.get("score", ""),
                        "url": tg["url"], "verified_on": today, "folder": folder.name, "status": "ready to apply",
                        "applied_on": "", "notes": ""})
    print(f"packaged → {folder}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]).expanduser())
