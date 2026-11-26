"""Tamil - Job Hunter · résumé builder

Renders a tailored résumé (YAML) into a one-page Word file in Hemi's house layout:
Arial · name bold caps centred · contact line centred with live links · bold caps section headers with a rule
above · bold role title, then organisation/location left and MM/YYYY dates right · round, justified bullets ·
no bold numbers · no separate skills section · order: Summary → Education → Work Experience → Projects.

Usage:
  python src/build_resume.py resume/tailored/<file>.yaml  OUT.docx  [--pdf]

A tailored YAML looks like:
  target:  {company: FanDuel, role: Data Analyst, url: https://...}
  summary: [three or four sentences, built from resume/master.yaml summary_bank]
  experience: [{id: ta, bullets: [...]}, {id: cricket, bullets: [...]}, ...]   # order = order on the page
  projects:   [{id: soccer, bullets: [...]}, ...]
Facts are checked against resume/master.yaml by src/check_facts.py before anything is built.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
FONT = "Arial"
BODY = 10
PAGE_W, MARGIN = 8.5, 0.5


def master() -> dict:
    return yaml.safe_load((ROOT / "resume" / "master.yaml").read_text())


def private_contact() -> dict:
    """Phone lives only on Hemi's Mac, never in the public repo."""
    for p in [Path.home() / "Desktop" / "Job Hunts" / "_private" / "contact.yaml",
              Path.home() / "Job Hunts" / "_private" / "contact.yaml",
              Path.home() / "mnt" / "Job Hunts" / "_private" / "contact.yaml"]:
        if p.exists():
            return yaml.safe_load(p.read_text()) or {}
    return {}


# ------------------------------------------------------------------ docx helpers
def run(p, text, bold=False, size=BODY, italic=False):
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    r.font.name, r.font.size = FONT, Pt(size)
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    return r


def spacing(p, before=0, after=0, line=1.0):
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), line


def hyperlink(p, url, label, size):
    part = p.part
    rid = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                         is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), rid)
    r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    fonts = OxmlElement("w:rFonts"); fonts.set(qn("w:ascii"), FONT); fonts.set(qn("w:hAnsi"), FONT)
    sz = OxmlElement("w:sz"); sz.set(qn("w:val"), str(int(size * 2)))
    col = OxmlElement("w:color"); col.set(qn("w:val"), "1F4E9A")
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single")
    for el in (fonts, sz, col, u):
        rpr.append(el)
    r.append(rpr)
    t = OxmlElement("w:t"); t.text = label; r.append(t)
    h.append(r); p._p.append(h)


def rule_above(p):
    ppr = p._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr"); top = OxmlElement("w:top")
    for k, v in {"val": "single", "sz": "6", "space": "1", "color": "000000"}.items():
        top.set(qn(f"w:{k}"), v)
    bdr.append(top); ppr.append(bdr)


def right_tab(p):
    p.paragraph_format.tab_stops.add_tab_stop(Inches(PAGE_W - 2 * MARGIN), WD_TAB_ALIGNMENT.RIGHT)


def bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf = p.paragraph_format
    pf.left_indent, pf.first_line_indent = Inches(0.22), Inches(-0.16)
    spacing(p, 0, 0.5)
    run(p, text)
    return p


def header(doc, title):
    p = doc.add_paragraph(); rule_above(p); spacing(p, 5, 2)
    run(p, title.upper(), bold=True, size=BODY + 0.5)


def entry(doc, title, org, location, dates):
    p = doc.add_paragraph(); spacing(p, 2, 0)
    run(p, title, bold=True)
    p = doc.add_paragraph(); right_tab(p); spacing(p, 0, 1)
    run(p, ", ".join(x for x in [org, location] if x))
    run(p, "\t" + dates)


def pick(item: dict, tailored: dict) -> list[str]:
    """style: advisory → consultant-voice bullets (question → data → logic → recommendation → result)."""
    if tailored.get("style") == "advisory" and item.get("advisory_bullets"):
        return item["advisory_bullets"]
    return item["bullets"]


# ------------------------------------------------------------------ build
def build(tailored: dict, out: Path) -> Path:
    m = master()
    doc = Document()
    sec = doc.sections[0]
    sec.orientation, sec.page_width, sec.page_height = WD_ORIENT.PORTRAIT, Inches(PAGE_W), Inches(11)
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, Inches(MARGIN))
    st = doc.styles["Normal"]; st.font.name, st.font.size = FONT, Pt(BODY)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    c = m["contact"]; c.update({k: v for k, v in private_contact().items() if v})
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; spacing(p, 0, 1)
    run(p, c["name"].upper(), bold=True, size=16)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; spacing(p, 0, 2)
    first = True
    for piece in [c.get("phone"), c["email"]]:
        if piece:
            run(p, ("" if first else "  |  ") + piece, size=BODY - 0.5); first = False
    for l in c["links"]:
        run(p, "  |  ", size=BODY - 0.5); hyperlink(p, l["url"], l["label"], BODY - 0.5)

    header(doc, "Summary of Qualifications")
    for s in tailored["summary"]:
        bullet(doc, s)

    header(doc, "Education")
    for e in m["education"]:
        if "degree" in e:
            entry(doc, e["degree"], e["school"], e["location"], e["dates"])
        elif tailored.get("show_certs", True):
            p = doc.add_paragraph(); spacing(p, 1, 0); run(p, e["line"])

    exp = {e["id"]: e for e in m["experience"]}
    header(doc, "Work Experience")
    for x in tailored["experience"]:
        e = exp[x["id"]]
        entry(doc, e["title"], e["org"], e["location"], e["dates"])
        for b in x.get("bullets") or pick(e, tailored):
            bullet(doc, b)

    prj = {p_["id"]: p_ for p_ in m["projects"]}
    header(doc, "Projects")
    for x in tailored["projects"]:
        pj = prj[x["id"]]
        p = doc.add_paragraph(); spacing(p, 2, 0)
        run(p, pj["name"], bold=True)
        if pj.get("tag"):
            run(p, f"  ·  {pj['tag']}", italic=True, size=BODY - 0.5)
        for b in x.get("bullets") or pick(pj, tailored):
            bullet(doc, b)

    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out


def to_pdf(docx: Path) -> tuple[Path, int]:
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(docx.parent), str(docx)],
                   check=True, capture_output=True)
    pdf = docx.with_suffix(".pdf")
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    pages = next((int(l.split()[-1]) for l in info.splitlines() if l.startswith("Pages:")), 0)
    return pdf, pages


if __name__ == "__main__":
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    t = yaml.safe_load(src.read_text())
    sys.path.insert(0, str(ROOT / "src"))
    from check_facts import check
    problems = check(t)
    if problems:
        print("Blocked: these numbers are not in resume/master.yaml:\n  " + "\n  ".join(problems))
        sys.exit(1)
    build(t, out)
    print(f"built {out}")
    if "--pdf" in sys.argv:
        pdf, pages = to_pdf(out)
        print(f"{pdf.name}: {pages} page(s)")
        if pages != 1:
            print("WARNING: not one page — cut words, keep 10 pt+ text.")
            sys.exit(2)
