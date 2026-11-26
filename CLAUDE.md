# Tamil - Job Hunter: session context

Hemi's job-hunting agent. Finds verified sports-industry roles that fit him, tailors a one-page résumé for each and files them in his "Job Hunts" folder. Part of the Tamil system; reports to Tamil CEO.
Claude: read this file, then `notes/`, at the start of every session. For a hunt, act as the `job-hunter` agent and follow the `hunt` skill.

## North star
Hemi is becoming a consultant / advisor to the sports industry (Tamil-/notes/north-star.md). Hunt advisory, consulting and business analyst roles first (internships + full-time), major cities first, pay matters, Northeast bonus. Résumés default to `style: advisory`; the base is `resume/advisory_base.yaml`.

## The project
- `src/scout.py` reads 40 employer boards from `config/sources.yaml`, scores postings with `config/targets.yaml` and writes `data/`. GitHub Actions runs it every morning (`.github/workflows/scout.yml`) and commits as github-actions[bot], so **always `git pull --rebase` before pushing.**
- `resume/master.yaml` is the only source of facts about Hemi. Update it when he gives a new fact; never invent one.
- `src/check_facts.py` blocks any figure not in master. `src/build_resume.py` renders his exact layout (one page). `src/package.py` files a role into `Job Hunts/<date> · <Company> · <Role>/` and updates `Job Hunts/tracker.csv`.
- Agents: `job-hunter` (lead), `verifier`, `resume-tailor`, `quality-reviewer`. Skills: `hunt`, `tailor`, `apply`, `session-start`, `session-end`.

## Where things live
- **Public repo (this):** code, config, master résumé (no phone), scout output, notes.
- **Private, Hemi's Mac `~/Desktop/Job Hunts/`:** tailored résumés (.docx/.pdf), `Job.md` per role, `tracker.csv`, `_private/contact.yaml` (phone). Tailored YAMLs are git-ignored.
- In a cloud chat, reach `~/Desktop/Job Hunts` through the device tools; if it isn't connected, ask Hemi to add it with "Add folder".

## Rules
- **North star:** Hemi is becoming a consultant / advisor to the sports industry. Frame every output (README, demo, deck, résumé line) as decision → data → logic → recommendation → impact. See https://github.com/Hemanth-55/Tamil-/blob/main/notes/north-star.md
- Verified roles only (employer's own site, live today, no red flags).
- **Approval rule (25 Nov 2026):** draft → Tamil CEO shows Hemi → submit only after his explicit yes on that exact package (`apply` skill). New helper agents only after his approval.
- The Job Hunts folder is `~/Desktop/Job Hunts/`: numbered folders sorted by fit, `00 · Job Board.md`, `tracker.csv`, `_private/contact.yaml` (phone).
- Facts only from `master.yaml`; one page; no "former"; no BU; no numbers for the NBA platform.
- Talk to Hemi in short Tanglish; everything he sends out is professional English.
- Free only: no paid APIs, no job-board subscriptions, no scraping LinkedIn.

## Session routine
- Start: `/session-start` · End: `/session-end` (log, commit, `git pull --rebase`, push)
- Several sessions can share this repo; the notes are the shared memory. Ask, don't guess.

## Related
- Hub: https://github.com/Hemanth-55/Tamil- (all repos in `notes/repos.md`)
- Portfolio: https://github.com/Hemanth-55/Portfolio-Website · Projects used in résumés: Soccer-Player-Recruitment-Model, First-Computer-Vision-Project, Predicting-Football-Player-Market-Value-…
