"""Tamil - Job Hunter · scout

Reads sports organizations' own job boards (Greenhouse, Lever, Ashby, SmartRecruiters, Workday),
keeps the roles that fit Hemi, scores them, and writes:
  data/inbox.json   every matching open role, best first
  data/seen.json    when each role was first seen (so "new" means new)
  data/latest.md    today's short list, readable on GitHub or a phone

Every posting comes from the employer's own hiring system, with the employer's own apply link.
Nothing is scraped from aggregators, so nothing here can be a fake listing.

Usage:
  python src/scout.py            full run
  python src/scout.py --check    only confirm each board in config/sources.yaml still resolves
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config"
DATA = ROOT / "data"
UA = {"User-Agent": "Mozilla/5.0 (Tamil-Job-Hunter; +https://github.com/Hemanth-55/Tamil---Job-Hunter-)",
      "Accept": "application/json"}
TODAY = dt.date.today()


# ---------------------------------------------------------------- http
def fetch(url: str, body: dict | None = None, tries: int = 4) -> dict | list | None:
    data = json.dumps(body).encode() if body is not None else None
    headers = dict(UA, **({"Content-Type": "application/json"} if body is not None else {}))
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:                       # rate limited: back off and retry
                time.sleep(4 * (i + 1))
                continue
            if e.code == 404:
                return None
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return None


def text(s: str | None) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def job(company, group, source, jid, title, location, url, posted=None, desc=""):
    return {"id": f"{source}:{jid}", "company": company, "group": group, "source": source,
            "title": (title or "").strip(), "location": (location or "").strip(), "url": url,
            "posted": posted, "description": desc}


# ---------------------------------------------------------------- boards
def greenhouse(b):
    js = fetch(f"https://boards-api.greenhouse.io/v1/boards/{b['slug']}/jobs?content=true")
    for j in (js or {}).get("jobs", []):
        yield job(b["name"], b["group"], "greenhouse", j["id"], j.get("title"),
                  (j.get("location") or {}).get("name"), j.get("absolute_url"),
                  (j.get("updated_at") or "")[:10] or None, text(j.get("content")))


def lever(b):
    js = fetch(f"https://api.lever.co/v0/postings/{b['slug']}?mode=json")
    for j in js or []:
        posted = dt.date.fromtimestamp(j["createdAt"] / 1000).isoformat() if j.get("createdAt") else None
        cats = j.get("categories") or {}
        yield job(b["name"], b["group"], "lever", j["id"], j.get("text"), cats.get("location"),
                  j.get("hostedUrl"), posted,
                  " ".join([j.get("descriptionPlain") or ""] +
                           [text(l.get("content")) for l in j.get("lists") or []]))


def ashby(b):
    js = fetch(f"https://api.ashbyhq.com/posting-api/job-board/{b['slug']}?includeCompensation=true")
    for j in (js or {}).get("jobs", []):
        if not j.get("isListed", True):
            continue
        yield job(b["name"], b["group"], "ashby", j["id"], j.get("title"), j.get("location"),
                  j.get("jobUrl"), (j.get("publishedAt") or "")[:10] or None,
                  j.get("descriptionPlain") or text(j.get("descriptionHtml")))


def smartrecruiters(b):
    offset = 0
    while True:
        js = fetch(f"https://api.smartrecruiters.com/v1/companies/{b['slug']}/postings?limit=100&offset={offset}")
        rows = (js or {}).get("content", [])
        for j in rows:
            loc = j.get("location") or {}
            yield job(b["name"], b["group"], "smartrecruiters", j["id"], j.get("name"),
                      ", ".join(x for x in [loc.get("city"), loc.get("region"), loc.get("country")] if x),
                      f"https://jobs.smartrecruiters.com/{b['slug']}/{j['id']}",
                      (j.get("releasedDate") or "")[:10] or None, "")
        offset += 100
        if not rows or offset >= (js or {}).get("totalFound", 0):
            break


WD_QUERIES = ["analyst", "analytics", "data", "intern", "machine learning", "insights"]


def workday(b):
    base = f"https://{b['tenant']}.wd{b['wd']}.myworkdayjobs.com"
    api = f"{base}/wday/cxs/{b['tenant']}/{b['site']}/jobs"
    seen = set()
    for q in WD_QUERIES:
        js = fetch(api, {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": q})
        time.sleep(1.5)
        for j in (js or {}).get("jobPostings", []):
            path = j.get("externalPath")
            if not path or path in seen:
                continue
            seen.add(path)
            yield job(b["name"], b["group"], "workday", f"{b['tenant']}{path}", j.get("title"),
                      j.get("locationsText"), f"{base}/{b['site']}{path}", relative_date(j.get("postedOn")), "")


def relative_date(s: str | None) -> str | None:
    """Workday says 'Posted Today' / 'Posted 3 Days Ago' / 'Posted 30+ Days Ago'."""
    if not s:
        return None
    s = s.lower()
    if "today" in s:
        return TODAY.isoformat()
    if "yesterday" in s:
        return (TODAY - dt.timedelta(days=1)).isoformat()
    m = re.search(r"(\d+)\+?\s*day", s)
    return (TODAY - dt.timedelta(days=int(m.group(1)))).isoformat() if m else None


READERS = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby,
           "smartrecruiters": smartrecruiters, "workday": workday}


# ---------------------------------------------------------------- scoring
def has(hay: str, words) -> list[str]:
    return [w for w in words if re.search(r"(?<![a-z])" + re.escape(w.strip()) + r"(?![a-z])", hay)]


SKILLS = ["python", "sql", "tableau", "excel", "machine learning", "statistics", "statistical", "scikit-learn",
          "pandas", "computer vision", "opencv", "modeling", "modelling", "regression", "forecast", "power bi",
          "a/b test", "experimentation", "causal", "gcp", "google cloud", "sap", "generative ai", "llm", "dashboards"]


def score(j: dict, t: dict) -> tuple[int, list[str]]:
    title, loc = j["title"].lower(), (j["location"] or "").lower()
    desc = j["description"].lower()
    why = []
    if has(title, t["exclude_titles"]):
        return 0, ["excluded title"]
    is_intern = bool(has(title, ["intern", "internship", "co-op", "fellow"]))
    if has(title, t["levels"]["avoid"]) and not is_intern:
        return 0, ["too senior"]

    s = 0
    core_t, adj_t = has(title, t["roles"]["core"]), has(title, t["roles"]["adjacent"])
    if non_us(loc):
        return 0, ["outside the US"]
    if core_t:
        s += 40; why.append("role: " + core_t[0])
    elif adj_t:
        s += 25; why.append("role: " + adj_t[0])
    elif "analyst" in title and len(has(desc, SKILLS)) >= 3:
        s += 20; why.append("analyst role with data skills")
    else:
        core_d = has(desc, t["roles"]["core"])
        if len(core_d) >= 2:
            s += 12; why.append("analytics work in description")
        else:
            return 0, ["not an analytics role"]

    lv = has(title, t["levels"]["want"])
    if is_intern:
        s += 25; why.append("internship / fellowship")
    elif lv:
        s += 20; why.append("level: " + lv[0])
    elif not has(title, t["levels"]["avoid"]):
        s += 8                                        # unlabeled level: often mid, sometimes entry

    if has(loc, t["locations"]["prefer"]) or not loc:
        s += 15; why.append("location: " + (loc or "unspecified"))
    elif has(loc, t["locations"]["ok"]):
        s += 8; why.append("location: " + loc)
    elif non_us(loc):
        return 0, ["outside the US"]
    elif re.search(r"\b(uk|united kingdom|london|ireland|dublin|india|germany|australia|canada|toronto|"
                   r"spain|france|netherlands|bulgaria|sofia|estonia|singapore|brazil|mexico|philippines)\b", loc):
        return 0, ["outside the US"]

    sk = has(desc, SKILLS)
    if sk:
        s += min(15, 2 * len(sk)); why.append("skills: " + ", ".join(sk[:5]))
    if re.search(r"\b(sports?|athlet|fan|league|team|game|player)", desc + " " + title):
        s += 5
    if re.search(r"\b(phd required|ph\.d\. required|5\+ years|7\+ years|10\+ years)", desc):
        s -= 15; why.append("asks for heavy experience")
    return max(0, min(100, s)), why


NON_US = ("uk", "united kingdom", "england", "scotland", "london", "edinburgh", "ireland", "dublin", "india",
          "germany", "munich", "leipzig", "austria", "vienna", "wien", "switzerland", "zurich", "australia", "sydney",
          "canada", "toronto", "ontario", "spain", "france", "paris", "netherlands", "amsterdam", "bulgaria", "sofia",
          "estonia", "tallinn", "singapore", "brazil", "mexico", "philippines", "muntinlupa", "greece", "athens",
          "slovenia", "ljubljana", "norway", "trondheim", "uruguay", "montevideo", "finland", "helsinki", "oulu",
          "qatar", "doha", "china", "shanghai", "japan", "tokyo", "hong kong", "italy", "poland", "portugal", "lisbon",
          "israel", "tel aviv", "south africa", "new zealand", "colombia", "argentina", "turkey", "uae", "dubai")


def non_us(loc: str) -> bool:
    """True when every place listed is outside the US."""
    if not loc:
        return False
    parts = [p.strip() for p in re.split(r"[;|/]", loc) if p.strip()]
    def outside(p):
        m = re.search(r",\s*([a-z]{2})$", p)               # SmartRecruiters style 'Vienna, at'
        if m and p.count(",") >= 2:                          # 'city, region, country': last part is the country
            return m.group(1) != "us"
        if m and m.group(1) not in ("us", "ma", "ny", "nj", "ca", "tx", "fl", "ga", "il", "wa", "co", "pa", "nc",
                                     "dc", "va", "md", "oh", "mi", "az", "or", "mn", "tn", "ne", "mo", "ky", "ut",
                                     "nv", "wi", "in", "ct", "ri", "nh", "la", "sc", "al", "ok", "ia", "ks"):
            return True
        return bool(has(p, NON_US)) and not has(p, ["united states", "usa", "us-remote", "remote - us"])
    return all(outside(p) for p in parts)


def fresh(j: dict, max_age: int) -> bool:
    try:
        return (TODAY - dt.date.fromisoformat(j["posted"])).days <= max_age
    except Exception:
        return True


# ---------------------------------------------------------------- main
def boards():
    src = yaml.safe_load((CFG / "sources.yaml").read_text())
    for kind, reader in READERS.items():
        for b in src.get(kind) or []:
            yield kind, b, reader


def check() -> int:
    bad = 0
    for kind, b, reader in boards():
        n = sum(1 for _ in reader(b))
        print(f"{'OK ' if n else '?? '} {kind:15} {b['name']:34} {n} open roles")
        bad += n == 0
    return bad


def main():
    t = yaml.safe_load((CFG / "targets.yaml").read_text())
    DATA.mkdir(exist_ok=True)
    seen_path = DATA / "seen.json"
    seen = json.loads(seen_path.read_text()) if seen_path.exists() else {}
    found, stats = [], []
    for kind, b, reader in boards():
        n = kept = 0
        for j in reader(b):
            n += 1
            s, why = score(j, t)
            if s >= t["min_score"] and fresh(j, t["max_age_days"]):
                j.update(score=s, why=why, first_seen=seen.get(j["id"], TODAY.isoformat()))
                j["description"] = j["description"][:4000]
                found.append(j); kept += 1
        stats.append((b["name"], n, kept))
        print(f"{b['name']:34} {n:4} open  {kept:3} fit", flush=True)

    found.sort(key=lambda j: (-j["score"], j["company"]))
    for j in found:
        seen.setdefault(j["id"], j["first_seen"])
    (DATA / "inbox.json").write_text(json.dumps(
        {"updated": TODAY.isoformat(), "count": len(found), "jobs": found}, indent=1))
    seen_path.write_text(json.dumps(dict(sorted(seen.items())), indent=0))

    new = [j for j in found if j["first_seen"] == TODAY.isoformat()]
    lines = [f"# Job Hunter · {TODAY:%d %b %Y}", "",
             f"**{len(found)}** open roles fit · **{len(new)}** new today · "
             f"{sum(s[1] for s in stats):,} postings read from {len(stats)} employer boards", "",
             "| Fit | Role | Company | Location | Posted |", "|:-:|---|---|---|---|"]
    for j in (new or found)[:40]:
        lines.append(f"| {j['score']} | [{j['title']}]({j['url']}) | {j['company']} | {j['location'] or '—'} | {j['posted'] or '—'} |")
    lines += ["", "<sub>Every link goes to the employer's own job board. Résumés are tailored in a Claude session: "
              "say \"Tamil, hunt\".</sub>"]
    (DATA / "latest.md").write_text("\n".join(lines) + "\n")
    print(f"\n{len(found)} fit, {len(new)} new → data/inbox.json, data/latest.md")


if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv else main())
