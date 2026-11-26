---
name: apply
description: Prepare and (only after Hemi's explicit approval) submit a job application. Use when Hemi says "apply to 03", "apply to the FanDuel role", or approves an application package.
---

# Apply (approval first, always)

**Rule set by Hemi (25 Nov 2026):** Job Hunter drafts everything, Tamil CEO brings it to Hemi, and **nothing is submitted until Hemi approves that exact package**. Other agents can help (verifier, resume-tailor, quality-reviewer, Mail & Calendar); new helper agents may be created only after Hemi approves them too.

## 1 · Prepare (no approval needed)
1. Open the role's folder in `~/Desktop/Job Hunts/<NN · Company · Role>/` and its `Job.md`. Re-open the posting: still live? If closed, tell Hemi and stop.
2. Tailor the résumé to this posting (`tailor` skill, `style: advisory`), fact-checked, one page. Replace the base résumé in the folder.
3. Draft a **cover letter** (`Cover Letter.docx`, one page, consultant voice: why this company, the business problem I can help with, proof from my work, close). Facts only from `resume/master.yaml`.
4. Open the application form (his signed-in browser) and list **every question** it asks. Draft answers in `Application.md`. Leave anything personal or legal (work authorization, sponsorship, demographics, salary, references, start date) as **"Hemi to answer"** unless he has already told you the answer for applications.
5. Run the `quality-reviewer` on the résumé + cover letter.

## 2 · Approval (Tamil CEO → Hemi)
Show Hemi, in one message: role + link, the tailored résumé, the cover letter, every form answer, and anything still marked "Hemi to answer". Ask: **"Approve and submit?"** Only a clear yes from Hemi in chat counts. Edits → revise → ask again.

## 3 · Submit (only after that yes)
- Fill the employer's form in his browser with exactly the approved content and upload the approved files.
- Hemi types passwords, creates accounts and enters verification codes himself. Never solve CAPTCHAs.
- Before the final Submit click, show the filled review page and confirm once more if anything differs from what he approved.
- After submitting: screenshot or note the confirmation, set the tracker row `status: applied`, `applied_on: <date>`, save `Submitted.md` (date, what was sent) in the folder, and log it in `notes/session-log.md`.
- If a step fails (login wall, broken form), stop and tell Hemi; never retry by other means.
