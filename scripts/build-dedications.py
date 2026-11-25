#!/usr/bin/env python3
"""The dedications store: site/he/dedicate.html and site/dedicate.html from
dedications/dedications.yaml.

    python scripts/build-dedications.py

Every part of the work a supporter can dedicate, discourse by discourse, with
its price (or "by arrangement") and a button: the item's Stripe Payment Link
once the owner has made one, until then an email to the project's address.
A dedication already taken shows instead of the button. Publish with
scripts/deploy-site.sh. The money never passes through Chayolei, which takes none.
"""
from __future__ import annotations

import html
import sys
from pathlib import Path
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "dedications" / "dedications.yaml"

T = {
    "he": {
        "dir": "rtl", "locale": "he_IL",
        "title": "להקדיש חלק · ספר פורג'",
        "desc": "כל חלק מעבודת ספר פורג' אפשר להקדיש לכבוד אדם יקר, לזכותו או לעילוי נשמת: חוברת, פרק, תרגום, סדרת שיעורים, כרך או שנה.",
        "h1": "להקדיש חלק מן העבודה",
        "lead": "כל חלק אפשר להקדיש לכבוד אדם יקר, לזכותו או לעילוי נשמת. ההקדשה מודפסת בחלק שהקדשתם, ומופיעה כאן.",
        "steps": ["בוחרים חלק.", "כותבים את נוסח ההקדשה: לכבוד, לזכות או לעילוי נשמת.", "ההקדשה מודפסת עם החלק, ומופיעה בדף הזה."],
        "kinds": {"edition": "מהדורה", "part": "חלק", "translation": "תרגום", "series": "שיעורים", "volume": "כרך", "year": "שנה"},
        "arrange": "המחיר בתיאום",
        "dedicate": "להקדיש",
        "write": "כתבו לנו",
        "repeat": "אפשר להקדיש כמה",
        "taken": "הוקדש",
        "subject": "הקדשה: {d} · {i}",
        "pay_stripe": "התשלום מאובטח ונעשה דרך Stripe. בטופס התשלום כותבים את נוסח ההקדשה.",
        "pay_mail": "התשלום באתר ייפתח בקרוב. עד אז כתבו לנו: נשלח את הדפים המתאימים, את נוסח ההקדשה כפי שיודפס, ואת דרך התשלום.",
        "other_h": "חלק אחר, או משהו גדול יותר",
        "other_p": "מלמדים, מוסדות, חוקרים והוצאות לאור, ומי שרוצה להקדיש חלק שאינו ברשימה: ספרו לנו מה מדבר אליכם.",
        "nav": [("./", "לתרום"), ("library.html", "הספרים"), ("how.html", "איך זה נעשה")],
        "lang": ("../dedicate.html", "en", "English"),
        "give": "לתמוך",
        "foot": [("library.html", "הספרים"), ("how.html", "איך זה נעשה"), ("../privacy.html", "מדיניות פרטיות"), ("../terms.html", "תנאי שימוש")],
        "contact": "יצירת קשר",
        "logo_alt": "הסמל של ספר פורג'",
        "name": "ספר פורג'",
        "root": "../",
    },
    "en": {
        "dir": "ltr", "locale": "en_US",
        "title": "Dedicate a part · Sefer Forge",
        "desc": "Any part of Sefer Forge's work can be dedicated in honour of someone dear, for their merit or in memory: a booklet, a chapter, a translation, a lesson series, a volume or a year.",
        "h1": "Dedicate a part of the work",
        "lead": "Any part can be dedicated in honour of someone dear, for their merit, or in memory. The dedication prints in the part you dedicated, and shows here.",
        "steps": ["Choose a part.", "Write the dedication: in honour of, for the merit of, or in memory of.", "The dedication prints with the part, and shows on this page."],
        "kinds": {"edition": "Edition", "part": "Part", "translation": "Translation", "series": "Lessons", "volume": "Volume", "year": "Year"},
        "arrange": "Price by arrangement",
        "dedicate": "Dedicate",
        "write": "Write to us",
        "repeat": "Several can dedicate",
        "taken": "Dedicated",
        "subject": "Dedication: {d} · {i}",
        "pay_stripe": "Payment is secure, through Stripe. The payment form asks for the dedication's wording.",
        "pay_mail": "Paying on the site opens soon. Until then, write to us: we'll send the pages that fit, the dedication as it will print, and how to pay.",
        "other_h": "Another part, or something larger",
        "other_p": "Teachers, institutions, scholars and publishers, and anyone who wants to dedicate a part not listed here: tell us what speaks to you.",
        "nav": [("./", "Give"), ("library.html", "The texts"), ("how.html", "How it is made")],
        "lang": ("he/dedicate.html", "he", "עברית"),
        "give": "Support",
        "foot": [("library.html", "The texts"), ("how.html", "How it is made"), ("privacy.html", "Privacy policy"), ("terms.html", "Terms")],
        "contact": "Contact",
        "logo_alt": "The Sefer Forge mark",
        "name": "Sefer Forge",
        "root": "",
    },
}

