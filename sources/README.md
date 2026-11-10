# sources/ — the books our texts cite

Reference works kept in the repo, so that every citation in a session's text can
be looked up and quoted from a known copy: in the reading pack built before a
lesson is recorded (`prompts/references-pack.md`), and in anything printed later.

| Work | File | From |
|---|---|---|
| עץ חיים | `arizal/etz-chaim.he.json` | Sefaria, "Sefer Etz Chaim" (hebrew.grimoar.cz), Public Domain |
| פרי עץ חיים | `arizal/pri-etz-chaim.he.json` | Sefaria, "Pri Etz Chaim" (hebrew.grimoar.cz), Public Domain |
| שער הגלגולים | `arizal/shaar-hagilgulim.he.json` | Sefaria, "Sha'ar HaGilgulim" (hebrew.grimoar.cz), Public Domain |

`sources.yaml` is the catalog: each work's file, how our texts abbreviate it
(`cite_as`), where it was downloaded and when, and its `numbering:` notes.

**Never edit a file here.** Each is a Sefaria export exactly as downloaded; a
correction goes in a plan's `note:`, not in the source. Errors found in a file
(e.g. Etz Chaim 49.2.1 reads "השמ"ל" for "החשמ"ל") are noted where they are quoted.

## Looking things up

    python scripts/source-lookup.py 'ע"ח שמ"ט פ"ה'           # a citation as our texts write it
    python scripts/source-lookup.py etz-chaim 39.11            # a Sefaria address
    python scripts/source-lookup.py --find 'גלות השכינה'       # a phrase, anywhere
    python scripts/source-lookup.py --gates etz-chaim          # the gates and their names

Addresses are Sefaria's: `gate.chapter.paragraph` (`49.5.1`), or the gate's name
for Pri Etz Chaim (`Gate of Prayer.7.3`). A paragraph is often a whole chapter.
`--find` ignores niqqud, quote marks and punctuation.

**Numbering.** The editions our texts cite (the Alter Rebbe's, the Shklov print)
number some gates, chapters and derushim differently from these files. The
quoted words decide where a citation points. `sources.yaml` lists every
difference found so far under each work's `numbering:`; add new ones there.

## Adding a work

Sefaria's export is public at `https://storage.googleapis.com/sefaria-export/`;
list a category with `?prefix=json/<Category>/&delimiter=/`. For a Hebrew text:

    curl -sS -o sources/<group>/<id>.he.json \
      "https://storage.googleapis.com/sefaria-export/json/<Category>/<Sub>/<Title>/Hebrew/merged.json"

Then add it to `sources.yaml` (title, file, `cite_as`, `gates`, `from`, `version`
with its license from the version file next to `merged.json`, `fetched`), and
check a known citation with `source-lookup.py`. Available from the same export:
שער הכוונות, שער הפסוקים, שער מאמרי רשב"י, שער המצוות and more under
`json/Kabbalah/Arizal and Chaim Vital/`; the Zohar under `json/Kabbalah/Zohar/`.
שער הגלגולים (here since 2026-11-09) is not the ספר הגלגולים our texts cite by
chapter: it is the other redaction of the same teachings, arranged in הקדמות
(address = הקדמה.paragraph), and the words the Alter Rebbe quotes from
"גלגולים פ"א" are not in it. Its teaching is, and a narration that explains
those citations quotes it from here: the souls' rise from the kelipot by
others' prayers, יחודים and mitzvot (13.1, 39.7), their עיבור in the מלכות
before they come down into a body (12.5, 12.7, 39.6). `sources.yaml` lists the
correspondences found.
