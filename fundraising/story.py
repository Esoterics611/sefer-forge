#!/usr/bin/env python3
"""The colour handout that tells the whole story: what we do, real pages, the
three steps, what is ready, booking a shiur, being a partner in the printing.
A4, two sides, Hebrew and English.

    python fundraising/story.py   ->  output/fundraising/story-he.pdf, story-en.pdf

The page pictures come from the prints themselves; build them first if missing:
    python scripts/build-handout.py discourses/006-padah-beshalom/handouts/padah-beshalom-text.md
    python scripts/build-pamphlet.py discourses/002-shaar-hayichud/sessions/011
"""
import subprocess
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from build import BASE_CSS, OUT, ROOT, SITE_EN, SITE_HE, GIVE_URL, qr, write  # noqa: E402

IMG = OUT / "img"
PAGES = {  # name: (pdf, page)
    "pb": (ROOT / "output/handouts/padah-beshalom-text.pdf", 1),
    "sh-cover": (ROOT / "output/pamphlets/002-shaar-hayichud-011.pdf", 1),
    "sh-page": (ROOT / "output/pamphlets/002-shaar-hayichud-011.pdf", 3),
}

DEEP, GOLD, CREAM, INK = "#5a2418", "#b8862f", "#f7f0e4", "#1f1a14"


def pictures():
    IMG.mkdir(parents=True, exist_ok=True)
    for name, (pdf, page) in PAGES.items():
        if not pdf.exists():
            sys.exit(f"missing {pdf.relative_to(ROOT)}: build it first (see the top of this file)")
        subprocess.run(["pdftoppm", "-r", "110", "-png", "-singlefile", "-f", str(page), "-l", str(page),
                        str(pdf), str(IMG / name)], check=True)
    return {n: (IMG / f"{n}.png").as_uri() for n in PAGES}


