# Independent check — the explanation of Shacharit after the Arizal (005, level 1)

2026-11-13. Three subagents that had not seen the writing each took a third of the built
`biur.md` (A: מבוא, §1–§3 · B: §4–§8 · C: §9–סיכום) and tried to break every claim against
the reading pack and `scripts/source-lookup.py`. Their full reports follow, unchanged.

**Result:** 1 serious, 15 moderate, 19 minor findings (A: 0/4/4, B: 0/5/7, C: 1/6/8). The
gematria and the quotations inside the prose were otherwise found letter for letter.

## What was done (in `biur.src.md`, 2026-11-13)

Every finding was applied, as a correction or as a stated disagreement of the sources, except
where noted. Nothing waits in `checks.yaml`.

- **C1 (serious), §13:** the two bursts at the Torah reading now follow the account both works
  prefer (יסוד אימא = ההיכל, יסוד ז"א = תיק הספר; SK Torah Reading.1.4 "היותר אמיתי אצלי", PEC
  1.5), quoted; the other account is named as the doubtful one.
- **A1:** what is fixed "ממילא" in the world below is its חיצוניות (מבוא, §1, §2).
- **A2:** the two counts of the eighteen blessings no longer divided by work.
- **A3:** the contradiction on the small tallit (SK Tzitzit 6.3 vs Prayers 3.3) stated in §2.
- **A4:** the knot of the head tefillin: לאה in SK, the מקיף of רחל in PEC, both stated in §3.
- **A5–A8:** the eight threads; "מבואר" for "מפורש"; "גם הוא אחור באחור"; the second wording of
  the בריאה/אצילות boundary in the מבוא.
