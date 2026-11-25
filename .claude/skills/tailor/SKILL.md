---
name: tailor
description: Tailor Hemi's one-page résumé to one specific job posting (a link or pasted text) and package it. Use when Hemi says "tailor my resume for…", "make a resume for this job" or shares a job link.
---

# Tailor one résumé

1. Get the posting: open the link (or use the pasted text). Verify it with the `verifier` rules if it came from LinkedIn, Handshake or a friend.
2. Use the `resume-tailor` agent to write `resume/tailored/<YYYY-MM-DD>_<company>_<role>.yaml` from `resume/master.yaml` only.
3. `python src/check_facts.py <yaml>` must say OK. `python src/build_resume.py <yaml> /tmp/check.docx --pdf` must print 1 page. Look at the page.
4. Package with `python src/package.py <yaml> ~/"Job Hunts"` (or the cloud route in the `hunt` skill).
5. Show Hemi the summary bullets, which projects you picked and why, and any gaps. He approves or edits; never send it anywhere yourself.
If Hemi gives a new fact (new project, result, role), add it to `resume/master.yaml` first, then tailor.