T = {
"he": dict(
    dir="rtl", font='"Frank Ruhl Libre"', site=SITE_HE, url="esoterics611.github.io/he",
    kicker="ספר פורג'",
    head='תורת אדמו"ר האמצעי<br>מבוארת, מודפסת ונלמדת בחבורה',
    sub="פָּדָה בְשָׁלוֹם · שַׁעַר הַיִּחוּד, פרק אחר פרק",
    lede='אדמו"ר האמצעי, בנו וממלא מקומו של אדמו"ר הזקן, כתב מאמרים רחבים ועמוקים, '
         'שלימודם קשה למי שלא הורגל בהם. אנחנו מבארים אותם מילה במילה מתוך המקורות, '
         'כל ציטוט מדויק, ומביאים אותם אל הלומדים: מודפסים, ובשיעור, בבית הכנסת, בחבורה ובאונליין.',
    caps=["פדה בשלום: הנוסח לפרקיו, ובראשו המאמר בקצרה ומהלכו",
          "שער היחוד, פרק ב': קונטרס לשיעור",
          "בכל עמוד: הנוסח, והביאור תחתיו"],
    steps=[("מבארים", "כל מילה מתוך המקורות. כל ציטוט מדויק, אות באות, כדי שהלומד יוכל לבדוק."),
           ("מדפיסים", "קונטרס לכל מאמר ולכל פרק: הנוסח, והביאור שלו תחתיו."),
           ("לומדים", "שיעור בבית הכנסת, בחבורה או באונליין. הקונטרס הוא חומר הלימוד, ונשאר ביד.")],
    ready_h="מה מוכן עכשיו",
    ready=[('פָּדָה בְשָׁלוֹם', 'מאמר אדמו"ר האמצעי על הפסוק שאמר אדמו"ר הזקן ביציאתו לחירות בי"ט כסלו: '
            'ביאור יסוד ענין התפילה שנקרא "שעת קרבא". שנים עשר פרקים.'),
           ('שַׁעַר הַיִּחוּד', 'לאדמו"ר האמצעי, עם ליקוטי ביאורים לר\' הלל מפאריטש. ההקדמה ופרקים א\'–ג\', '
            'כל פרק קונטרס לשיעור, וממשיכים.'),
           ('ועוד', 'לבושי הנשמה בלשון אדמו"ר הזקן, עם חוברת המקורות; ביאור תפילת השחר על פי האר"י; '
            'סיפורי שבחי הבעש"ט בעברית, באנגלית ובצרפתית.')],
    book_h="להזמין שיעור",
    book=["בבית הכנסת: שיעור על מאמר, בין מנחה לערבית או בשבת.",
          "בחבורת לימוד: סדרה, פרק אחר פרק בשער היחוד.",
          "באונליין: שיעור בזום לקבוצה, בכל מקום.",
          "אני מגיע עם הקונטרסים, וכל משתתף מקבל עותק."],
    give_h="להיות שותפים בהדפסה",
    give=[('ח"י ₪ · ל"ו ₪', "עותקים ללומדים"),
          ('ק"פ ₪', "קונטרסים לבית כנסת או לחבורה"),
          ("1,800 ₪", "הקדשת הדפסה של מאמר או פרק, לזכות או לעילוי נשמת")],
    foot_h="השאירו פרטים, ואחזור אליכם",
    foot="לשיעור, לחבורה או להקדשה. סרקו לראות את הדפים עצמם.",
    scan="לראות את הדפים", givescan="לתרומה",
    vsrc='תהלים נה, יט · הפסוק שאדמו"ר הזקן אמר ביציאתו לחירות',
),
"en": dict(
    dir="ltr", font='"EB Garamond"', site=SITE_EN, url="esoterics611.github.io",
    kicker="Sefer Forge",
    head="The teachings of the Mitteler Rebbe<br>explained, printed, and learned together",
    sub="Padah B'Shalom · Shaar HaYichud, chapter by chapter",
    lede="The Mitteler Rebbe, son and successor of the Alter Rebbe, wrote broad and deep maamarim "
         "that are hard going for anyone not used to them. We explain them word by word from their "
         "sources, every quotation exact, and bring them to people who learn: in print, and in a "
         "shiur, in shul, in a study group, and online.",
    caps=["Padah B'Shalom: the text by chapter, opening with a summary and its course",
          "Shaar HaYichud, chapter 2: a booklet for the class",
          "On every page: the text, and the explanation below it"],
    steps=[("We explain", "Every word from the sources. Every quotation exact, letter for letter, so the reader can check."),
           ("We print", "A booklet for each maamar and each chapter: the text, with its explanation below."),
           ("We learn", "A shiur in shul, in a study group, or online. The booklet is the class material, and it stays with you.")],
    ready_h="Ready now",
    ready=[("Padah B'Shalom", "The Mitteler Rebbe's maamar on the verse the Alter Rebbe was saying when he "
            "was freed on 19 Kislev: the foundation of prayer as “the hour of battle”. Twelve chapters."),
           ("Shaar HaYichud", "By the Mitteler Rebbe, with the explanations of Reb Hillel of Paritch. The "
            "introduction and chapters 1–3, each a booklet for a class, and more to come."),
           ("And more", "The garments of the soul in the Alter Rebbe's own words, with its source pack; the "
            "morning prayer after the Arizal; the stories of the Baal Shem Tov in Hebrew, English and French.")],
    book_h="Book a shiur",
    book=["In shul: a maamar, between Mincha and Maariv or on Shabbos.",
          "In a study group: a series, chapter by chapter through Shaar HaYichud.",
          "Online: a class on Zoom for a group, anywhere.",
          "I come with the booklets, and every participant gets a copy."],
    give_h="Be a partner in the printing",
    give=[("₪18 · ₪36", "copies for learners"),
          ("₪180", "booklets for a shul or a study group"),
          ("₪1,800", "dedicate the printing of a maamar or a chapter, in honor of someone or in memory of a loved one")],
    foot_h="Leave your details and I will be in touch",
    foot="For a shiur, a study group, or a dedication. Scan to see the pages themselves.",
    scan="See the pages", givescan="Give",
    vsrc="“He redeemed my soul in peace from the battle against me” (Psalms 55:19), the verse the Alter Rebbe was saying when he was freed",
),
}


