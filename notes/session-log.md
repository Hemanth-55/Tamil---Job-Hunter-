# Session log (newest first)

## 2026-11-28 · Morning hunt (SportsCareers first batch)
- Packaged 4 (not submitted): Orioles · Analyst, Business Strategy ($70–90K + bonus, starts early 2027 → ask about a mid-2027 start); Orioles · Analyst, Major League Strategy & Analytics ($60–80K, baseball-specific gap); D.C. United · Analyst, CRM & Strategy (pinned); Rockies · Business Strategy Analyst. Narrative cover letters for all 4. check_facts OK, 1 page each.
- Verified: both Orioles roles via the Greenhouse API (live, no sponsorship restriction stated). D.C. United + Rockies: live in the SportsCareers feed, but TeamWork Online blocks scripts and Hemi's Mac was offline, so the full postings (and work-authorization wording) still need one read in his browser before applying.
- Skipped: Vegas Golden Knights BSA Associate (part-time, on-site Las Vegas through June 2027). Saints/Pelicans Strategy & Analytics: Dayforce page needs a browser; next time.
- Mac offline during the run: packages sent to Hemi in chat as a zip; copy into ~/Desktop/Job Hunts with tracker.csv when the Mac is back.

## 2026-11-27: SportsCareers added to the scout
- Hemi pinned D.C. United · Analyst, CRM & Strategy (TeamWork Online) → new `config/watchlist.yaml`; the hunt prepares pinned roles first.
- Done: new source `sportscareers` (sports-careers.com/api/jobs, allowed by its robots.txt; one request a run). ~3,400 team, league and sportsbook roles; each links to the employer's own application form. Scout now de-duplicates the same posting across boards. First run: 75 fits, 57 from SportsCareers (Orioles, Rockies, Dolphins, D.C. United, Fanatics, Kalshi…).
- Next: Hemi wants to start applying tomorrow: tailor packages for the top roles, Hemi approves each one before anything is submitted.

## 2026-11-27 · Batch A applications submitted
- Submitted 12 applications (FanDuel x5, Alo x2, Red Bull x2, Tonal, DICK'S x2). Skipped 3 CAA roles: postings exclude anyone needing sponsorship now or later.
- New rules: cover letters are narrative (Hemi's story → linked subtly to each role, src/build_cover.py `body:`); preferred name always just "Hemi" (Workday forces a last name).
- New: src/applied_list.py builds "Applied Jobs.md" in Job Hunts from tracker.csv; rerun after each submission.
- Answers used: authorized Yes, future sponsorship Yes (H-1B), pay = mid of posted range or $70K (DICK'S), demographics Asian/Male/not veteran, disability "prefer not". Hemi ticks arbitration/legal boxes and attaches files himself.
- Next (Fri 4 Dec, 10 PM ET, reminder set): Batch B/C not yet approved (Playfly, RBNY internships, PrizePicks); check eligibility, ask Hemi; optional fresh hunt.

## 2026-11-25 (night): New sources, board re-sorted to 19 roles
- Done: from Hemi's two sites, added 7 verified roles (Playfly Sports Consulting / Consulting & Analytics / Research & Insights / Integrated Marketing Strategy / Global Partnerships; Red Bull NY Spring 2027 Corporate Partnerships; CAA Summer 2027 Brand Management). Board re-sorted for the advisor path (01–19) in ~/Desktop/Job Hunts.
- Added to scout: Playfly (Greenhouse playsports), CAA (Workday); manual: Global Sports Jobs, The Sports Intern.
- LinkedIn: not scraped (ToS/account risk). Use job-alert emails in Gmail and a read-only look at his feed in his own browser during sessions.
- Next: 3 PM 26 Nov apply session (reminder set): Hemi picks numbers, `apply` skill, submit only after his yes.

## 2026-11-25: Job Hunts folder filled; approval-to-submit rule
- Done: 12 verified roles packaged into ~/Desktop/Job Hunts (sorted 01–12 by fit, advisory résumés with phone, Job.md, tracker, 00 · Job Board.md). Fixed Workday location bug (Accenture roles abroad leaked in).
- Decision: Job Hunter may submit applications, but only after Hemi explicitly approves the exact package via Tamil CEO (new `apply` skill).
- Next: Hemi picks roles ("apply to 03"); tailor + cover letter + answers per role.

## 2026-11-25: Red Bull New York Academy Scout (from a LinkedIn post)
- Done: traced Hemi's LinkedIn link to RBNY's Spring 2027 Academy Scout internship; verified live on Red Bull's SmartRecruiters (744000163139079, posted 2026-11-23); tailored + packaged résumé.
- Found alongside: Spring 2027 Data Science and RBII Team Analysis internships (same board, Morristown NJ).
- Added Red Bull's SmartRecruiters board to the scout; fixed country-code bug (Bogotá "co" read as Colorado); added scout/video-analysis titles to targets.
- Gaps flagged: unpaid for academic credit; in person in Morristown NJ in spring 2027; no Hudl Sportscode/Wyscout yet.

## 2026-11-25: Tamil - Job Hunter built
- Done: scout over 40 verified employer boards (Greenhouse 25, Lever 4, Ashby 6, SmartRecruiters 1, Workday 4); first run read 2,002 postings → 23 fits. Résumé engine in Hemi's layout with fact check; packaging to ~/Job Hunts; agents job-hunter, verifier, resume-tailor; skills hunt, tailor; daily GitHub Action.
- Example: FanDuel Campaign Analytics Data Analyst résumé built (1 page, facts checked).
- Next: Hemi creates ~/Job Hunts and connects it; confirms targets (internship vs full-time, locations, sponsorship filter); first full hunt.
