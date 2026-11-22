#!/usr/bin/env python3
"""Print what a day of fundraising in the street and in shuls needs:
cards to hand out (QR to the site), a sign for learning in public, a sign-up
sheet for the clipboard, and a pocket script with the route.

    python fundraising/build.py        ->  output/fundraising/*.pdf

GIVE_URL: a Bit / PayBox / payment link. When set, the cards and the sign carry
a second QR code for giving. Never put a private phone number here.
"""
import pathlib
import segno
from weasyprint import HTML

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "fundraising"
FONTS = (ROOT / "templates" / "fonts").as_uri()

SITE_HE = "https://esoterics611.github.io/he/"
SITE_EN = "https://esoterics611.github.io/"
GIVE_URL = None

TIERS_HE = 'ח"י ₪ · ל"ו ₪ · ק"פ ₪ · הקדשת הדפסה 1,800 ₪'
TIERS_EN = "₪18 · ₪36 · ₪180 · Dedicate a printing ₪1,800"


def qr(url):
    return segno.make(url, error="m").svg_data_uri(scale=10, border=0, dark="#1f1a14")


BASE_CSS = f"""
@font-face {{ font-family: "Frank Ruhl Libre"; src: url({FONTS}/FrankRuhlLibre-Regular.ttf); }}
@font-face {{ font-family: "Frank Ruhl Libre"; font-weight: bold; src: url({FONTS}/FrankRuhlLibre-Bold.ttf); }}
@font-face {{ font-family: "EB Garamond"; src: url({FONTS}/EBGaramond-Regular.ttf); }}
@font-face {{ font-family: "EB Garamond"; font-weight: bold; src: url({FONTS}/EBGaramond-SemiBold.ttf); }}
@font-face {{ font-family: "EB Garamond"; font-style: italic; src: url({FONTS}/EBGaramond-Italic.ttf); }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: "Frank Ruhl Libre", "EB Garamond"; color: #1f1a14; }}
.he {{ direction: rtl; font-family: "Frank Ruhl Libre"; }}
.en {{ direction: ltr; font-family: "EB Garamond"; }}
.accent {{ color: #7a4b1e; }}
"""


def write(name, html):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    HTML(string=html, base_url=str(ROOT)).write_pdf(path)
    print("wrote", path.relative_to(ROOT))


# ---------------------------------------------------------------- cards (A6, 4 per A4)

def card_he():
    give = (f'<div class="q"><img src="{qr(GIVE_URL)}"><div>לתרומה</div></div>' if GIVE_URL else "")
    return f"""<div class="card he">
  <div class="brand">ספר פורג'</div>
  <div class="title">פְּדֵה בְשָׁלוֹם נַפְשִׁי</div>
  <div class="sub">מאמר אדמו"ר האמצעי · שערי תשובה, שער התפלה</div>
  <div class="verse">הפסוק שאמר אדמו"ר הזקן ביציאתו לחירות בי"ט כסלו</div>
  <p>אנחנו מבארים את קבלת האר"י ז"ל ואת החסידות מתוך מקורותיהן, כל ציטוט מדויק,
  ומוציאים אותן לקונטרסים מודפסים, ללומדים, לשיעורים ולבתי הכנסת.</p>
  <p class="ask">המאמרים מוכנים. חסרה ההדפסה.</p>
  <div class="tiers">{TIERS_HE}</div>
  <div class="ded">אפשר להקדיש את ההדפסה לזכות או לעילוי נשמת.</div>
  <div class="qrs"><div class="q"><img src="{qr(SITE_HE)}"><div>סרקו לראות את הדפים</div></div>{give}</div>
  <div class="url en">esoterics611.github.io/he</div>
</div>"""