def css(t):
    side = "right" if t["dir"] == "rtl" else "left"
    return BASE_CSS + f"""
@page {{ size: A4; margin: 0; }}
body {{ direction: {t['dir']}; font-family: {t['font']}; color: {INK}; }}
.page {{ width: 210mm; height: 297mm; position: relative; page-break-after: always; overflow: hidden; }}
.page:last-child {{ page-break-after: auto; }}
.band {{ background: {DEEP}; color: #fff; padding: 13mm 15mm 9mm; }}
.kicker {{ color: {GOLD}; font-size: 10pt; letter-spacing: .12em; }}
h1 {{ font-size: 25pt; line-height: 1.22; margin-top: 2mm; font-weight: bold; }}
.sub {{ color: #f0d9a8; font-size: 13pt; margin-top: 2.5mm; }}
.lede {{ font-size: 12.6pt; line-height: 1.55; padding: 9mm 15mm 0; text-align: justify; }}
.pics {{ display: flex; justify-content: center; gap: 7mm; padding: 9mm 12mm 0; direction: ltr; }}
.pic {{ width: 57mm; text-align: center; direction: {t['dir']}; }}
.pic img {{ width: 57mm; display: block; border: 0.2mm solid #cbbfae;
            box-shadow: 1.2mm 1.4mm 2.5mm rgba(60,30,10,.28); background: #fff; }}
.pic div {{ font-size: 9.4pt; line-height: 1.3; margin-top: 2.5mm; color: #4a3f35; }}
.steps {{ display: flex; gap: 5mm; padding: 10mm 15mm 0; }}
.step {{ flex: 1; background: {CREAM}; border-top: 1.2mm solid {GOLD}; padding: 4mm 4mm 4.5mm; }}
.num {{ display: inline-block; width: 8mm; height: 8mm; line-height: 8mm; border-radius: 50%;
        background: {DEEP}; color: #fff; text-align: center; font-weight: bold; font-size: 11pt; }}
.step h3 {{ display: inline; font-size: 15.5pt; margin-{side}: 2mm; color: {DEEP}; }}
.step p {{ font-size: 11pt; line-height: 1.45; margin-top: 2.5mm; }}
.verse {{ position: absolute; bottom: 12mm; left: 15mm; right: 15mm; text-align: center; color: {DEEP}; }}
.verse .v {{ font-family: "Frank Ruhl Libre"; direction: rtl; font-size: 19pt; font-weight: bold; }}
.verse .s {{ font-size: 10pt; color: #6b6259; margin-top: 1.5mm; }}
.verse:before {{ content: ""; display: block; width: 40mm; margin: 0 auto 5mm; border-top: 0.5mm solid {GOLD}; }}
h2 {{ font-size: 19pt; color: {DEEP}; }}
.ready {{ padding: 15mm 15mm 0; }}
.item {{ display: flex; gap: 5mm; margin-top: 5.5mm; padding-bottom: 5mm; border-bottom: 0.25mm solid #e1d6c6; }}
.item b {{ flex: 0 0 36mm; font-size: 15pt; color: {DEEP}; }}
.item span {{ font-size: 11.8pt; line-height: 1.5; }}
.two {{ display: flex; gap: 6mm; padding: 12mm 15mm 0; }}
.panel {{ flex: 1; padding: 7mm 7mm 8mm; }}
.panel.a {{ background: {CREAM}; border-{side}: 1.4mm solid {GOLD}; }}
.panel.b {{ background: {DEEP}; color: #fff; }}
.panel.b h2 {{ color: #f0d9a8; }}
.panel ul {{ list-style: none; margin-top: 3mm; }}
.panel li {{ font-size: 11.8pt; line-height: 1.5; margin-top: 3.5mm; padding-{side}: 4mm; position: relative; }}
.panel li:before {{ content: "◆"; color: {GOLD}; font-size: 7pt; position: absolute; {side}: 0; top: .5mm; }}
.panel li.last {{ font-weight: bold; }}
.tier {{ margin-top: 5mm; }}
.tier b {{ font-size: 18pt; color: #f0d9a8; display: block; }}
.tier span {{ font-size: 11.4pt; line-height: 1.4; }}
.foot {{ position: absolute; bottom: 0; left: 0; right: 0; background: {CREAM};
         border-top: 1.2mm solid {GOLD}; padding: 7mm 15mm; display: flex; align-items: center; gap: 8mm; }}
.foot .t {{ flex: 1; }}
.foot h3 {{ font-size: 16pt; color: {DEEP}; }}
.foot p {{ font-size: 10.6pt; margin-top: 1.5mm; line-height: 1.4; }}
.foot .url {{ font-family: "EB Garamond"; font-size: 10pt; color: #6b6259; margin-top: 1.5mm; direction: ltr; text-align: {side}; }}
.q {{ text-align: center; font-size: 8.6pt; }}
.q img {{ width: 30mm; height: 30mm; display: block; margin-bottom: 1.5mm; }}
"""


