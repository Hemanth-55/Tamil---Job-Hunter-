"""Tamil - Job Hunter · build cover letters

One page, Arial. Default since 27 Nov 2026: a narrative letter (`body:` paragraphs) that tells Hemi's story,
from the cricket ground in Chennai to analytics in Boston, and links it quietly to this exact role.
Older letters use the template: why this company -> the business problem -> proof -> close.
Facts only from resume/master.yaml (every number is checked). Phone comes from the private contact file.

  python src/build_cover.py resume/cover_letters.yaml OUT_DIR [--only 01,02] [--contact path/to/contact.yaml]
Writes OUT_DIR/<NN>/Cover Letter.docx and .pdf
"""
import argparse, re, subprocess, sys
from datetime import date
from pathlib import Path

import yaml
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from check_facts import numbers, flatten  # noqa: E402

FONT, BODY = "Arial", 10.5


def run(p, text, bold=False, size=BODY, color=None):
    r = p.add_run(text); r.bold = bold; r.font.name = FONT; r.font.size = Pt(size)
    if color: r.font.color.rgb = RGBColor(*color)
    return r


def para(doc, text="", after=8, align=None, size=BODY, bold=False):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(after); p.paragraph_format.space_before = Pt(0); p.paragraph_format.line_spacing = 1.12
    if align: p.alignment = align
    if text: run(p, text, bold=bold, size=size)
    return p


def letter_text(cfg, nn):
    L = cfg["letters"][nn]
    if "body" in L:  # narrative letter (Hemi's rule, 27 Nov 2026): his story, linked to this role
        return L, [t.strip() for t in L["body"]]
    pr = [cfg["proofs"][k] for k in L["proofs"]]
    body = [L["why"], " ".join([L["problem"], pr[0]]), " ".join(pr[1:]), cfg["availability"][L["avail"]] + " " + cfg["close"]]
    return L, body


def fact_check(texts, master_nums):
    bad = sorted(n for t in texts for n in numbers(t) if n not in master_nums and n not in {"2027", "2026", "1", "2", "3"})
    banned = [w for t in texts for w in (r"\bformer\b", r"\bBU\b", "Boston University") if re.search(w, t)]
    return bad, banned


def build(cfg, nn, out_dir, contact, master_nums):
    L, body = letter_text(cfg, nn)
    bad, banned = fact_check([L.get("why", ""), *body], master_nums)
    if bad or banned:
        raise SystemExit(f"{nn}: fact check failed: numbers not in master {bad} {banned}")
    doc = Document()
    s = doc.sections[0]; s.top_margin = s.bottom_margin = Inches(0.9); s.left_margin = s.right_margin = Inches(1.0)
    para(doc, "HEMANTH KUMAR GOPI", after=2, align=WD_ALIGN_PARAGRAPH.CENTER, size=15, bold=True)
    line = " · ".join(x for x in [contact.get("phone"), "hemanthkumargopi55@gmail.com", "hemanthkumargopi.vercel.app", "linkedin.com/in/hemanthkumargopi"] if x)
    p = para(doc, after=18, align=WD_ALIGN_PARAGRAPH.CENTER); run(p, line, size=9, color=(80, 80, 80))
    para(doc, date.today().strftime("%B %-d, %Y"), after=12)
    para(doc, f"Hiring Team, {L['company']}", after=2)
    para(doc, f"Re: {L['role']}", after=14, bold=True)
    para(doc, "Dear Hiring Team,", after=10)
    for t in body:
        para(doc, t, after=10)
    para(doc, "Sincerely,", after=2)
    para(doc, "Hemanth Kumar Gopi", after=0, bold=True)
    d = out_dir / nn; d.mkdir(parents=True, exist_ok=True)
    f = d / "Cover Letter.docx"; doc.save(f)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(d), str(f)], capture_output=True, timeout=120)
    pages = subprocess.run(["pdfinfo", str(d / "Cover Letter.pdf")], capture_output=True, text=True).stdout
    n = int(re.search(r"Pages:\s+(\d+)", pages).group(1)) if "Pages" in pages else -1
    if n != 1:
        raise SystemExit(f"{nn}: cover letter is {n} pages, must be 1")
    return f


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("letters"); ap.add_argument("out"); ap.add_argument("--only"); ap.add_argument("--contact")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.letters))
    master = yaml.safe_load(open(ROOT / "resume/master.yaml"))
    master_nums = {n for t in flatten(master) for n in numbers(t)}
    contact = yaml.safe_load(open(a.contact)) if a.contact and Path(a.contact).exists() else {}
    keys = a.only.split(",") if a.only else sorted(cfg["letters"])
    for nn in keys:
        print("built", build(cfg, nn, Path(a.out), contact, master_nums))