def card_en():
    give = (f'<div class="q"><img src="{qr(GIVE_URL)}"><div>Give</div></div>' if GIVE_URL else "")
    return f"""<div class="card en">
  <div class="brand">Sefer Forge</div>
  <div class="title">Padah B'Shalom</div>
  <div class="sub"><i>“He redeemed my soul in peace”</i> · a maamar of the Mitteler Rebbe,
  Shaarei Teshuvah, the Gate of Prayer</div>
  <div class="verse">The verse the Alter Rebbe was saying when he was freed on 19 Kislev</div>
  <p>We explain the Kabbalah of the Arizal and Chassidus from their own sources, every
  quotation exact, and print them as booklets for learners, classes and shuls,
  in Hebrew and in translation.</p>
  <p class="ask">The maamarim are ready. What is missing is the printing.</p>
  <div class="tiers">{TIERS_EN}</div>
  <div class="ded">A printing can be dedicated in honor of someone, or in memory of a loved one.</div>
  <div class="qrs"><div class="q"><img src="{qr(SITE_EN)}"><div>Scan to see the pages</div></div>{give}</div>
  <div class="url">esoterics611.github.io</div>
</div>"""


CARD_CSS = BASE_CSS + """
@page { size: A4; margin: 0; }
.sheet { width: 210mm; height: 297mm; display: flex; flex-wrap: wrap; page-break-after: always; }
.sheet:last-child { page-break-after: auto; }
.card { width: 105mm; height: 148.5mm; padding: 13mm 9mm 7mm; outline: 0.2mm dashed #c9c0b4;
        outline-offset: -0.1mm; display: flex; flex-direction: column; text-align: center; }
.brand { font-size: 8pt; letter-spacing: .08em; color: #7a4b1e; }
.title { font-size: 24pt; font-weight: bold; margin-top: 3mm; line-height: 1.15; }
.card.en .title { font-size: 22pt; }
.sub { font-size: 9.4pt; margin-top: 1.5mm; line-height: 1.3; }
.verse { font-size: 9.4pt; color: #7a4b1e; margin-top: 2.5mm; line-height: 1.3; }
.card p { font-size: 10pt; line-height: 1.4; margin-top: 4mm; text-align: justify; }
.card.he p { text-align: justify; }
.card p.ask { font-weight: bold; text-align: center; font-size: 11pt; margin-top: 3.5mm; }
.tiers { font-size: 10.6pt; font-weight: bold; color: #7a4b1e; margin-top: 2mm; }
.ded { font-size: 8.8pt; margin-top: 1.2mm; }
.qrs { display: flex; justify-content: center; gap: 8mm; margin-top: 7mm; }
.q { font-size: 7.6pt; text-align: center; }
.q img { width: 27mm; height: 27mm; display: block; margin: 0 auto 1mm; }
.url { font-size: 7.4pt; color: #6b6259; margin-top: 1mm; font-family: "EB Garamond"; }
"""


def cards():
    he, en = card_he(), card_en()
    # page 2 is the back: flipped on the long edge, so the left and right columns swap.
    # Every card is the same, so the backs line up either way.
    html = f"""<html><head><meta charset="utf-8"><style>{CARD_CSS}</style></head><body>
<div class="sheet">{he * 4}</div><div class="sheet">{en * 4}</div></body></html>"""
    write("cards.pdf", html)


# ---------------------------------------------------------------- sign (A3)

