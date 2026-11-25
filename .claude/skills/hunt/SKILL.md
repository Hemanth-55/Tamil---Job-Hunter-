---
name: hunt
description: Run Tamil - Job Hunter end to end — collect, verify, rank, tailor résumés and file them in Hemi's Job Hunts folder. Use when Hemi says "hunt", "find me jobs", "job hunt", "any new jobs?" or names a company or role to apply for.
---

# Hunt

Keep a task list: Collect → Verify → Rank → Tailor → Package → Report.

## 0 · Ready
- `git pull --rebase`. Read `resume/master.yaml`, `config/targets.yaml`, and the top of `notes/session-log.md` (what was already sent, so nothing repeats).
- Find the **Job Hunts** folder: on Hemi's Mac it is `~/Job Hunts` (in a cloud chat, through the device tools; ask him to connect it with "Add folder" if it isn't connected). Read `Job Hunts/tracker.csv` so you skip roles already packaged.
- If Hemi named a company or role, hunt only that.

## 1 · Collect
1. `data/inbox.json` is the daily scout (GitHub Actions). If `updated` isn't today, run `python src/scout.py` (about 5 minutes).
2. Widen with sources the scout can't read (see `config/sources.yaml → manual`):
   - TeamWork Online: open the analytics / sports technology / internship searches. It is the official board for team and league jobs.
   - League career sites: NBA, NFL, MLB, NHL.
   - LinkedIn and Handshake: through Hemi's signed-in browser, or search Gmail for their job-alert emails. Never scrape LinkedIn.
   - Hemi's targets in `config/targets.yaml`. Note new employer boards you find, and add them to `config/sources.yaml` after `python src/scout.py --check`.
3. Drop anything already in the tracker.

## 2 · Verify
Use the `verifier` agent (in parallel for several roles). Keep only **VERIFIED**. Note DEAD/SUSPECT in the report in one line.

## 3 · Rank
Read each full posting against `master.yaml`. Score must-haves met, level, start date (graduates 05/2027: summer-2027 internships or roles starting mid-2027), location (Boston → remote US → hubs).
Write down the honest gaps. Pick the top 5 (or what Hemi asked for). Fewer strong picks beat many weak ones.

## 4 · Tailor
Use the `resume-tailor` agent per pick, in parallel. Each YAML must pass `python src/check_facts.py` and build to **one page**. Look at each rendered page.

## 5 · Package
- On the Mac (Claude Code): `python src/package.py resume/tailored/<file>.yaml ~/"Job Hunts"`.
- In a cloud chat: run `package.py` into a local `Job Hunts/` folder in the workspace, then copy each new folder and `tracker.csv` to the Mac with the device tools. If no Mac folder is connected, send the files in chat and say so.
- Each folder holds the Word résumé, the PDF, `Job.md` (link, verification, fit, gaps, next steps) and `resume-content.yaml`.

## 6 · Report (Tanglish, short)
A table: Fit · Role · Company · Location · why in one line · link. Then gaps, then "apply pannu machi; sonna tracker update panren".
Hemi applies himself. When he says "applied to X", set that tracker row's `status` to `applied` and `applied_on` to today.

## 7 · Save
Add a dated entry to `notes/session-log.md` (roles packaged, dead/suspect ones, new boards added), commit, `git pull --rebase`, push.
Tailored YAMLs stay out of the public repo (see `.gitignore`); the Job Hunts folder is the private record.
