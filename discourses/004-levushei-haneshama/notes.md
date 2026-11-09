# Notes — levushei-haneshama

Text: the הגהה "לשון אדמו"ר נ"ע בעצמו" (on the לבושים of the soul made by
תורה ומצוות, תפלה in פנימיות and the מצוות מעשיות in חיצוניות, the חשמל), from
chabadlibrary.org/books/3901370076, 3901370077, 3901370078, pasted by the user
on 2026-11-05. Its last paragraph is the opening of the next maamar, "ויצא יצחק
לשוח בשדה".

Session 001: the text in `ocr.md`; its sources in `references.yaml` →
`references.md` and the reading pack (`output/references/004-levushei-haneshama-001.pdf`),
to be read from while recording the lesson. 26 citations of עץ חיים and פרי עץ
חיים set out; ספר הגלגולים, טעמי המצוות, ליקוטי תורה, מקדש מלך, כוונות and the
Zohar are listed, not quoted.

Recordings (2026-11-07): session 001 also holds the introduction, הקדמה 1.m4a
and הקדמה 2.m4a (labelled parts in commentary.md; part 2 opens הערה 1). Part 1
is cut at 01:45, at the speaker's request. The introduction reads none of the
text (ocr-match finds no reading).

Addition (2026-11-09): לבאר ענין הצלם.m4a (3:34), the speaker's addition to the
introduction, in session 001 as part ג' (commentary.md "## הקדמה — חלק ג'"): the
צלם as the intermediary between the נר"ן and the body, Jung's stack from genes to
personality, the "air" in which all is written. It reads none of the text. Its
last 16 seconds (cognitive psychology, broken off, "כל זה כבר לא שייך") are left
out, as set aside by the speaker. Same passes as parts א'–ב'; introduction.md and
introduction.teaching.md carry it (`scripts/sync-opening.py`; skill
`extend-session`).

How it is made (decided 2026-11-08, after הערה 1 and 2):
- One narration per box of the reading pack (הערה N), each in its own session.
  `python scripts/box-session.py discourses/004-levushei-haneshama <N>` starts it
  (session 002 = box 1, 003 = box 2, so box 3 → 004): ocr.md from the pack,
  a starter plan. Then `ingest-session` to its end: the transcript cleaned
  faithfully, matched, laid out paired (the text's stretch labelled "לשון
  אדמו"ר נ"ע", the Etz Chaim passage set apart), `nusach.end` at the last
  sentence read, the readability, style and teaching passes.
- The pamphlet opens with the text with its box letters (text.md, from
  `build-references.py --marked-text`) and the introduction (introduction.md
  and its .teaching.md, from session 001), then one part per הערה. Reassemble
  (`assemble-discourse.py --force`: discourse.md here is only the assembled
  parts) and print (`build-pamphlet.py discourses/004-levushei-haneshama`).
- The speaker's corrections go in as `edits:` marked "the speaker's
  correction (date)".

Open: the slug and title are working names; the book this goes in is not chosen.