def sign():
    give = (f'<div class="q"><img src="{qr(GIVE_URL)}"><div>לתרומה · Give</div></div>' if GIVE_URL else "")
    html = f"""<html><head><meta charset="utf-8"><style>{BASE_CSS}
@page {{ size: A3; margin: 24mm 22mm; }}
html, body {{ height: 100%; }}
body {{ text-align: center; display: flex; flex-direction: column; justify-content: space-between; }}
.now {{ font-size: 46pt; color: #7a4b1e; letter-spacing: .03em; }}
.m {{ font-size: 30pt; margin-top: 10mm; }}
.big {{ font-size: 130pt; font-weight: bold; line-height: 1.05; margin-top: 2mm; }}
.by {{ font-size: 34pt; margin-top: 4mm; }}
.verse {{ font-size: 23pt; margin-top: 12mm; color: #3d342b; }}
.come {{ font-size: 52pt; font-weight: bold; margin-top: 16mm; }}
hr {{ border: 0; border-top: 0.6mm solid #7a4b1e; width: 55%; margin: 16mm auto 10mm; }}
.en {{ font-size: 28pt; line-height: 1.35; }}
.qrs {{ display: flex; justify-content: center; gap: 22mm; margin-top: 14mm; }}
.q {{ font-size: 17pt; }}
.q img {{ width: 75mm; height: 75mm; display: block; margin: 0 auto 3mm; }}
</style></head><body>
<div class="he">
  <div class="now">לומדים עכשיו</div>
  <div class="m">מאמר</div>
  <div class="big">פְּדֵה בְשָׁלוֹם</div>
  <div class="by">של אדמו"ר האמצעי</div>
  <div class="verse">הפסוק שאמר אדמו"ר הזקן ביציאתו לחירות בי"ט כסלו</div>
  <div class="come">בואו ללמוד חמש דקות</div>
</div>
<hr>
<div class="en">Learning now: <b>Padah B'Shalom</b>, a maamar of the Mitteler Rebbe.<br>
<i>Come learn for five minutes.</i></div>
<div class="qrs"><div class="q"><img src="{qr(SITE_HE)}">
<div class="he">עוזרים להדפיס את המאמרים</div><div class="en" style="font-size:15pt">Help print the maamarim</div></div>{give}</div>
</body></html>"""
    write("sign-A3.pdf", html)


# ---------------------------------------------------------------- sign-up sheet (A4 landscape)

def signup():
    rows = "".join("<tr><td></td><td></td><td></td><td></td><td></td><td class='c'><span class='box'></span></td></tr>" for _ in range(13))
    html = f"""<html><head><meta charset="utf-8"><style>{BASE_CSS}
@page {{ size: A4 landscape; margin: 12mm 12mm 10mm; }}
h1 {{ font-size: 19pt; text-align: center; }}
.en.h {{ font-size: 13pt; text-align: center; font-style: italic; margin-top: 1mm; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 6mm; direction: rtl; }}
th {{ font-size: 11pt; font-weight: bold; padding: 1.5mm 2mm; border-bottom: 0.5mm solid #7a4b1e; text-align: right; }}
th span {{ display: block; font-family: "EB Garamond"; font-weight: normal; font-size: 9pt; color: #6b6259; direction: ltr; text-align: right; }}
td {{ height: 10.4mm; border-bottom: 0.25mm solid #b9afa3; }}
td.c {{ text-align: center; }}
.box {{ display: inline-block; width: 4mm; height: 4mm; border: 0.3mm solid #6b6259; }}
.foot {{ font-size: 9pt; color: #6b6259; text-align: center; margin-top: 4mm; }}
</style></head><body>
<div class="he"><h1>לקבל את המאמרים, ולהיות שותפים בהדפסה</h1></div>
<div class="en h">Receive the maamarim, and be a partner in printing them</div>
<table>
<tr>
<th style="width:21%">שם<span>Name</span></th>
<th style="width:17%">טלפון / וואטסאפ<span>Phone / WhatsApp</span></th>
<th style="width:22%">אימייל<span>Email</span></th>
<th style="width:9%">סכום<span>Amount</span></th>
<th style="width:21%">הקדשה: לזכות / לע"נ<span>Dedication</span></th>
<th style="width:10%">לשלוח לי את המאמר<span>Send me the maamar</span></th>
</tr>{rows}</table>
<div class="foot"><span class="he">הפרטים נשמרים אצל ספר פורג' בלבד ולא יועברו לאחרים.</span>
&nbsp;·&nbsp; <span class="en">Kept by Sefer Forge only, never passed on.</span></div>
</body></html>"""
    write("signup-sheet.pdf", html)


