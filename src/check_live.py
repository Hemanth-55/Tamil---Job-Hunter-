"""Tamil - Job Hunter · src/check_live.py

Checks that each role in "Job Hunts" is still live on the employer's own system, and pulls the
application form's questions where the system publishes them (Greenhouse).
Input: a text file of lines "NN|url" (read from each folder's Job.md). Output: JSON to stdout.

  python src/check_live.py roles.txt > live.json
"""
import json, re, sys, time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Tamil Job Hunter; verification)", "Accept": "application/json"}
GH_BOARD = {"playfly.com": "playsports", "fanduel.careers": "fanduel", "prizepicks.com": "prizepicks"}


def get(url, data=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                 headers={**UA, **({"Content-Type": "application/json"} if data else {})})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status, json.loads(r.read().decode() or "null")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(4 * (attempt + 1)); continue
            return e.code, None
        except Exception as e:  # network or parse problem
            return 0, str(e)
    return 0, None


def check(url):
    gh = re.search(r"gh_jid=(\d+)", url) or re.search(r"greenhouse\.io/([^/]+)/jobs/(\d+)", url)
    if "greenhouse.io" in url:
        board, jid = re.search(r"greenhouse\.io/([^/]+)/jobs/(\d+)", url).groups()
    elif gh:
        board, jid = next(v for k, v in GH_BOARD.items() if k in url), gh.group(1)
    else:
        board = jid = None
    if board:
        code, js = get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{jid}?questions=true")
        if code != 200 or not js:
            return {"system": "greenhouse", "live": False, "code": code}
        qs = [{"label": q.get("label"), "required": q.get("required"),
               "type": (q.get("fields") or [{}])[0].get("type"),
               "options": [v.get("label") for v in (q.get("fields") or [{}])[0].get("values", [])][:12]} for q in js.get("questions", [])]
        qs += [{"label": q.get("label") or q.get("name"), "required": q.get("required"), "type": "compliance", "options": []}
               for q in (js.get("compliance") or []) for q in (q.get("questions") or [])]
        return {"system": "greenhouse", "live": True, "title": js.get("title"), "location": (js.get("location") or {}).get("name"),
                "updated": js.get("updated_at"), "apply_url": js.get("absolute_url"), "questions": qs}
    if "ashbyhq.com" in url:
        org, jid = re.search(r"ashbyhq\.com/([^/]+)/([0-9a-f-]+)", url).groups()
        code, js = get(f"https://api.ashbyhq.com/posting-api/job-board/{org}")
        job = next((j for j in (js or {}).get("jobs", []) if j.get("id") == jid), None) if code == 200 else None
        return {"system": "ashby", "live": bool(job), "title": job and job.get("title"), "location": job and job.get("location"), "apply_url": url + "/application"}
    if "smartrecruiters.com" in url:
        comp, jid = re.search(r"smartrecruiters\.com/([^/]+)/(\d+)", url).groups()
        code, js = get(f"https://api.smartrecruiters.com/v1/companies/{comp}/postings/{jid}")
        live = code == 200 and bool(js) and js.get("active", True) is not False
        return {"system": "smartrecruiters", "live": live, "title": js and js.get("name"), "location": js and (js.get("location") or {}).get("fullLocation"), "apply_url": js and js.get("applyUrl") or url}
    if "myworkdayjobs.com" in url:
        m = re.search(r"https://([^.]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([^/]+)/job/(.+)$", url)
        tenant, wd, site, path = m.groups()
        code, js = get(f"https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/job/{path}")
        info = (js or {}).get("jobPostingInfo") if code == 200 else None
        return {"system": "workday", "live": bool(info) and info.get("canApply", True), "title": info and info.get("title"),
                "location": info and info.get("location"), "apply_url": url + "/apply", "note": "Workday needs an account: Hemi creates it and types the password"}
    return {"system": "unknown", "live": None}


if __name__ == "__main__":
    out = {}
    for line in open(sys.argv[1]):
        if "|" not in line or not line.split("|")[1].strip():
            continue
        nn, url = line.strip().split("|", 1)
        out[nn] = {"url": url, **check(url)}
        time.sleep(0.6)
    print(json.dumps(out, indent=1))
