# Translation rules: the Shivchei HaBesht booklets

Applies when Claude translates `shivchei-habesht-simple.md` (the stories in
modern Hebrew, printed as the themed booklets) into another language:
`shivchei-habesht-simple-en.md` (English), `shivchei-habesht-simple-fr.md`
(French). The booklets in those languages are built from these files by
`python scripts/build-booklets.py --lang en|fr`.

The translation carries the Hebrew booklet text into the other language and
nothing else. It is the same text, in the same order, at the same level: a
high-school student reads it unaided.

## Source

- Translate from `shivchei-habesht-simple.md`, sentence by sentence.
- Where the simple Hebrew is ambiguous, read the same place in
  `shivchei-habesht.md` (the original) and translate the meaning the simple
  text chose. Never take wording from `shivchei-habesht-english.md` (an older,
  literal translation of the original).
- The French is translated from the Hebrew too. The English may be read
  beside it to keep names and terms the same, never as its source.

## Faithful

- Every sentence of the Hebrew is in the translation, and nothing else: no
  added event, motive, feeling, description, explanation or lesson; nothing
  dropped, merged away or summarised.
- Who speaks, what is said, believed and done stays as the Hebrew has it.
  What the Hebrew leaves open (an unclear "he", an unstated reason) stays open.
- Parenthesised glosses and side notes stay in parentheses at the same point.
  A gloss the Hebrew gives for a Hebrew or Yiddish word is kept when that word
  is kept (`בעלפער, עוזר המלמד` → `a *belfer*, the teacher's helper`); when
  the target language has a plain word for it, the word is translated and a
  gloss that only explained the Hebrew word is dropped.
- Quoted verses and sayings are translated in plain language, inside quotation
  marks, with the Hebrew's "וכו'" as "etc." / « etc. ».
- The register stays plain and modern. Biblical or archaic phrasing only
  inside a quoted verse.

## Same shape

`python scripts/check-translation.py <file>` checks all of this:

- The header line, the intro paragraph, then the 211 `## ` sections in the
  Hebrew order: `## The Author's Introduction` / `## Introduction de l'auteur`,
  then `## <n> — <title>` with the story number in Arabic numerals.
- Each story has the same number of paragraphs as the Hebrew, and the same
  `>` blockquote paragraphs at the same places. A Hebrew paragraph is never
  split or joined.
- The last paragraph is the summary: `**Summary:**` / `**Résumé :**`.
- `<!-- MATURE: ... -->` flags are copied verbatim, in the same paragraph.
  `<!-- UNCLEAR: ... -->` flags stay in the Hebrew only: the translation
  follows the reading the Hebrew chose.
- No Hebrew letters in the text. Hebrew words that stay are transliterated.
- The book's closing line follows the last summary:
  `Finished and complete. Praise to God, Creator of the world.` /
  `Fin. Louange à Dieu, Créateur du monde.`

## Typography

- English: American spelling; straight quotes `"` `'` in the source (the
  build makes them curly); `—` for a dash; titles in title case.
- French: guillemets `« … »` with a space inside, a space before `: ; ! ?`
  (the build turns these spaces into narrow no-break spaces); `—` for a dash
  inside a sentence; titles in sentence case; `Rabbi` written out.
- Transliterated terms in italics the first time they occur in a story only
  when the reader could take them for an English/French word; names never.

## Names

One form per person or place, everywhere. "The Baal Shem Tov" / « le Baal
Chem Tov » always (never "the Besht").

| Hebrew | English | French |
|---|---|---|
| הבעל שם טוב | the Baal Shem Tov | le Baal Chem Tov |
| רבי ישראל בעל שם טוב | Rabbi Israel Baal Shem Tov | Rabbi Israël Baal Chem Tov |
| רבי אליעזר (אביו) | Rabbi Eliezer | Rabbi Eliézer |
| רבי גרשון מקיטוב / מקוטוב | Rabbi Gershon of Kitov | Rabbi Guershon de Kitov |
| המגיד ממזריטש, רבי דוב בער | the Maggid of Mezritch, Rabbi Dov Ber | le Maguid de Mezritch, Rabbi Dov Ber |
| רבי אברהם בן המגיד | Rabbi Avraham, the Maggid's son | Rabbi Avraham, le fils du Maguid |
| הרב מפולנאה, רבי יעקב יוסף | the Rabbi of Polonne, Rabbi Yaakov Yosef | le rav de Polonné, Rabbi Yaakov Yossef |
| המוכיח מפולנאה, רבי אריה לייב | the Mokhiach of Polonne, Rabbi Aryeh Leib | le Mokhia'h de Polonné, Rabbi Arié Leib |
| רבי נחמן מהורודנקה | Rabbi Nachman of Horodenka | Rabbi Na'hman de Horodenka |
| רבי נחמן מקוסוב | Rabbi Nachman of Kosov | Rabbi Na'hman de Kossov |
| רבי יצחק מדרוהוביץ' | Rabbi Yitzchak of Drohobych | Rabbi Its'hak de Drohobytch |
| רבי פנחס מקוריץ | Rabbi Pinchas of Koretz | Rabbi Pin'has de Koretz |
| רבי מיכל מזלוטשוב | Rabbi Michel of Zlotchov | Rabbi Mikhel de Zlotchov |
| רבי אליעזר מאמשטרדם | Rabbi Eliezer of Amsterdam | Rabbi Eliézer d'Amsterdam |
| רבי שמעון בר יוחאי | Rabbi Shimon bar Yochai | Rabbi Chimon bar Yo'haï |
| האר"י | the Arizal | l'Arizal |
| משה רבנו, אליהו הנביא | Moses our teacher, Elijah the Prophet | Moïse notre maître, le prophète Élie |
| אברהם, יצחק ויעקב | Abraham, Isaac and Jacob | Abraham, Isaac et Jacob |
| שבתי צבי | Shabbetai Tzvi | Chabbetaï Tsvi |
| מז'יבוז' | Mezhibuzh | Mejibij |
| פולנאה | Polonne | Polonné |
| מזריטש | Mezritch | Mezritch |
| ברודי, נמירוב, לבוב | Brody, Nemirov, Lvov | Brody, Nemirov, Lvov |
| אוסטרהא | Ostroh | Ostroh |
| שרגורוד | Shargorod | Chargorod |
| זסלב | Zaslav | Zaslav |
| ואלאכיה | Wallachia | la Valachie |
| ברסלאו | Breslau | Breslau |
| ארץ ישראל | the Land of Israel | la terre d'Israël |
| איסטנבול | Istanbul | Istanbul |

