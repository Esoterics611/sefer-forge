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
out, as set aside by the speaker. The speaker's addition the same day (`edits:`):
the "air" is the צלם, the source of the information from the surroundings,
between the biological stack and the soul. Same passes as parts א'–ב'; introduction.md and
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

Session 004 (2026-11-09): "עץ חיים 3.m4a" (7:05, uploaded as "עתיק חיים 3"),
box 3, Etz Chaim 39:1, in three cuts. Through the full pipeline, then condensed at
the speaker's request: the text keeps what explains the passage (prayer too
refines, העלאת מ"ן; the נר"ן rise from the kelipot), the rest is in seven notes
(`^[...]` in `teaching:`, set under their paragraphs in smaller type). Its main
point follows the speaker's correction in session 005: the garments by the
practical mitzvot, the נר"ן by prayer.

Session 005 (2026-11-09): "אבל ירידת משם.m4a" (6:19), the speaker's narration of
the Alter Rebbe's own words after הערה ג' ("אבל ירידתן משם ... ומעלה אותה עד הנקבה
העליונה כו'"), no box of its own. Its ocr.md: that stretch (the reading pack's text
from citation 3 up to the words of citation 4), then שער הגלגולים, הקדמות י"ב, י"ג,
י"א (sources/arizal/shaar-hagilgulim.he.json, added the same day at the speaker's
request: the teaching behind "כמ"ש בגלגולים פ"א"), printed with the part as quoted
sources. The speaker asked for the restarts merged into one segment and for his
reading checked against the sources before the text is finished. Box 4's
narration (`box-session.py ... 4`) starts its text at "וכ"כ בע"ח של"ט דרוש י"א":
the words before it are this session's.

Open: the slug and title are working names; the book this goes in is not chosen.