# ---------------------------------------------------------------- pocket script (A5, 2 pages)

def script():
    html = f"""<html><head><meta charset="utf-8"><style>{BASE_CSS}
@page {{ size: A5; margin: 10mm 10mm 9mm; }}
body {{ font-size: 9.2pt; line-height: 1.38; }}
h1 {{ font-size: 14pt; color: #7a4b1e; border-bottom: 0.4mm solid #7a4b1e; padding-bottom: 1mm; }}
h2 {{ font-size: 10.4pt; margin-top: 3mm; }}
h2 small {{ font-weight: normal; color: #6b6259; font-size: 8.4pt; }}
.say {{ background: #f5efe6; padding: 1.6mm 2.4mm; margin-top: 1mm; border-right: 0.8mm solid #7a4b1e; }}
.say.en {{ border-right: 0; border-left: 0.8mm solid #7a4b1e; font-size: 9.4pt; }}
ul {{ padding-right: 4.5mm; margin-top: 1mm; }}
li {{ margin-top: .6mm; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 1.5mm; font-size: 8.6pt; }}
td {{ padding: 1mm 1.2mm; border-bottom: 0.2mm solid #cfc6ba; vertical-align: top; }}
td:first-child {{ white-space: nowrap; font-weight: bold; width: 21mm; direction: ltr; text-align: right; }}
.page {{ page-break-after: always; }}
.cols {{ display: flex; gap: 5mm; }} .cols > div {{ flex: 1; }}
</style></head><body>

<div class="he page">
<h1>מה לומר</h1>

<h2>לגבאי, לפני התפילה</h2>
<div class="say">"שלום, אני רוני. אני מבאר מאמרי חסידות מתוך המקורות ומדפיס אותם.
אפשר לומר שתי דקות אחרי התפילה, או לעמוד ליד הדלת עם המאמר?"</div>

<h2>ברחוב <small>· 15 שניות</small></h2>
<div class="say">"זה מאמר של אדמו"ר האמצעי על הפסוק 'פדה בשלום נפשי', הפסוק שאדמו"ר הזקן
אמר כשיצא לחירות בי"ט כסלו. אנחנו מבארים אותו מילה במילה מתוך המקורות, ומדפיסים אותו
לכל מי שרוצה ללמוד. רוצה להיות שותף? ל"ו שקל, ק"פ, או להקדיש הדפסה שלמה."</div>
<div class="say en">"This is a maamar of the Mitteler Rebbe on 'Padah B'Shalom', the verse the Alter
Rebbe was saying when he was freed on 19 Kislev. We explain it word by word from the sources and
print it for anyone who wants to learn. Will you be a partner? 36 shekels, 180, or dedicate a whole printing."</div>

<h2>אחרי התפילה <small>· דקה אחת</small></h2>
<ul>
<li><b>מי אני:</b> שמי, ושאני מבאר את האר"י והחסידות מתוך המקורות, כל ציטוט מדויק.</li>
<li><b>המאמר:</b> מרים את הקונטרס. "פדה בשלום", ביאור יסוד ענין התפילה שנקרא שעת קרבא.</li>
<li><b>מה כבר נעשה:</b> קונטרס לבושי הנשמה, ביאור תפילת השחר על פי האר"י,
211 סיפורי שבחי הבעש"ט בעברית, אנגלית וצרפתית.</li>
<li><b>הבקשה, במספר:</b> "המאמרים מוכנים, חסרה ההדפסה. ק"פ שקל מדפיסים ערימה לבית כנסת;
1,800 מקדישים הדפסה שלמה לזכות או לעילוי נשמת."</li>
<li><b>איפה אני:</b> "אני עומד ליד הדלת עם המאמר. סרקו את הכרטיס או כתבו שם." ולשתוק.</li>
</ul>

<h2>מי שמתעניין</h2>
<div class="say">"רוצה להקדיש את ההדפסה? 1,800 שקל, והקונטרס יוצא לזכות מי שתבחר."</div>

<h2>סוף כל מפגש, גם בלי כסף</h2>
<div class="say">"תכתוב טלפון, ואשלח לך את המאמר כשהוא יוצא מהדפוס." ונותנים כרטיס.</div>
</div>

<div class="he">
<h1>שאלות, כללים, היום</h1>
<div class="cols"><div>
<h2>כשישאלו</h2>
<ul>
<li><b>"יש קבלה למס?"</b> "אין עדיין עמותה. זו תרומה אישית, בלי קבלה." לא להבטיח.</li>
<li><b>"מי אתם?"</b> "אני. הכול פתוח באתר: הדפים, ואיך זה נעשה." מראים את הקוד בכרטיס.</li>
<li><b>"אין לי מזומן"</b> ביט / פייבוקס. או לרשום פרטים ולשלוח קישור בערב.</li>
<li><b>"אין לי זמן"</b> כרטיס ביד, "יום טוב", הלאה.</li>
</ul>
</div><div>
<h2>כללים</h2>
<ul>
<li>קודם הגבאי, תמיד.</li>
<li>לומדים באמת, בקול. העניין קודם, הבקשה אחריו.</li>
<li>תמיד לנקוב מספר.</li>
<li>כל מי שעוצר מקבל כרטיס; כל שם נרשם.</li>
<li>לא להתווכח. לא ללחוץ.</li>
<li>סטטוס בוואטסאפ כל 2–3 שעות: תמונה + "עד עכשיו X ₪".</li>
<li>בערב: הודעת תודה לכל מי שנרשם.</li>
</ul>
</div></div>

<h2>היום</h2>
<table>
<tr><td>מוצאי שבת</td><td>התוועדות י"ט כסלו. לבקש מהמשפיע להזכיר, או לגשת אחד אחד.</td></tr>
<tr><td>7:00–9:30</td><td>שחרית בבית חב"ד, ומניין שני. דקה אחרי התפילה, באישור הגבאי.</td></tr>
<tr><td>10:00–13:00</td><td>העיר העתיקה: רחבת הכותל, הרובע, בית הכנסת צמח צדק. תיירים: באנגלית.</td></tr>
<tr><td>13:30–16:00</td><td>בן יהודה / מחנה יהודה: לומדים בקול ליד השלט.</td></tr>
<tr><td>16:00–17:30</td><td>רחביה / נחלאות: בתי כנסת של דוברי אנגלית ושל מתעניינים בקבלה.</td></tr>
<tr><td>מנחה–ערבית</td><td>מניין עם כולל או שיעור אחריו.</td></tr>
<tr><td>ערב</td><td>התוועדות י"ט כסלו: החדר הטוב ביותר של היום.</td></tr>
</table>

<div class="cols"><div>
<h2>לקחת</h2>
<ul>
<li>הקונטרס "פדה בשלום"</li>
<li>200 כרטיסים</li>
<li>השלט, ומשהו להעמיד או להדביק אותו</li>
<li>לוח כתיבה, 3 דפי הרשמה, 2 עטים</li>
<li>טלפון טעון וסוללה נוספת</li>
<li>ביט / פייבוקס מוכנים</li>
<li>נרתיק, עודף, מים</li>
</ul>
</div><div>
<h2>לפני היום</h2>
<ul>
<li>הצעת מחיר מדפוס ל-100 ול-500 עותקים</li>
<li>קישור ביט / פייבוקס</li>
<li>לדבר עם 2–3 גבאים</li>
<li>הודעה ל-30 מכרים: "ביום __ אני יוצא לגייס להדפסת פדה בשלום. היעד X ₪. תהיה הראשון?"</li>
<li>מכתב ברכה מרב או משפיע, אם אפשר</li>
</ul>
</div></div>
</div>
</body></html>"""
    write("pocket-script.pdf", html)


if __name__ == "__main__":
    cards(); sign(); signup(); script()