- **B1:** the separating amens (three, besides אמן יש"ר; the last is "ואמרו אמן").
- **B2:** the contradiction of Shema 6.4.4 and 8.1.23 (who receives mochin, who garments)
  stated in §8; all eight lights first to Yaakov.
- **B3:** speech begins with the morning blessings, the rising itself from the עקידה.
- **B4:** צדקה at "כי כל בשמים ובארץ", with "ואתה מושל בכל" as the second report.
- **B5:** the קטורת before and after the prayer: a reason for each.
- **B minor:** R. Chaim Vital's recollection marked as such; "אז" = 8; "חוץ מן הפנימיים של
  הקטנות"; Rachel only begins to rise to היכל ק"ק; "פרצו'"; "מלכא עלאה". Not changed: B "6.2
  fuses the reasons of MP.2 and MP.6" — §6 now gives the second reason as "מטעם נוסף שבדרוש".
- **C2:** the reconciliation of the בריאה/אצילות boundary presented as a connection, with SK
  Standing Prayer.2.1.3.
- **C3:** the rise in the repetition is completed by the קדושה, which lights Rachel's דעת.
- **C4:** the second division of the drop (SK Standing Prayer.6.1.26) stated in §11.
- **C5:** "אליך" in נפילת אפים: the reading of the נפילת אפים gate (the נוקבא), the Shema
  reading (ת"ת) as the other.
- **C6, C7:** the סיכום: no kaddish between בריאה and אצילות; the sentence on the Rashash removed.
- **C minor:** "באהבה" before "מלך עוזר"; Yaakov in חסד also in SK; the text's own reason for
  the repetition (האם זוקפת); "תחלה"; "ומסמא את עיניהן"; the שעיר departs by the portion; the
  removal of the tefillin (the two passages differ on the order, so only hand sitting / head
  standing is stated); the second account of the middle blessings (6.1.3).

## What waits for Ronnie
- Part 3 (§9–§13) rests on selected passages (`notes/open-questions.md`, "Part 3").
- The disagreements the explanation now states openly (Rachel's point; the small tallit; the
  knot; who receives mochin in ק"ש; the order of removing the tefillin) are not decided.

---


# Report A

## Check A: biur.md, the מבוא and §1–§3

Scope: discourses/005-kavanot-shacharit/biur-arizal/biur.md, from "## מבוא" up to "### 4.". Each claim was checked against the reading pack (00–03) and source-lookup. No file in the repository was edited.

Counts: serious 0 · moderate 4 · minor 4.

## Findings

1. **מבוא.19, 1.19, 2.25: what is fixed "of itself" in the world below** (moderate)
   - **Claims:**
     - מבוא.19: "וכשנתקנות שלוש האחרונות של עולם, נתקנות ממילא הספירות העליונות של העולם שתחתיו."
     - 1.19: "כשנתקנות בה שלוש האחרונות של היצירה, נתקנות ממילא גם שבע הספירות העליונות של העשיה".
     - 2.25: "בציצית נתקנה אפוא היצירה במקומה, ועמה העשיה כולה".
   - **Problem:** The text says that what is fixed of itself is the outer side (חיצוניות) only. The inner side (פנימיות) of the seven upper sefirot is fixed only one stage later. As written, these three sentences say the whole of the world below is fixed. 2.2 states it correctly ("שבע העליונות בחיצוניותן בלבד"), so the biur also disagrees with itself.
   - **Evidence:**
     - SK Sermons on Morning Prayers.3.3: "ממילא נתקנו כל הי"ס שבעשי' ... אמנם לא נתקנו רק בבחי' חיצוניות' בלבד ... וז' עליונות דעשיה בבחינת חיצוניות בלבד".
     - SK Sermons on Morning Prayers.3.4 (only at תש"י): "וגם נתקנו הפנימיות דז' עליונות דעשיה".
   - **Suggested correction:** Add "בחיצוניותן בלבד" in מבוא.19 and 1.19. Add "ופנימיות שבען העליונות נתקנת רק בתפילין של יד" (or similar). In 2.25 write "ועמה חיצוניות שבע העליונות של העשיה" in place of "העשיה כולה".

2. **1.13: the two ways of counting the eighteen blessings, split by work** (moderate; flagged claim 4)
   - **Claim:** "בשער הכוונות, וכן בשער התפילה שבפרי עץ חיים, שמונה עשרה הברכות נמנות מ"על נטילת ידים" ... בשער הברכות שבפרי עץ חיים, כאן, שמונה עשרה נמנות מ"הנותן לשכוי בינה"".
   - **Problem:** In שער הכוונות the split holds: it counts from ענ"י every time (Morning Prayers.1.2, Morning Blessings.7). In פרי עץ חיים it does not hold. Each of the two gates counts both ways, and the paragraph the biur quotes is internally inconsistent.
   - **Evidence:**
     - PEC Gate of Prayer.6.14 counts from ענט"י: "ח"י ברכאן דשחרית, מן ענט"י עד ברכת התורה".
     - PEC Gate of Prayer.7.57 continued in 7.55 counts the same way as שער הברכות: "ואחר כך ח"י ברכאין ... אחרנין, שיש מן הנותן לשכוי בינה, עד סוף ברכת התורה".
     - PEC Gate of Blessings.4.2 counts from ענ"י: "הח"י ברכות וברכות שיש מן ענ"י עד ברכת התורה". 4.3 and 7.2 count from הנותן לשכוי.
     - PEC Gate of Blessings.5.1 is headed "כוונות כוללות עשרים ברכות של שחר ... מן ענט"י עד סוף ברכות התורה", but it lists 3 + 18 = 21. The quoted block starts with "…", which cuts off this heading.
   - **Suggested correction:** Say that שער הכוונות consistently counts from "על נטילת ידים". Say that both gates of פרי עץ חיים have both counts: from ענט"י in Prayer 6.14 and Blessings 4.2; from "הנותן לשכוי" in Prayer 7.55/7.57 and Blessings 4.3, 5.1 and 7.2. Mention 5.1's own "עשרים". Alternatively, drop the attribution to whole works.

3. **2.2, 2.5–2.6: whether the small tallit is the inner or the outer side of יצירה** (moderate; bears on flagged claim 5)
   - **Claims:**
     - 2.2: "הטלית הקטן ... כנגד פנימיותן".
     - 2.5–2.6: "מכאן מתיישב שהטלית הקטן נמנה פעם בעשיה ופעם ביצירה ... הקטן הוא היצירה בקטנותה".
   - **Problem:** The paragraph quoted in 2.5 (SK Tzitzit 6.3) opens by citing the order of Shacharit for the opposite of 2.2: the small tzitzit is in the outer side of יצירה, not the inner. The block starts with "… ובמקום אחר", just after that clause, so the contradiction between the two gates is never shown. What 2.6 then says is itself sound: the small tallit is יצירה in its קטנות, and that קטנות is עשיה.
   - **Evidence:**
     - SK Sermons on Tzitzit.6.3: "והנה בענין הטלי' קטן צריך שתדע מה שית"ל בסדר עליית התפילה של שחרית דחול ... ושם נת' כי ציצית קטן הוא בחיצו' היצירה ולא בפנימיות ובמקום אחר אנו מוצאין כי ציצית קטן הוא בעשי'".
     - SK Sermons on Morning Prayers.3.3: "הטלית קטן הוא כנגד פנימיו' ג' תחתונות דיצירה ... והטלית גדול הוא כנגד חיצוניותם".
   - **Suggested correction:** Note the disagreement. 3.3 places the small tallit at the inner side; Tzitzit 6.3 reports the same order as placing it at the outer side. Leave it unresolved, or start the quoted block of 6.3 one clause earlier.

4. **3.14: whose the knot of the head tefillin is** (moderate)
   - **Claim:** "הקשר של ראש הוא לאה, ותפילין של יד רחל. ובפרי עץ חיים נתבאר איך נעשית הד' שבקשר".
   - **Problem:** The PEC chapter quoted next (Gate of Teffilin.5.1–5.3) ends by calling this same ד' of the knot Rachel's encircling light (אור מקיף). So the passage brought in support of "the knot is Leah" names Rachel. Leah is supported by שער הכוונות (Morning Prayers.2.2, "לאה היא בבחי' הקשר דתש"ר") and by the line in Tefillin, but the conflict goes unmentioned.
   - **Evidence:** PEC Gate of Teffilin.5.3: "ודע, כי בחי' ד' זו שהוא הקשר של תפלה של ראש, היא בחי' א"מ עצמה של המלכות הנקראת רחל, שהוא עומד כאן למעלה, ומכאן הוא מקיף אליה".
   - **Suggested correction:** Add that in פרי עץ חיים the ד' of the knot is "אור מקיף של רחל", against שער הכוונות, where the knot is לאה. Alternatively, do not present 5.1 as an account of Leah's knot.

5. **2.14: "ארבע הציציות ושמונת החוטים שבכל אחת הם מה שזעיר אנפין נותן לנוקבא"** (minor)
   - **Problem:** Of the eight threads, four are the four plain letters (אותיות פשוטות) of her own הוי"ה, which she had before ז"א came to her. Only the filling (מילוי) is what he gives. 2.15 states this correctly, so the topic sentence overstates.
   - **Evidence:** SK Sermons on Tzitzit.1.2: "הנוק' דז"א לא היה לה בתחי' רק הוי"ה א' פשו' בד' אותיות בלבד ואחר שבא עליה ז"א יהיב בה ... מילוי ההוי"ה".
   - **Suggested correction:** Write "הם הוי"ה שלה עם המילוי שזעיר אנפין נותן בה".

6. **מבוא.27: "ובפרי עץ חיים מפורש באיזו בחינה שלהם הוא נעשה [זיווג העמידה]"** (minor; flagged claim 3)
   - **Problem:** 7.46 speaks of "תפלת שחרית דחול" generally. It says פב"פ, not זיווג, and does not name the עמידה. Placing it at the עמידה is an inference, though a fair one: from 7.45 ("ובעמידה חוזרת פב"פ") and from 7.54, whose "ואחר כך בחזרת התפלה" shows that its first sentence is the silent עמידה. "מפורש" overstates.
   - **Suggested correction:** Write "ובפרי עץ חיים מבואר..." and cite 7.45 with it.
   - **The ישראל/יעקב sentence in מבוא.28 is sound** against PEC 7.47:
     - "ראשו ... סתומים בנה"י של בינה ... לאה היוצאת משם";
     - "רחל, היוצאת אחר גילוי החסדים מן יסוד בינה שהוא בחזה דז"א";
     - "מקום הפרש בין יעקב לישראל שהוא מהחזה ולמטה".

7. **3.18: the Rosh Hashana version** (minor)
   - **Claim:** "...והיא לבדה עולה בברכת אבות עד כתר זעיר אנפין, אחור באחור, ואחר כך נעשית פרצוף".
   - **Problem:** The source adds that the פרצוף, too, is made back to back, and the biur drops this. The source of the remark is SK Tefillin.5.9 (5.6 hints at it). The block shown in §3 is 5.8.
   - **Evidence:** SK Sermons on Tefillin.5.9: "והיא לבדה עולה בברכת אבות עד הכת' דז"א אחור באחור ואח"כ נעשית פרצוף ג"כ בבחי' אחור באחור".
   - **Suggested correction:** Add "גם הוא אחור באחור" and name 5.9.

8. **מבוא.8: the first statement of the division** (minor)
   - **Claim:** "מ"יוצר אור" עד העמידה עולם הבריאה, והעמידה עולם האצילות".
   - **Problem:** The block just above says "מן יוצר אור עד סוף ברכת אבות הוא עולם הבריאה ושאר כל העמידה הוא עולם האצילות". The next sentence qualifies the statement, but read alone it contradicts the quotation. (SK 1.3 later does say "ומשם עד תפלת י"ח הוא עולם הבריאה", so both phrasings exist.)
   - **Suggested correction:** Write "מ'יוצר אור' עד סוף ברכת אבות, ושאר העמידה עולם האצילות". Alternatively, open by saying that the דרוש has both phrasings.

## Flagged claims checked and found sound

- **1. מבוא.10 (SK Morning Prayers.1.2): sound.**
  - "והנה יש בה קלי' קשות וחזקות לכן צריך ליחד תחילה ראש היצירה בראש העשיה ואח"כ שאר היצירה הוא מתתא לעילא". Here "בה" is עשיה.
  - The sequence fits the order of the prayer: הודו–ב"ש is ראש העשיה, ב"ש is ראש היצירה (היכל ק"ק), and the ח"י שמהן of יהי כבוד is the יסוד of יצירה.
  - "אין מחברים אותה אל תחתית היצירה" is a fair paraphrase of "תחילה ראש היצירה".
- **2. מבוא.19 (SK Morning Prayers.3.2–3.4): sound line by line,** except the "ממילא" sentence (finding 1). Checked:
  - נט"י and the outer side, יפנה and the inner side of the last three sefirot of עשיה;
  - the two blessings as אור מקיף, with the quotation "כי כל מצוה הנעשית בדיבור ובהבל הפה הוא בחי' אור מקיף" letter for letter;
  - two טליתות for יצירה, תש"י for בריאה (outer side only), תש"ר for the last three of אצילות (the inner light of the outer side only, its מקיף made of itself, Ashkenazim blessing);
  - the קליפות gripping less at each higher world.
- **3. מבוא.27–28 (PEC 7.46/7.54/7.47):** sound in substance (see finding 6 for the word "מפורש"). יעקב בנצח, רחל בהוד, זיווג ביסוד, לאה with ישראל back to back: all correct.
- **4. 1.13:** see finding 2. The SK side and the quotation "לפי שכולם הם רמזים נפלאים אל אורות עליונים" (SK Morning Blessings.7) are exact.
- **5. 2.15:** the four fringes as the four fillings of מילוי ההי"ן is sound, including the source's own correction "כפי האמת אינם רק [ד'] מילוים כי ... ו"ד הראשו' הם מילוי אות א'". So are the eight threads, the five knots as the five חסדים and the four spaces as the four plain letters. "The small tallit is יצירה in its קטנות" (2.6) matches SK Tzitzit 6.3; see finding 3 for the unshown contradiction.
- **6. 3.11–3.12 (SK Tefillin 5.3–5.6): sound.**
  - The רשימו of ז"א goes up at nightfall; Rachel's goes into his chest ("שימני כחותם על לבך").
  - At midnight the tenth sefira (= כתר) goes down to היכל ק"ק דבריאה and the nine join Leah.
  - In the morning Leah shrinks and the nine go down to בי"ע. The point goes up to אצילות, helped by Torah study after midnight.
  - It is tied on the left arm (גבורה) at the קיבורת, facing the heart.
- **6b. 3.21–3.22 (SK Tefillin 6.2): sound.**
  - Rashi from the mochin of אימא and Rabbenu Tam from those of אבא; wide and narrow יסוד and the order of the passages.
  - Rashi's placed first because אימא's mochin enter first.
  - The Arizal wore both together in the morning.
- **Other checks (sound):**
  - Gematria: ענ"י = ק"ל; 13 words in ענט"י; 14×3 = מ"ב; מלבוש = חשמ"ל = 378; יה"ו ו"ה = ל"ב = ר"ת "להתעטף בציצית"; אהי"ה+הוי"ה+אדנ"י = יב"ק; אהי"ה+הוי"ה+אהי"ה = חיים; together ק"ף = ע"ב+ס"ג+מ"ה; 21 אזכרות = 3×7.
  - The quotations in the prose: "לפי שעיקר הכונה היא לכלול ולקשר עולם בעולם"; the 3.5 quotation in מבוא.21; "א"א להתקיים אפילו שעה אחת"; "נכלל עמהם" / "עולים ונכללי'". All letter for letter.
  - מבוא.29 (the Arizal's own practice): matches PEC Gate of Blessings.4.2.
  - 3.23 (רוח/נפש before tefillin): matches the tefillin pack, lines 464 and 792.
  - מבוא.8 "וכן בפרי עץ חיים": matches PEC Gate of Prayer.6.4.

# Report B

## Check B — biur-arizal/biur.md, §4–§8 (from "### 4." to before "### 9.")

Checked against the reading pack (04–08) and `scripts/source-lookup.py` (שער הכוונות; פרי עץ חיים). No repository file was edited.

Totals: serious 0 · moderate 5 · minor 7.

## Findings

1. **§5, [5.15] "שאר האמנים שבקדיש מפסיקים בין חלקי שם מ"ב …" (moderate)**
   - **Problem:** The paragraph contradicts [5.14] and the source.
     - The third "separating" amen, after the כ"ח תיבות, falls at "דאמירן בעלמא ואמרו אמן". [5.14] counts that same amen as one of the two amens of the צ"א kavana, so it is not one of "שאר האמנים".
     - The source counts the separating amens against אמן יש"ר alone, not against both amens of [5.14].
     - For "שאר האמנים", the source gives a different kavana: the general amen kavana. [5.16] presents that kavana next.
   - **Evidence:**
     - SK Kaddish.1.5.3: "ולכן צריך לחזור ולענות אמן פ"ג וג' אמנים אלו הם זולת אמן יש"ר כו".
     - SK Kaddish.1.5.8: "כל שאר מלות אמן שיש בקדישין אין בהם כונה זו אלא באלו שני אמנים בלבד שהם באמן יהא שמיה רבא מברך כו' ובדאמירן בעלמא ואמרו אמן. אבל בשאר האמנים יש להם כונה אחרת וביארנו אותה בענין סדר כל האמנים והברכות".
   - **Fix:** Say "שלושה אמנים, מלבד אמן יהא שמיה רבא, מפסיקים …". Note that the third, "דאמירן בעלמא ואמרו אמן", also carries the צ"א kavana of the מוחין דאבא. Drop "שאר".

2. **§8, [8.24] "ארבע שלפני 'עזרת אבותינו' הן הארת ארבעת המוחין עצמם … והן ללאה. ארבע שאחריו … ארבעת השמות אהי"ה, והן לרחל" (moderate)**
   - **Problem:** This follows SK Shema 8.1.23. In [8.15], however, the biur follows 6.4.4: Leah receives only from the garments of the mochin, and Rachel from the mochin themselves. The two paragraphs now contradict each other without comment.
   - **Evidence:**
     - SK Shema 6.4.4: "אין לאה לוקחת הארה מן המוחין עצמן דז"א אלא מן הנה"י דאימא אשר הם הלבוש … אבל רחל לוקחת הארה מן המוחין עצמן".
     - SK Shema 8.1.23: "ארבע אמת הראשונים … ד' שמות יה"ו … ונמשכות אל לאה שהם המוחין עצמן וד' אמת האחרונים … ד' שמות אהיה פשוטין שהם לבושי המוחין ונמשכות אל רחל".
     - SK Shema 8.1.16 presents the Leah/Rachel split as a separate kavana ("עוד יש כונה אחרת … ד"פ אמת הראשונים הם כנגד ד' דאחד … והד' אמת האחרונים … ברחל"). 8.1.23 says all eight lights first go to Yaakov: "בתחילה כל ח' הארות אלו נמשכות כולם אל יעקב ואח"כ מחציין יוצאת לאה ומחציין … רחל".
   - **Fix:** Keep the 8.1.23 reading, and add that all eight lights go first to Yaakov and only then divide. In [8.15], limit the "garments only" point to what Leah receives at ד' דאחד (6.4.4), so that it does not clash with [8.24].

3. **§4, [4.1] "מפרשת העקידה ואילך מתחילה התפילה שבדיבור" (moderate)**
   - **Problem:** In the source, the stage of speech begins with the eighteen morning blessings (ברכות השחר), not with the עקידה. Morning Blessings.5 only gives a precondition for "arranging the prayer from the עקידה on". [4.2] then treats the ברכות השחר as coming before speech.
   - **Evidence:** SK Sermons on Morning Prayers.3.5: "ועתה נבאר בחי' הדיבור … והנה עד עתה ע"י המעשה נתקנו העולמות … כדי שאח"כ ע"י הדיבור של התפלה נוכל להעלות עולם בעולם … הנה ע"י הי"ח ברכ' דשחרי' מברכ' ענ"י עד פ' התמיד אנו מורידים שפע גדול … אל הג' ראשונות דעשיה".
   - **Fix:** For example: "מפרשת העקידה ואילך מסדרים את התפילה בבית הכנסת, וקודם לה קבלה אחת". Present the ברכות השחר as the first step of speech (3.5), not as something before it.

4. **§6, [6.16] "וב'ואתה מושל בכל' נותנים צדקה בעמידה" (moderate)**
   - **Problem:** The text gives "כי כל בשמים ובארץ" as the time for giving, and "ואתה מושל בכל" only as a second report. The biur prints the second report as the rule. The figure of the יסוד as גבאי צדקה, called "כל", belongs to both reports.
   - **Evidence:** SK Morning Prayers.23: "ומזה הטעם עצמו צריך ליתנ' בעת שאומר כי כל בשמים ובארץ שהוא רומז אל היסוד הנקרא כל ופעם אחרת שמעתי ממוז"ל שצריך שיתננה בעת שאומר ואתה מושל בכל".
   - **Fix:** "בשעה שאומרים 'כי כל בשמים ובארץ', ובשמועה אחרת ב'ואתה מושל בכל', נותנים …".

5. **§4, [4.14] "אמירת הקטורת סמוכה לתפילה מלפניה ומאחריה, ומטעם אחד" (moderate)**
   - **Problem:** The source gives two reasons, and [4.15] itself states both:
     - before the prayer: "שלא יתאחזו הקליפו' ויעלו בעלי' העולמות";
     - after it: "כדי שלא ינקו הקליפו' מן השפע היורד".
     
     "ומטעם אחד" holds only at the general level (keeping the קליפות from taking hold). The source also has the incense said before מנחה ("קודם שני תפלות").
   - **Evidence:** SK Sermons on Morning Prayers.3.11 (quoted in the block); PEC Gate of the World of Action.4.2.
   - **Fix:** "… ומטעם אחד בכללו, להרחיק את הקליפות, ובשני פנים: …". Optionally mention מנחה.

6. **§4, [4.5] "ובכל פעם ניתוסף ממילא תיקון גם בעולם שתחתיו: אחר 'ברוך שאמר' עולה גם חיצוניות שלוש הראשונות של העשיה …" (minor)**
   - **Problem:** The source gives this as R. Chaim Vital's own recollection, not as a statement of the text. The biur does mark such reports elsewhere, as "בשמועה אחרת" in [4.21].
   - **Evidence:** SK Sermons on Morning Prayers.3.6: "ונלע"ד חיים ששמעתי ממוז"ל כי עד ב"ש …".
   - **Fix:** Mark it as a report, e.g. "ובשמועה …".

7. **§7, [7.5] "והוא רמוז במילה 'מאז' … כמניין שמונה אותיותיו" (minor)**
   - **Problem:** The gematria 8 belongs to "אז", not to "מאז" (מאז = 48).
   - **Evidence:** SK Morning Prayers.29: "וכונת שם הנז' הוא במלת מאז כי אז הוא בגי' ח' אותיות של שם הנז'".
   - **Fix:** "… במילה 'מאז' …, ש'אז' שבה מניינו שמונה, כמניין אותיותיו".

8. **§6, [6.2] "מזה הטעם 'הודו' נאמר קודם 'ברוך שאמר' … : היצירה עצמה אינה מקבלת אור אלא מ'ברוך שאמר' ואילך" (minor)**
   - **Problem:** Two different reasons are fused into one. MP.6 gives a second reason ("גם לטעם הזה"): the נשמה must be given before the lower three of יצירה rise. The clause after the colon is MP.2's separate reason.
   - **Evidence:**
     - SK Morning Prayers.2: "יצירה עצמה עדיין אינה נתקנת ואינה מקבלת אור אליה עצמה רק מן ברוך שאמר ואילך".
     - SK Morning Prayers.6: "וגם לטעם הזה אומרים הודו קודם ב"ש".
   - **Fix:** "… גם מזה הטעם … ; וטעם נוסף: היצירה עצמה …".

9. **§8, [8.29] "אחר שהמוחין נסתלקו בלילה לגמרי" (minor)**
   - **Problem:** Slightly overstated. The inner קטנות mochin of אימא never leave.
   - **Evidence:** SK Shema 4.1.4: "לפי שהוא בא אחר הלילה שלא נשארו בו רק פנימים דקטנות דאימא בלבד".
   - **Fix:** "… אחר שבלילה נסתלקו המוחין חוץ מן הפנימיים של הקטנות מצד אימא".

10. **§8, [8.30] "ועלתה עמו עד היכל קודש הקודשים" (minor)**
    - **Problem:** At "תהלות לאל עליון" the ascent only begins. The entry is completed at "אדני שפתי תפתח", as [8.26] itself says.
    - **Evidence:** SK Shema 8.1.24: "אז הוא התחלת עליית יעקב עם לאה ורחל בהיכל ק"ק דבריאה … ואח"כ באדני שפתי תפתח אז הוא גמר כניסתם".
    - **Fix:** "והתחילה לעלות עמו אל היכל קודש הקודשים".

11. **§6, [6.16]: a quotation not letter-for-letter (minor)**
    - **Problem:** The biur quotes "כי בכל עולם ועולם יש כמה פרצופים". The source has "כי בכל עולם ועולם יש כמה פרצו'" (SK Morning Prayers.22).
    - **Fix:** Quote it as written, or drop the quotation marks.

12. **§8, [8.26]: a translation in quotation marks (minor)**
    - **Problem:** "זהו 'המלך העליון' היוצא לקבל את הכלה" puts quotation marks around a Hebrew rendering. The source has "מלכא עלאה" (SK Shema 8.1.25: "וז"ש בזוהר דכדין מלכא עלאה נפק לקבלא כו'"). Readers will take it as a quotation.
    - **Fix:** Use the source's words, "מלכא עלאה", or remove the quotation marks.

## Checked and found sound

**§4**
- [4.3] The pnimiut/chitzoniut ladder through all the worlds up to עתיק (SK 3.5).
- [4.4]–[4.5] The first "change": ג"ר of יצירה clothe only the מלכות of בריאה, and only the עשיה part of each world is repaired now. The higher worlds rise later at ב"ש, יוצר and עמידה. The מלכות clothes three because its measure is נה"י (3.6).
- [4.7] The second "change": elsewhere, ג"ר rise into the four lowest of the upper world. In עשיה they rise into נה"י of יצירה only, and מלכות of יצירה stays in ז"ת of עשיה, "כל בחינת המלכות הוא בחינת עשיה" (3.7).
- [4.9] א"ל אדנ"י = 96 = צ"ו; אבגית"ץ = 506 = תולע; עולת/תולע; the חסד rooted in גבורה (3.10–3.11). [4.10] Every עולה corresponds to לאה העליונה (3.11).
- [4.12]–[4.13] The 11 incense spices:
  - ten inner sparks plus one encompassing light (3.12);
  - the verse "קח לך סמים" and חלבנה = מלכות, לבונה זכה = the encompassing light;
  - in their root, the 7 kings plus 4 אחוריים of או"א and ישסו"ת (3.13);
  - PEC's "first teaching", "תחלה שמעתי", that they are the י"ס דעשיה plus one holy power (Gate of the World of Action.4.2).
- [4.17]–[4.18] אנא בכח:
  - חיצוניות ג"ר and פנימיות ג' אמצעיות of עשיה clothe מלכות of יצירה, and "העשיה חזרה להיות יצירה";
  - six levels raised by the six first names into the six letters of שקוצי"ת, one name per letter;
  - the ruling name of each day, אבגית"ץ on Sunday through שקוצי"ת on Shabbat (3.8–3.9).
- [4.20] The rest of עשיה rises through איזהו מקומן, with עשיה completed as ten from above and below. The quotation "והנה בעלית העולמות …" is exact (3.9).
- [4.21] The 13 levels, and the alternative report counting 13 in עשיה alone (3.9). [4.22] דרוש א' places ישתבח at the end of יצירה; this is correct (Sermons on Morning Prayers.1.2).

**§5**
- [5.2] The five kaddishim and what each joins, with קדיש יתמא excluded (Kaddish.1.1.3, 1.3.1, 1.4.1–1.4.2).
- [5.3]–[5.5] The heichalot structure, the column, and why there is no kaddish between גאולה and תפלה (1.1.3–1.1.6).
- [5.7] נפש, then רוח through the first kaddish (1.1.2).
- [5.8] The two kinds of 28 and 42:
  - first kaddish: letters from מ"ה (יצירה), raising 6 heichalot; words from ס"ג (בריאה), raising the 7th;
  - ב"ן has no 28;
  - second kaddish: ס"ג and ע"ב; after the Amida: ע"ב;
  - the 42 of the kaddish is not the אנא בכח name but ד'+י'+כ"ח of each הוי"ה (1.1.2, 1.1.6, 1.2.1, 1.3.1, 1.5.3).
- [5.10] Targum (1.5.1). [5.12]–[5.14] ו"ה = 11; יתגדל/ויתקדש against Ima and Abba; אל"ם becoming אלהים; אמן = 91 as the three fillings of י"ה; לעלם/ולעלמי/עלמיא (1.5.2, 1.5.4, 1.5.8).
- [5.16]–[5.17] PEC amen: יאהדונה"י in ת"ת, יסוד and the space below יסוד. The kaddish's amen is the חיבוק with Adni first; the others are the נישוק (Amen 1.2–1.4, 2.1–2.3).

**§6**
- [6.1]–[6.2] ג"ר דעשיה receive נפש, then רוח through the kaddish, then נשמה through הודו (MP.6). The Ari followed the Sephardi custom (MP.2).
- [6.4]–[6.7] (MP.3–8).
- [6.9] ברוך שאמר: 13 ברוך against the 13 תיקוני דיקנא; 87 words = 22 + 65; "ראשו כתם פז"; מ"ה with its 42 letters = 87; לבנה = 87 (MP.9–10).
- [6.11]–[6.14] (MP.11–17).
- [6.15] The five הללויה psalms:
  - הללי נפשי = מלכות;
  - כי טוב זמרה = יסוד, with נ"ה attached;
  - מן השמים = ת"ת, ending in גבורה;
  - שיר חדש = חסד, with גבורה included;
  - הללו אל בקדשו = ג"ר;
  - and the Rav's doubt whether these are the sefirot of יצירה or of its מלכות (MP.20–21).
- [6.16] The three coins: two together, for לאה and מלכות דבינה, then one for רחל (MP.23). Standing from ויברך דוד to "אתה הוא ה' האלהים" (MP.22).
- [6.17]–[6.20] (MP.26; Kaddish.1.2.1; Sermons on Morning Prayers.3.6).

**§7**
- [7.2]–[7.3] The order of the seven heichalot in the blessings matches MP.27 exactly:
  - לבנת הספיר = יסוד, to "אל ברוך גדול דעה";
  - עצם השמים = הוד, to "לאל ברוך נעימות";
  - נוגה = נצח, to "המחדש בטובו";
  - זכות = גבורה, to "אהבת עולם";
  - אהבה = חסד, to "אמת ויציב";
  - רצון = ת"ת, to the Amida;
  - ק"ק = ג"ר at "אדני שפתי".
  
  The מלכות of בריאה is outside the count.
- [7.4]–[7.6] (MP.28–29). [7.7]–[7.8] (PEC Shema 2.3; MP.29). [7.10]–[7.11] (MP.30–31).

**§8**
- [8.1]–[8.3] (Shema 6.1.2; PEC Shema 4.5). [8.4]–[8.5] Only the ו"ק mochin of אימא enter now; the upper פרקין remain as מקיף (6.1.2, 6.4.1, 8.1.25).
- [8.6]–[8.7] The two zivugim (6.1.6, 6.1.9).
- [8.8] The stages of the קטנות mochin: in ק"ש of יוצר the inner and encompassing mochin of אימא and the inner mochin of אבא are already present. "ישראל" brings in the encompassing mochin of אבא (Shema 4.1.5, 6.3.1).
- [8.9]–[8.13] (6.3.3–6.4.1). [8.14]–[8.17] לאה and רחל at "אחד" and in בשכמל"ו, including the כתר of לאה from the four alephs, עק"ב for רחל, and ציקי קדרה (6.3.4–6.5.7). [8.18] (Shema 5.1.7; PEC Shema 6.1).
- [8.20] Word counts of the paragraphs: 42 (head), 72 (חג"ת), 50 (two thirds of ת"ת), 72 (נה"י), and the three words repeated (8.1.3, 8.1.6). [8.21]–[8.22] (8.1.2, 8.1.13–8.1.14).
- [8.23]–[8.24] The eight "אמת": four יה"ו and four אהיה פשוטים, which are Yaakov's and not ז"א itself; the 15 vavs; the two "לעד" (8.1.16–8.1.23; see finding 2).
- [8.26]–[8.27] (8.1.24–8.1.28).
- [8.28]–[8.29] Ranking of the four Shema recitations:
  - על המטה: from the chitzoniut of או"א;
  - ערבית: from the chitzoniut of א"א;
  - קרבנות: from the pnimiut of א"א;
  - יוצר: from the chitzoniut of עתיק.
  
  Also: why two recitations in the morning, and why there is none at מנחה (Shema 3.1.4, 4.1.4, 1.1.4).

# Report C

## Check C: biur-arizal §9 to the end (§9–§13, סיכום)

File checked: discourses/005-kavanot-shacharit/biur-arizal/biur.md. It was rebuilt while I worked (08:43). In §10 the paragraph numbers moved down by one, so 10.1 is now the prose that follows the first passage. Paragraphs are named below by their number and their first words.

## Findings

1. **§13.2 "בזיווג של העמידה נבקע יסוד אימא … אחר הזיווג נבקע גם הוא, בשתי בקיעות: הראשונה יציאתו מגופו של זעיר אנפין, והיא פתיחת ההיכל; והשנייה בקיעת היסוד עצמו, שהוא ספר התורה"**
   - Problem: the biur gives as the teaching the account of the two bursts that both works mark as doubtful, or as the second reading. It leaves out the account each of them prefers. The quoted block stops at "ומאירין ביעקב …", just before the preferred account starts.
   - Evidence: SK Sermons on Torah Reading.1.4 introduces the first account with "ובענין שני בקיעות אלו נסתפקתי איך שמעתי ממוז"ל כי הנלע"ד ששמעתי ממנו". It then goes on: "אמנם היותר נלע"ד ששמעתי בבירור ממוז"ל הוא באופן זה כי הבקיעה הא' היא בקיעת היסוד דאימא … והבקיעה זאת היא ענין פתיחת ההיכל … כי ההיכל הוא יסוד דאימא אשר בתוכו הס"ת שהוא היסוד דאבא ואח"כ באה הבקיעה הב' והיא בקיעת היסוד דז"א עצמו … ובקיעה זו היא ענין פתיחת תיק הס"ת … וזהו היותר אמיתי אצלי מדרך הראשון". PEC Gate of Reading the Torah.1.5 says "פי' - ההיכל, יסוד אמא, ס"ת, יסוד". PEC 1.9 brings the biur's account only as "ונלע"ד באופן אחר … אך הפירוש הראשון הוא יותר פשוט אצלי בביאור שכך שמעתי".
   - Seriousness: **serious**.
   - Correction: give the preferred account. The first burst is יסוד אימא, the היכל, which lets the light of יסוד אבא out into the body of ז"א. The second is יסוד ז"א, the opening of the case of the ספר תורה, so the light goes out to יעקב, and the reading itself lets out the light inside. At most mention the other account as a second version. Either extend the quoted block or quote the preferred passage.

2. **§9.2 "בכך מתיישבים שני הלשונות שבדרוש א' של תפילת השחר (מבוא): בפסוק עצמו עדיין עומדים בבריאה, ו'ברוך' של ברכת אבות עדיין נקרא היכל קודש הקודשים שלה … אלא שעתה הוא נכלל באצילות ועולה עמה"**
   - Problem: the biur presents its own harmonization as something the passage settles. SK Standing Prayer.1.1.3 explains why "אדני שפתי תפתח" is not an interruption ("כתפלה אריכתא דמיא"). It places the verse, and through "ברוך", in the היכל קה"ק דבריאה. It does not address the statement in Morning Prayers.1.2 that בריאה lasts "עד סוף בא"י מגן אברהם", and the harmonization reaches only as far as "ברוך". The passage itself says only "ואמנם תכוין שעדיין בפ' זה אנו בעולם הבריאה", and that is about the verse.
   - Evidence: SK Standing Prayer.1.1.3 (above). SK Standing Prayer.2.2.5 says "המלכות … והיא עתה בהיכל קה"ק דבריאה וצריכה לעלות", which is at "ברוך". What actually covers the whole blessing is SK Standing Prayer.2.1.3–2.1.4: "שהנקב' עומדת עד עתה בעולם הבריאה בהיכל קה"ק ועתה עולה אל האצילות", and "ובעלות אותה נקו' בברכת אבות … מתחברת מדרגה אחר מדרגה".
   - Seriousness: moderate.
   - Correction: present it as the biur's own connection, not as what 1.1.3 decides. If the end of ברכת אבות is meant, base it on 2.1.3–2.1.4: Rachel's nine ספירות rise out of the היכל קה"ק of בריאה over the course of ברכת אבות.

3. **§10.2 (formerly 10.3) "הקדושה שבחזרה היא כסדר הקדושה שב'יוצר', 'רק שתכוין שהוא באצילות' (סעיף 7)"**
   - Problem: the quotation is exact; it comes from PEC Gate of the Recitation of the Shema.2.1. But the gates of the repetition, which this section is built on, make the קדושה of the repetition the act that raises יעקב and רחל to חג"ת and completes Rachel's דעת. The biur leaves this out. It also says in 10.1 that they rise in the repetition, without saying when or how. PEC says that rise does not happen at the start of the repetition. And SK Repetition.4.1.2 sets the קדושה of יוצר apart, as the one that raises המלכות to the הוד of בריאה.
   - Evidence: PEC Gate of the Repetition of the Silent Prayer.3.6 says "אע"פ שאמרנו כי בחזרת עמידה עולין עד חג"ת, אינה בתחלת עמידה. אך בברכת אבות, מאירים בהן מן החסד, כדי לעלות שם יעקב. ובברכת גבורות … כדי שתעלה שם רחל … ועולין עד חג"ת, והעלאה זו הוא ע"י הקדושה". 3.7 says "סוד הקדושה ותכליתה הוא, כדי להאיר לדעת של רחל". 3.8 says that חג"ת of ז"א must first rise to its ג"ר. SK Sermons on the Repetition of the Standing Prayer.2.1.2 says the three קדושות fix her three מוחין and her דעת.
   - Seriousness: moderate.
   - Correction: add that the rise to חג"ת is completed by the קדושה. In ברכת אבות and גבורות they receive light from the two arms, and then through the קדושה they rise, and Rachel's דעת is completed. Keep the PEC line as a further note.

4. **§11.5 "והיא מתחלקת לשלושה: חלק יורד אל רחל; חלק נמשך בחסד של זעיר אנפין, לחיבוק מעולה מן הראשון; וחלק עולה אל הדיקנא שלו"**
   - Problem: this matches SK Vaya'avor.1.3 and PEC Confession.1.4. But a passage of the עמידה gate that the biur does not quote divides the drop differently: one part to the hug, one to the union of ז"א with לאה, one down to רחל. The biur's paragraph puts the two purposes (לאה, דיקנא) next to the three parts (רחל, חיבוק, דיקנא) and does not mention the difference. A reader cannot tell where לאה's union stands in the division.
   - Evidence: SK Sermons on the Standing Prayer.6.1.26 says "ע"י תיקון י"ג מידות של רחמים דויעבור אנו מחלקין אותה לג' חלקים חלק א' לחיבוק א' והוא מעולה מאד וחלק הב' לצורך זווג ז"א עם לאה מן החזה ולמעלה … וחלק הג' יורד למטה עד פי היסוד דז"א ומשם יוצא וניתן בדעת דיעקב".
   - Seriousness: moderate.
   - Correction: say that the עמידה gate (6.1.26) gives a second division, in which לאה takes the place of the דיקנא. Or make clear that the three parts in Vaya'avor.1.3 are a separate matter from the two purposes.

5. **§12.3 "ו'אליך' דווקא: הנשמות מועלות עד ה', שהוא התפארת"**
   - Problem: the biur's source here is the קריאת שמע gate. The נפילת אפים gate itself, in both works, reads the verse the other way. There "אליך", and not "עליך", shows that those who give themselves over in נפילת אפים stay below, in מלכות, and the ה' of the verse is the נוקבא. The biur gives one reading as settled, while the gate it is explaining says the opposite.
   - Evidence: SK Shema 5.1.10, the biur's source, says "מלת אליך דייקא לרמוז שאנו מעלין נשמותינו עד ה' ממש שהוא הת"ת". Against it: SK Sermons on the Falling on the Face Prayer.5.2 says "וגבי מוסר עצמו למיתה כתיב אליך ה' נפשי אשא ולא כתיב עליך כי הם למטה במל'". PEC Gate of Putting Down the Head.4.2 says the same: "אליך ולא עליך, כי הם למטה במלכות". SK Falling on the Face.3.2 says "אליך ה' פי' בעבורך ה' שהיא הנוקבא דז"א הנק' שם ההויה דמלוי ההין".
   - Seriousness: moderate.
   - Correction: give the reading of the נפילת אפים gate, that the souls are raised to the נוקבא and into her יסוד, which is also what 12.2 itself says. Mention the קריאת שמע reading (ת"ת) as a second version, if at all.

6. **סיכום.2 "…ומ'יוצר אור' עד העמידה הנשמות שבבריאה, וקדיש בין כל עולם לעולם. בעמידה כל העולמות קשורים באצילות."**
   - Problem: this contradicts the biur's own §5. The source says there is no קדיש between בריאה and אצילות, because גאולה must be joined to תפילה.
   - Evidence: biur 5.2 says "בין הבריאה לאצילות, בין גאולה לתפילה, אין קדיש", and 5.5 says "מכאן גם שאין קדיש בין הבריאה לאצילות". The source behind them, quoted in §5, has "ואין לך סמיכות גדול מזה".
   - Seriousness: moderate.
   - Correction: "וקדיש בין העשיה ליצירה ובין היצירה לבריאה; בין הבריאה לאצילות אין קדיש".

7. **סיכום.4 "על המבנה הזה בונה הרש"ש את דרכו, סעיף כנגד סעיף."**
   - Problem: no section of the biur and none of its sources say this. It is a statement from outside, about a later work that is not in the library, and it is printed as fact.
   - Evidence: there is no Rashash text among the sources of this biur. Nothing in §1–§13 supports it.
   - Seriousness: moderate. It also goes against the rule that what prints is explanation from the sources.
   - Correction: remove it, or move it to notes/.

8. **§9.8 "החזרה פנים בפנים נעשית ב'מלך עוזר ומושיע ומגן'"**
   - Problem: this leaves out a step, and the passage it relies on places things differently. In 2.6.1, Rachel grows back-to-back to the full height of ז"א and turns face-to-face at "באהבה". She then shrinks to a small point at the עטרה of the יסוד, and only in "מלך עוזר ומושיע ומגן" is she rebuilt face-to-face, from כתר down (מלך = כתר, עוזר = ג"ר, and so on). 2.6.4 does refer back to "שחוזרים פב"פ בתיבו' מלך עוזר ומושיע ומגן", but it says this concerns יעקב ורחל only.
   - Evidence: SK Standing Prayer.2.6.1 says "ואז תכוין ג"כ להביאה עי"ז פב"פ עם ז"א … וכל אלו הכוונות תכוין במלת אהבה. והנה אחר חזרת' פב"פ עמו מתמעטת ונופלת לרגלי ז"א בסוד נקודה קטנה … ואז תכוין לחזור ולבנות' כבתחילה בבחי' פב"פ וזה יהיה במלות: מלך עוזר ומושיע ומגן". SK Standing Prayer.2.6.3 says "ענין חזרה זו איננה עם ז"א עצמו אלא עם יעקב".
   - Seriousness: minor.
   - Correction: "ב'באהבה' היא חוזרת פנים בפנים ומתמעטת לנקודה, וב'מלך עוזר ומושיע ומגן' היא נבנית מחדש פנים בפנים, עם יעקב".

9. **§10.1 (formerly 10.2) "בחזרה הם עולים כנגד חסד, גבורה ותפארת, ובפרי עץ חיים: יעקב בחסד ורחל בגבורה"**
   - Problem: the biur credits the detail to PEC alone. It is in the very SK passage quoted above it, in the part after the cut. This is not a misreading, only the wrong attribution.
   - Evidence: SK Repetition.1.1.3 says "ועתה בחזרת ש"ץ העמידה כונתינו עתה היא להעלות' יותר למעלה ולהעמיד ליעקב בחסד דז"א ורחל בגבור' דז"א". PEC Gate of the Repetition of the Silent Prayer.1.2 says the same.
   - Seriousness: minor.
   - Correction: "וכן בהמשך הדרוש ובפרי עץ חיים".

10. **§10.1 "זה הכלל שנתבאר ב'אמת ויציב' (סעיף 8), שמה שגדול למטה קטן בעלותו"**
    - Problem: the reason the passage gives is different: "בכל עליית מדריגה יותר עליונ' צריכ' אל הארות אחרות יתירו'", that is, more light is needed. The link to the rule in §8 is the writer's own. The passage also gives a second reason, that יסוד אימא stands upright and not crouching, so חג"ת are left revealed. The biur does not mention it.
    - Evidence: SK Repetition.1.1.3 (the quoted part), and further on: "נשאר' זקופה ועי"כ נמצאו כל חג"ת דז"א באורות מגולים". PEC Repetition.1.3 says the same.
    - Seriousness: minor.
    - Correction: soften it to "וקרוב לזה הכלל…", or replace it with the text's own reason, האם רובצת / זקופה.

11. **§12.2 "'אשה מזרעת תחילה'"**
    - Problem: a quotation inside the prose that is not letter-for-letter.
    - Evidence: SK Falling on the Face.2.3 has "אשה מזרעת תחלה".
    - Seriousness: minor.
    - Correction: "תחלה".

12. **§13.6 "כי אורו גדול מהם והם אינם יכולים להיאחז בו"**
    - Problem: a small paraphrase drift. The source says the light blinds them; it does not compare it with them.
    - Evidence: PEC Reading the Torah.6.1 says "כי אורו גדול ומסמא את עיניהן, ואינן יכולין להתאחז בו".
    - Seriousness: minor.
    - Correction: "כי אורו גדול ומסמא את עיניהן".

13. **§11.3 "החלק שלוקח הצד האחר בשעת הווידוי נפרד מן הקדושה"**
    - Problem: the source says that the שעיר, the other side itself, departs from the holy by means of the portion it takes during the confession. The biur says the portion is what separates.
    - Evidence: PEC Confession.8.33 says "והוא נפרש מן הקדושה, ע"י אותו החלק שלוקח בעת הוידוי, ואחר שהלך לו".
    - Seriousness: minor.
    - Correction: "הצד האחר נפרד מן הקדושה על ידי החלק שהוא לוקח בשעת הווידוי".

14. **§13.6 "ואחריהם את הטלית, שכשם שהונח קודם התפילה כך נשאר עד שהוסרו (סעיף 3)"**
    - Problem: the order is correct, but the reason "כשם ש…" is not in any source. The source also says how they are removed: the head tefillin standing, the hand tefillin sitting.
    - Evidence: SK Sermons on Aleinu and the Prayer Formula.1.24 says "עלינו לשבח … ואח"כ יסיר תש"ר מעומד … ואח"כ ישב ויסיר תש"י מיושב … ואח"כ יסיר הטלית". PEC Reading the Torah.6.3 matches.
    - Seriousness: minor.
    - Correction: drop the reason, or cite 1.24.

15. **§9.12 "ושלוש הברכות הראשונות של האמצעיות, 'אתה חונן', 'השיבנו' ו'סלח לנו', נעשות לנוקבא חכמה, בינה ודעת"**
    - Problem: this is faithful to 6.1.3. But it says nothing of the clash with the passages that follow in the same gate, where "סלח לנו" is the חסד of the נוקבא (6.1.6). It also leaves out the second account in 6.1.3, where only אתה חונן and השיבנו are her חו"ב, and the next seven blessings are the seven kisses.
    - Evidence: SK Standing Prayer.6.1.6 says "סלח לנו אבינו כו' הוא בחסד שבה". 6.1.3 says "ונמצא כי ברכת אתה חונן וברכת השיבנו הם ב' מוחין חו"ב שלה וז' ברכות שלאחריהן הם בחי' השבעה נשיקין".
    - Seriousness: minor.
    - Correction: either "ולפי הדרוש השני, שתי הראשונות חכמה ובינה שלה, והשבע שאחריהן שבע הנשיקין", or leave 9.12 and qualify "והן הנשיקין" in 9.13 to match.

## Claims checked and found sound

- §9.1–9.2: the verse is the היכל קה"ק דבריאה. Its ג"ר are included in מלכות דאצילות, called תפלה, and rise with it ("ונעשו הכל בחי' אצילות"). The reading of the verse (אדני = מלכות, שפתי = נ"ה, תפתח = ת"ת, פי = מלכות drawing from אצילות into בריאה) follows 1.1.3. The harmonization itself is finding 2.
- §9.3–9.4: the כתר of רחל stays in אצילות, and the nine below it rise from the היכל קה"ק (2.1.3).
- §9.5–9.6: the order of bowing and straightening is exact (2.2.1): ברוך = body, ו' toward ה'; אתה = head, י' toward ה'; at the Name the body straightens first (ה' תתאה toward ו') and then the head (ה' עילאה toward י'). The second זיווג of או"א brings in the ג"ר of Imma's מוחין and then the nine מוחין of Abba. "נשלם פרצוף ז"א … ורחל אחור באחור" is borne by 2.6.1 ("כבר נשלם פרצוף ז"א ויעקב ורחל … עדיין רחל עומדת אחור באחור").
- §9.8: the נסירה needs no תרדמה by day because of the רשימו (2.6.1). The נצחים and הודים of א"א, או"א and ז"א; אספקלריא דנהרא / דלא נהרא; הוי"ה and אדנ"י "פרודות", joined in the middle line (2.6.4). The link back to §3, Rachel in the left line where the point of her כתר was bound, matches 3.17 and its source.
- §9.9–9.10: נה"י of Imma leave by themselves; Rachel stays from the חזה down, the place of her אצילות, where יסוד אימא ends; the bow at "מגן אברהם" brings נה"י back into ז"א (2.6.5).
- §9.11–9.12: the first and last three blessings are the original ו"ק, which became חב"ד and חג"ת; twelve additions (three new נה"י of ז"א, nine ספירות of the נוקבא) against twelve middle blessings; the כתר of ז"א through ברכת המינים; the other hearing of thirteen levels (6.1.2–6.1.3).
- §9.13: the hugs follow the עמידה: אבות on the right with ע"ב, אתה גבור "שמאלו תחת לראשי", אתה קדוש on the body; Imma fixes her with בוכ"ו; the middle blessings fix her from ז"א himself and are called kisses (6.1.3). The block from 6.1.21 bears "after the hug and the kisses".
- §9.14: שים שלום is the יסוד; the drop comes from the five חסדים in the דעת, through יסוד אימא, to the יסוד of ז"א; שורק = קשר; the second hearing, the full Name, five גבורות sweetened in five חסדים, יב"ק (6.1.21).
- §9.15: at שים שלום the drop only begins; the union of יעקב and רחל is completed in נפילת אפים (SK Falling 2.2; PEC Putting Down the Head 2.1; PEC Confession 8.33). "למען יחלצון" gives שם יל"י, which raises the sparks of the seven kings, and "יהיו לרצון" has yods in nine of its ten words, against the nine yods of עסמ"ב; the quotation "אשר כל סודות תפלת י"ח תלויים בהם" is exact (6.1.27). The quotation "להחזיר זעיר ונוקבא פנים בפנים למטה במקומם" is exact (PEC Prayer 6.12).
- §10.1: the silent prayer from the חזה down, the כתר against ת"ת; the rise to חג"ת; Rachel again back-to-back, then a point face-to-face, then a full partzuf; silent because of the hold of the outer forces below, aloud in חג"ת (SK Repetition 1.1.3).
- §10.3: the two צלמים; the ages 13 (איש), 18 (לחופה), 20 (מוכר קרקעות), and Abba's outer lights "בחתימת זקן"; in ברכת אבות all enter except Abba's outer lights, which enter in ברכת כהנים before the union (SK Repetition 5.1.3; PEC Repetition 6.1, 6.4, 6.13).
- §11.1–11.2: the stations of the drop are correct: at ש"ש from the brain to the חזה, unrevealed; in the confession to the heart, revealed; ויעבור, the union of ישראל and לאה from the חזה up; נפילת אפים down to the יסוד, to יעקב and רחל (SK Falling 2.2; PEC Putting Down the Head 2.1). The order in PEC Confession 8.33 (confession, the 13 מידות, נפילת אפים, "שלא יהיו חטאיו מעכבין את החסדים") is correct.
- §11.3: the plural, ערבות, "ונשא השעיר", "ולא יתערב זר בתוכינו" are exact; apart from finding 13, all in PEC Confession 8.33. On sadness, SK Morning Blessings.4: "בעת שמתודה הוידוי ומפרט חטאיו אז טוב להתעצב בלבד, אבל בשאר התפילה נמשך לו נזק נפלא גדול". Sound.
- §11.4–11.5: the two purposes are exact (Vaya'avor 1.3). The drop comes from the outer light on the head of ז"א on the side of חכמה, and at its root from the חסד of עתיק in the כתר of א"א. The three ע"ב are: ע"ב of yods; ס"ג with 10 letters; מ"ה with כ"ו (Vaya'avor 1.3; PEC Confession 1.3–1.4). "כדיקנא של אריך" is borne by SK Repetition 5.1.3 ("גם הוא כמו א"א").
- §12.1–12.2: the drop of מ"ד to רחל and the מ"ן first; מ"ן from the seven kings in the קליפות of each world; the worshipper in אצילות, included in רחל; the fall to the bottom of עשיה, "כאדם המפיל עצמו מראש הגג"; gathering from עשיה, יצירה and בריאה and handing them over in her יסוד (SK Falling 2.3; 2.4 likewise). The link to "אל נקמות" is borne by Morning Prayers.4, quoted in §6.
- §12.3: קריאת שמע means four court deaths for the upper union; here "נשיאות נפש בסוד מיתה טבעית בלבד" is exact (SK Shema 6.3.9; 5.1.10). Apart from finding 5, sound.
- §13.1–13.2: Mondays and Thursdays, יצירה = ז"א = the Written Torah (SK Torah Reading 1.3; PEC 1.6, 2.5); in the עמידה יסוד אימא was opened and יסוד אבא stayed closed, only its glow going out to יעקב (1.4). "תורה צוה לנו משה … משה הוא יסוד אבא" is exact.
- §13.3–13.4: the שפע goes down to בריאה, then יצירה, then עשיה, while the worlds stay above until after עלינו (SK Ashrei 1.2; PEC Reading the Torah 3.3). This matches the opening (Morning Prayers 1.3) and §5.
- §13.5–13.6: עלינו brings down the outer light itself, which cancels the outer forces; they lie between the inner and the outer light (חשמ"ל); the second reason, that the great light comes last; after each of the three prayers (PEC Reading the Torah 6.1). Removing the tefillin only after עלינו and the tallit after them is borne by SK Aleinu and the Prayer Formula 1.24, apart from the reason in finding 14.
- סיכום.1: the purpose, ז"א and נוקבא face-to-face in their place below; sorting out the sparks; the new souls made in each union (6.1.21); the רשימו until night (2.6.1).
- סיכום.3: the order of the building agrees with the sections and their sources (tefillin; קריאת שמע; אמת ויציב; תהלות לאל עליון; אבות; middle blessings; ש"ש; the repetition; ברכת כהנים; confession, ויעבור, נפילת אפים; the descent; עלינו). On the turning in אבות, see finding 8.
- סיכום.4: "the worlds themselves do not rise" (Morning Prayers 1.3); the guards against the קליפות; Rachel rebuilt at each level. Apart from the closing sentence, finding 7, sound.
