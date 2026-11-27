# Decisions (dated, one line each)
- 2026-11-25: Only employer-owned boards count as verified; LinkedIn/Handshake are leads until found on the employer's site
- 2026-11-25: Tailored résumés, tracker and phone stay private in ~/Job Hunts; the public repo holds code, config and master facts
- 2026-11-25: Hemi applies himself; the agent never submits applications
- 2026-11-25: Submitting applications is allowed only after Hemi's explicit approval of the exact package, presented by Tamil CEO

## 2026-11-27 · Cover letters are narrative (Hemi's rule)
- Every cover letter tells Hemi's whole story: cricket grounds in Chennai → professional opening batter (TNPL, Dindigul Dragons; still plays in the US) → engineering + marketing internship → MS Business Analytics in Boston → sports-industry advisor.
- Link the story to THIS job subtly (one image that maps cricket to the role), human and cinematic, "ready for a Google application". Treat every job seriously; read the full posting first.
- Still one page, facts only from master.yaml (`story:` section holds his own words), no invented scenes, honest about gaps.
- Build: `body:` paragraphs in resume/cover_letters.yaml → src/build_cover.py.