SYMBOL = {"USD": "$", "ILS": "₪", "EUR": "€", "GBP": "£"}


def e(s: str) -> str:
    return html.escape(s or "", quote=True)


def price(p, cur: str) -> str:
    return f"{SYMBOL.get(cur, cur + ' ')}{int(p):,}"


def mailto(addr: str, subject: str) -> str:
    return f"mailto:{addr}?subject={quote(subject)}"


def page(data: dict, lang: str) -> str:
    t = T[lang]
    contact, cur = data["contact"], data.get("currency", "USD")
    any_stripe = any(i.get("stripe") for d in data["discourses"] for i in d["items"])
    canon = "https://esoterics611.github.io/" + ("he/" if lang == "he" else "") + "dedicate.html"
    out: list[str] = []
    w = out.append
    w(f"""<!doctype html>
<html lang="{lang}" dir="{t['dir']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t['title'])}</title>
<meta name="description" content="{e(t['desc'])}">
<link rel="alternate" hreflang="en" href="https://esoterics611.github.io/dedicate.html">
<link rel="alternate" hreflang="he" href="https://esoterics611.github.io/he/dedicate.html">
<meta property="og:title" content="{e(t['h1'])}">
<meta property="og:description" content="{e(t['desc'])}">
<meta property="og:image" content="https://esoterics611.github.io/assets/og.jpg">
<meta property="og:url" content="{canon}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{t['locale']}">
<link rel="icon" href="{t['root']}assets/favicon.webp" type="image/webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@400;700&display=swap">
<link rel="stylesheet" href="{t['root']}style.css">
</head>
<body class="home store">
<!-- Built by scripts/build-dedications.py from dedications/dedications.yaml: edit those, not this. -->
<header>
  <img src="{t['root']}assets/logo.webp" alt="{e(t['logo_alt'])}">
  <a class="name" href="./">{e(t['name'])}</a>
  <nav>
""")
    for href, label in t["nav"]:
        w(f'    <a class="nav-part" href="{href}">{e(label)}</a>\n')
    lh, ll, lt = t["lang"]
    w(f'    <a class="lang-toggle" href="{lh}" lang="{ll}" hreflang="{ll}">{lt}</a>\n')
    w(f'    <a class="nav-give" href="dedicate.html" aria-current="page">{e(t["give"])}</a>\n  </nav>\n</header>\n\n<main>\n')
    w(f'  <h1 class="tagline">{e(t["h1"])}</h1>\n  <p class="lead">{e(t["lead"])}</p>\n')
    w('  <ol class="ded-steps">\n' + "".join(f"    <li>{e(s)}</li>\n" for s in t["steps"]) + "  </ol>\n")
    w('  <nav class="ded-jump" aria-label="' + e(t["h1"]) + '">\n')
    for d in data["discourses"]:
        w(f'    <a href="#{e(d["id"])}">{e(d[lang]["title"])}</a>\n')
    w("  </nav>\n")

    for d in data["discourses"]:
        dl = d[lang]
        w(f'\n  <section id="{e(d["id"])}" class="block">\n    <h2>{e(dl["title"])}</h2>\n')
        if dl.get("subtitle"):
            w(f'    <p class="small">{e(dl["subtitle"])}</p>\n')
        w('    <div class="ded-grid">\n')
        for it in d["items"]:
            il = it[lang]
            taken = (it.get("dedicated") or "").strip() and not it.get("repeat")
            w(f'      <article class="card ded" id="{e(it["id"])}">\n')
            w(f'        <p class="ded-kind">{e(t["kinds"].get(it["kind"], it["kind"]))}'
              + (f' · {e(t["repeat"])}' if it.get("repeat") else "") + "</p>\n")
            w(f'        <h3>{e(il["title"])}</h3>\n        <p>{e(il["about"])}</p>\n')
            if taken:
                w(f'        <p class="ded-taken"><b>{e(t["taken"])}:</b> <span dir="auto">{e(it["dedicated"])}</span></p>\n')
            else:
                p = it.get("price")
                w(f'        <p class="ded-price">{price(p, cur) if p is not None else e(t["arrange"])}</p>\n')
                if it.get("stripe"):
                    w(f'        <a class="btn primary" href="{e(it["stripe"])}">{e(t["dedicate"])}</a>\n')
                else:
                    subj = t["subject"].format(d=dl["title"], i=il["title"])
                    w(f'        <a class="btn" href="{e(mailto(contact, subj))}">{e(t["write"])}</a>\n')
            w("      </article>\n")
        w("    </div>\n  </section>\n")

    w(f'\n  <p class="small ded-pay">{e(t["pay_stripe"] if any_stripe else t["pay_mail"])}</p>\n')
    w(f'  <div class="cta-band">\n    <h3>{e(t["other_h"])}</h3>\n    <p>{e(t["other_p"])}</p>\n'
      f'    <a class="btn primary" href="{e(mailto(contact, t["subject"].format(d=t["name"], i=t["other_h"])))}">{e(t["write"])}</a>\n  </div>\n</main>\n\n<footer>\n')
    for href, label in t["foot"]:
        w(f'  <a href="{href}">{e(label)}</a>\n')
    w(f'  <a href="{e(mailto(contact, t["subject"].format(d=t["name"], i=t["contact"])))}">{e(t["contact"])} ({e(contact)})</a>\n')
    w(f'  <a href="{lh}" lang="{ll}">{lt}</a>\n  <div>© 2026 Ronnie Rendel · Sefer Forge</div>\n</footer>\n</body>\n</html>\n')
    return "".join(out)


