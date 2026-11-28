# Tamil · Job Hunter

**An AI agent that finds verified sports-industry roles that fit me, and writes a tailored one-page résumé for each.**

| Employer boards read daily | Postings screened (first run) | Roles that fit | Fake listings possible |
|:-:|:-:|:-:|:-:|
| **40** | **2,002** | **23** | **0** |

<sub>First run, 25 Nov 2026. Every posting is read from the employer's own hiring system, so a listing can't be fake.</sub>

## Why

Sports jobs are scattered across team sites, league boards, sports-tech startups and brands. Most aggregators repost stale or fake listings, and a generic résumé gets filtered out. Job Hunter does the slow parts: it reads the employers' own boards every morning, keeps only roles that match my level and skills, checks each one is live, and tailors my résumé to the posting using only facts I've already proven.

It is part of **Tamil**, my personal agent system built on Claude, and reports to Tamil CEO.

## How it works

| Stage | What happens | Where |
|---|---|---|
| **1 · Scout** | Reads the SportsCareers feed and 40 sports employers' job boards (Greenhouse, Lever, Ashby, SmartRecruiters, Workday) and scores every posting for role, level, location and skills | `src/scout.py`, daily on GitHub Actions |
| **2 · Widen** | Adds team and league roles from TeamWork Online and league career sites, plus LinkedIn and Handshake leads | Claude session |
| **3 · Verify** | Keeps a role only if it is live on the employer's own site, on the employer's domain, with no scam signals | `verifier` agent |
| **4 · Rank** | Reads the full posting against my real experience and lists the honest gaps | `job-hunter` agent |
| **5 · Tailor** | Writes a one-page résumé for the role from my master résumé, then blocks any number that isn't in it | `resume-tailor` agent, `src/check_facts.py` |
| **6 · Package** | Saves the Word and PDF résumé, the posting and a tracker row into my "Job Hunts" folder | `src/package.py` |

I review every résumé and apply myself. The agent never submits anything.

## The scout

| | |
|---|---|
| **Sources** | **SportsCareers** (sports-careers.com: ~3,400 team, league and sportsbook roles in one public feed, each linking to the employer's own application form), plus teams and leagues (Boston Red Sox, Fenway Sports Group, MLS, Monumental), sports data and tech (Sportradar, Genius Sports, Hudl, Catapult, KINEXON, Teamworks), betting and fantasy (DraftKings, FanDuel, PrizePicks, Underdog), media (Disney/ESPN, The Athletic), brands and wearables (Nike, Fanatics, WHOOP, Strava, Oura) |
| **Role match** | Sports, data, ML and computer vision titles score highest; adjacent analytics roles score lower; retail, warehouse and part-time roles are removed |
| **Level** | Internships, fellowships, analyst, associate and new-grad roles score up; senior, staff, lead and manager roles are removed |
| **Location** | Boston first, then remote US, then US sports hubs; roles that are only outside the US are removed |
| **Output** | `data/latest.md` (today's list), `data/inbox.json` (all fits, best first), `data/seen.json` (when each role first appeared) |

Workday boards rate-limit bursts, so the scout backs off and retries. Boards that block scripts (TeamWork Online) or need my login (LinkedIn, Handshake) are read by the agent in a browser instead.

## Résumés that stay true

- **One source of truth.** `resume/master.yaml` holds every fact, number and project I can stand behind.
- **Fact check.** `src/check_facts.py` stops the build if a tailored résumé contains a figure that isn't in the master file.
- **One layout.** `src/build_resume.py` renders my house style in Word: Arial, one page, centered header with live links, ruled section headers, dates right-aligned.
- **Private by default.** Tailored résumés, my phone number and the application tracker live only in my "Job Hunts" folder, not in this public repo.

## Run it

```bash
pip install -r requirements.txt
python src/scout.py                     # read every board, write data/
python src/scout.py --check             # confirm each board still resolves
python src/check_facts.py resume/tailored/<role>.yaml
python src/package.py resume/tailored/<role>.yaml ~/Desktop/"Job Hunts"
```

Or in a Claude session on this repo, say **"Tamil, hunt"**.

## Repository structure

```
.
├── src/
│   ├── scout.py          # reads employer boards, scores and ranks roles
│   ├── build_resume.py   # tailored YAML → one-page Word résumé (+ PDF)
│   ├── check_facts.py    # blocks any number not in the master résumé
│   └── package.py        # files a role into "Job Hunts" with résumé, posting and tracker row
├── config/
│   ├── sources.yaml      # the employer boards, each checked to exist
│   └── targets.yaml      # what a good role looks like for me
├── resume/master.yaml    # every fact the résumés may use
├── data/                 # daily scout output
├── .claude/              # the agents (job-hunter, verifier, resume-tailor) and skills (hunt, tailor)
└── .github/workflows/scout.yml
```

<sub>Hemanth Kumar Gopi · <a href="https://hemanthkumargopi.vercel.app">hemanthkumargopi.vercel.app</a> · Built with Claude · Free to run: GitHub Actions, no paid APIs</sub>