def page_html(t, pics):
    steps = "".join(f'<div class="step"><span class="num">{i}</span><h3>{h}</h3><p>{p}</p></div>'
                    for i, (h, p) in enumerate(t["steps"], 1))
    order = ["pb", "sh-cover", "sh-page"]
    if t["dir"] == "rtl":  # read right to left: the first picture on the right
        order, caps = order[::-1], t["caps"][::-1]
    else:
        caps = t["caps"]
    pics_html = "".join(f'<div class="pic"><img src="{pics[n]}"><div>{c}</div></div>' for n, c in zip(order, caps))
    ready = "".join(f'<div class="item"><b>{h}</b><span>{p}</span></div>' for h, p in t["ready"])
    book = "".join(f'<li class="{"last" if i == len(t["book"]) - 1 else ""}">{x}</li>' for i, x in enumerate(t["book"]))
    give = "".join(f'<div class="tier"><b>{a}</b><span>{b}</span></div>' for a, b in t["give"])
    giveqr = (f'<div class="q"><img src="{qr(GIVE_URL)}">{t["givescan"]}</div>' if GIVE_URL else "")
    return f"""<html><head><meta charset="utf-8"><style>{css(t)}</style></head><body>
<div class="page">
  <div class="band"><div class="kicker">{t['kicker']}</div><h1>{t['head']}</h1><div class="sub">{t['sub']}</div></div>
  <p class="lede">{t['lede']}</p>
  <div class="pics">{pics_html}</div>
  <div class="steps">{steps}</div>
  <div class="verse"><div class="v">פדה בשלום נפשי מקרב לי כי ברבים היו עמדי</div><div class="s">{t['vsrc']}</div></div>
</div>
<div class="page">
  <div class="ready"><h2>{t['ready_h']}</h2>{ready}</div>
  <div class="two">
    <div class="panel a"><h2>{t['book_h']}</h2><ul>{book}</ul></div>
    <div class="panel b"><h2>{t['give_h']}</h2>{give}</div>
  </div>
  <div class="foot">
    <div class="t"><h3>{t['foot_h']}</h3><p>{t['foot']}</p><div class="url">{t['url']}</div></div>
    <div class="q"><img src="{qr(t['site'])}">{t['scan']}</div>{giveqr}
  </div>
</div>
</body></html>"""


if __name__ == "__main__":
    pics = pictures()
    for lang in ("he", "en"):
        write(f"story-{lang}.pdf", page_html(T[lang], pics))