def check(data: dict) -> list[str]:
    errs, seen = [], set()
    for d in data.get("discourses", []):
        for it in d.get("items", []):
            iid = it.get("id", "?")
            if iid in seen:
                errs.append(f"{iid}: id used twice")
            seen.add(iid)
            for lang in ("he", "en"):
                if not (it.get(lang) or {}).get("title") or not (it.get(lang) or {}).get("about"):
                    errs.append(f"{iid}: {lang} title or about missing")
            if it.get("kind") not in T["en"]["kinds"]:
                errs.append(f"{iid}: unknown kind {it.get('kind')!r}")
            if it.get("price") is not None and not (isinstance(it["price"], int) and it["price"] > 0):
                errs.append(f"{iid}: price must be a whole number above 0, or null")
            if it.get("stripe") and not str(it["stripe"]).startswith("https://buy.stripe.com/"):
                errs.append(f"{iid}: stripe must be a Stripe Payment Link (https://buy.stripe.com/...)")
    return errs


def main() -> int:
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    errs = check(data)
    if errs:
        print("dedications.yaml:\n  " + "\n  ".join(errs), file=sys.stderr)
        return 1
    (ROOT / "site" / "he" / "dedicate.html").write_text(page(data, "he"), encoding="utf-8")
    (ROOT / "site" / "dedicate.html").write_text(page(data, "en"), encoding="utf-8")
    n = sum(len(d["items"]) for d in data["discourses"])
    print(f"dedications: {n} items in {len(data['discourses'])} groups -> site/he/dedicate.html, site/dedicate.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