Other people and places: the common English (French) spelling where one
exists, otherwise a plain transliteration of the Hebrew. Add each one to this
table the first time it is used.

## Terms

| Hebrew | English | French |
|---|---|---|
| ה' | God; "the Lord" in a quoted verse | Dieu ; « l'Éternel » dans un verset |
| מן השמים | from Heaven | du Ciel |
| חז"ל | our Sages | nos Sages |
| רבנו (אדמו"ר הרב) | our master (the Rebbe, the Rav) | notre maître (le Rabbi, le Rav) |
| אדון | the nobleman | le seigneur |
| שר | the minister / the official / the nobleman, by context | le ministre / le dignitaire / le seigneur |
| המשנה למלך | the viceroy | le vice-roi |
| מוכסן | tollkeeper | fermier des péages |
| חוכר, חכירה (ארענדע) | leaseholder, lease (*arenda*) | fermier, bail (*arenda*) |
| קומיסר | commissar | commissaire |
| זהוב | zloty (pl. zlotys) | zloty(s) |
| יין שרף | vodka | eau-de-vie |
| מלמד, חדר | teacher, cheder | maître d'école, 'héder |
| בית המדרש, קלויז | the study house, the kloyz | la maison d'étude, le kloyz |
| בית הכנסת | the synagogue | la synagogue |
| מקווה | mikveh | mikvé |
| שוחט | shochet | cho'het |
| חזן, ש"ץ, לפני התיבה | cantor, prayer leader, before the ark | 'hazan, officiant, devant l'arche |
| שמונה עשרה, חזרת הש"ץ | the Amidah, the cantor's repetition | la Amida, la répétition de l'officiant |
| שחרית, מנחה, מעריב | the morning / afternoon / evening prayer | la prière du matin / de l'après-midi / du soir |
| תפילין, טלית, ציצית, מזוזה | tefillin, tallit, tzitzit, mezuzah | téfilines, talith, tsitsit, mezouza |
| צדיק | tzaddik | tsaddik |
| חסיד | Hasid; "pious" before a name | 'hassid ; « le pieux » devant un nom |
| גיהנום, גן עדן | Gehinnom, the Garden of Eden | la Géhenne, le jardin d'Éden |
| שד, מזיק | demon, harmful spirit | démon, esprit malfaisant |
| מכשף, מכשפה | sorcerer, witch | sorcier, sorcière |
| שמות קדושים, קמע | holy names, amulet | noms saints, amulette |
| כוונות, יחודים | mystical intentions, unifications | intentions mystiques, unifications |
| עליית נשמה | ascent of the soul | ascension de l'âme |
| ניצוצות, תיקון, קליפה | sparks, *tikkun*, *kelipah* | étincelles, *tikoun*, *kelipa* |
| שכינה | the Shechinah | la Chekhina |
| קפיצת הדרך | the road shortened (*kefitzat haderech*) | le chemin raccourci (*kefitsat haderekh*) |
| פרסה | parsah | parsa |
| שאלת חלום | dream question | question de rêve |
| מקטרג, קטרוג | accuser, accusation (in Heaven) | accusateur, accusation (au Ciel) |
| כרוז | proclamation (in Heaven) | proclamation (au Ciel) |
| עלילה, עלילת דם | false accusation, blood libel | fausse accusation, accusation de meurtre rituel |
| ברית, סנדק | circumcision (bris), sandek | circoncision, sandak |
| פדיון הבן | the redemption of the firstborn | le rachat du premier-né |
| תנאים, נדוניה | engagement contract, dowry | contrat de fiançailles, dot |
| משכון | pledge | gage |
| עגונה | agunah | agouna |
| ועד ארבע ארצות | the Council of Four Lands | le Conseil des Quatre Pays |
| ספר התולדות | the *Toldot* | les *Toldot* |
| הספר הזוהר | the Zohar | le Zohar |

The booklet glossaries (`booklets/glossary-en.yaml`, `glossary-fr.yaml`)
explain the kept terms; a term that stays untranslated in the text has an
entry there.
