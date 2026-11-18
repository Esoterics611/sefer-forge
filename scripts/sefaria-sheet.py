#!/usr/bin/env python3
"""Put a ביאור on Sefaria as a source sheet, its quotations linked to the library.

Usage:
    python scripts/sefaria-sheet.py <biur-dir>               # build output/sefaria/<name>.json and <name>.paste.js
    python scripts/sefaria-sheet.py <biur-dir> --deploy      # a ביאור not on Sefaria yet: only at Ronnie's command
    python scripts/sefaria-sheet.py <biur-dir> --record ID   # after the paste made a new sheet: record its number
    python scripts/sefaria-sheet.py --beside                 # which sheets Sefaria lists beside their passages

The sheet is built from `biur.src.md` the way `build-biur.py` builds the print:
the explanation paragraphs, the meaning blocks ("בנפש האדם"), the terms key, and
each directive replaced by its text. Where the work is on Sefaria (a `sefaria:`
link in sources/sources.yaml), a quotation goes in as a *linked* source: its
Sefaria address, so the sheet is listed in that passage's side panel. A work
Sefaria lacks (נהר שלום, חסדי דוד, a transcription) goes in as text, on a tinted
ground under its label. Every address is checked against Sefaria (cached in
output/sefaria/refs.json); one that does not resolve goes in as text, and is
reported.

The paste (`<name>.paste.js`) runs in the browser console on voices.sefaria.org,
logged in: it saves the sheet under its number in sefaria/sheets.yaml (the link
already shared keeps working; summary and topics stay as published unless the
record gives them), or makes a new one and publishes it, and adds it to the
collection. The record, sefaria/sheets.yaml, is the list of what is up.

A ביאור is kept apart from the teacher's work until he commands it deployed
(CLAUDE.md): a ביאור not in the record is refused without --deploy.
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

import sourcelib as S

ROOT = S.ROOT
RECORD = ROOT / "sefaria" / "sheets.yaml"
OUT = ROOT / "output" / "sefaria"
CACHE = OUT / "refs.json"
API = "https://www.sefaria.org"
TINT_SOURCE = "#f4efe4"      # a quotation from a work Sefaria lacks (as the published sheets)
TINT_MEANING = "#eef3f7"     # the meaning layer, "בנפש האדם"

spec = importlib.util.spec_from_file_location("build_biur", ROOT / "scripts" / "build-biur.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)


# --- Sefaria addresses ---------------------------------------------------------

def book_title(work: str) -> str | None:
    url = S.catalog()[work].get("sefaria")
    return urllib.parse.unquote(url.rstrip("/").rsplit("/", 1)[1]).replace("_", " ") if url else None


def split_addr(addr: str) -> tuple[list[str], list[str]]:
    """'Gate of Prayer.7.3' -> (['Gate of Prayer'], ['7', '3']); '49.5.1' -> ([], ['49', '5', '1'])."""
    parts = addr.split(".")
    i = 0
    while i < len(parts) and not re.fullmatch(r"\d+[ab]?", parts[i]):
        i += 1
    return parts[:i], parts[i:]


def to_ref(work: str, addrs: list[str]) -> str | None:
    """Sefaria's address for consecutive paragraphs of a work, or None if it has none."""
    title = book_title(work)
    if not title or not addrs:
        return None
    names, first = split_addr(addrs[0])
    head = ", ".join([title] + names)
    ref = f"{head} {':'.join(first)}" if first else head
    if len(addrs) > 1:
        names2, last = split_addr(addrs[-1])
        if names2 != names or len(last) != len(first):
            return None
        k = next((i for i in range(len(first)) if first[i] != last[i]), len(first))
        if k < len(first):
            ref += "-" + ":".join(last[k:])
    return ref


_cache: dict | None = None


def resolve(ref: str) -> dict | None:
    """{'ref', 'heRef'} as Sefaria normalises it, or None if Sefaria does not know it."""
    global _cache
    if _cache is None:
        _cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.is_file() else {}
    if ref not in _cache:
        url = f"{API}/api/texts/{urllib.parse.quote(ref)}?context=0&commentary=0&pad=0"
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                j = json.load(r)
            _cache[ref] = {"ref": j["ref"], "heRef": j["heRef"]} if j.get("ref") and not j.get("error") else None
        except Exception:
            return None                     # offline or refused: not cached, tried again next time
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(_cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return _cache[ref]


def locate_stretch(work: str, stretch: str) -> list[str]:
    """The addresses in `work` from the paragraph holding the stretch's first words to the one
    holding its last (empty if either is not found once)."""
    words = stretch.split()
    if len(words) < 4:
        return []
    head = S.find(work, " ".join(words[:6]))
    tail = S.find(work, " ".join(words[-6:]))
    if len(head) != 1 or not tail:
        return []
    keys = list(S.paragraphs(work))
    a = keys.index(head[0][0])
    b = max((keys.index(t[0]) for t in tail if keys.index(t[0]) >= a), default=-1)
    return keys[a:b + 1] if b >= a else []


# --- the sheet -----------------------------------------------------------------

def md_to_html(chunks: list[str]) -> list[str]:
    """Markdown to HTML, all chunks in one pandoc run."""
    if not chunks:
        return []
    sep = "\n\nSEFARIASPLIT{}\n\n"
    joined = "".join(c + sep.format(i) for i, c in enumerate(chunks))
    out = subprocess.run(["pandoc", "--from", "markdown-auto_identifiers-smart", "--to", "html", "--wrap=none"],
                         input=joined, capture_output=True, text=True, check=True).stdout
    parts = re.split(r"<p>SEFARIASPLIT\d+</p>\n?", out)
    return [p.strip() for p in parts[: len(chunks)]]


def build_sheet(src: Path) -> tuple[dict, list[str]]:
    raw = src.read_text(encoding="utf-8")
    _, fm, body = raw.split("---", 2)
    meta = yaml.safe_load(fm) or {}
    first_line = raw[: len(raw) - len(body)].count("\n") + 1
    errs = B.lint(body, first_line)
    if errs:
        raise SystemExit("the source breaks prompts/biur-rules.md:\n  " + "\n  ".join(errs))
    blocks = B.meaning_blocks(body)
    cursor = B.TextCursor(meta)
    text_work = None
    if meta.get("text_file"):
        tf = (ROOT / meta["text_file"]).read_text(encoding="utf-8")
        text_work = (yaml.safe_load(tf.split("---", 2)[1]) or {}).get("work") if tf.startswith("---") else None

    items: list[tuple[str, object]] = []     # ("md", markdown) | ("source", dict) | ("tinted", (label, markdown))
    para: list[str] = []
    notes = {"linked": 0, "text": 0, "unresolved": []}

    def flush():
        if any(x.strip() for x in para):
            items.append(("md", "\n".join(para)))
        para.clear()

    in_meaning = False
    lines = body.split("\n")
    for no, line in enumerate(lines, first_line):
        s = line.strip()
        if s.startswith("[") and re.search(r"\]\{\.(bsd|subtitle)\}$", s) or re.match(r"^# ", line):
            continue                                            # the title block: the sheet has its own title
        if s == B.MEANING_OPEN:
            flush(); in_meaning = True; continue
        if s.startswith(":::"):
            if in_meaning and s == ":::":
                items.append(("meaning", "\n".join(para))); para.clear(); in_meaning = False
            continue                                            # other fenced divs (.keep): the fence only
        m = B.DIRECTIVE.match(line)
        if not m:
            para.append(line)
            continue
        flush()
        kind, d = m.group(1), B.args_of(m.group(2), no)
        where = f"line {no}"
        if kind == "text":
            t = B.bold(cursor.take(d, where), d.get("mark"), where)
            addrs = locate_stretch(text_work, re.sub(r"\*\*", "", t)) if text_work else []
            items.append(link_or_tint(text_work, addrs, t, "", notes, where))
            continue
        if kind == "source":
            text, _ = B.source_text(d, where)
            label = d.get("label") or " · ".join(x for x in (S.catalog()[d["work"]]["title"],
                                                              S.gate_title(d["work"], d.get("ref", "").split(",")[0]) if d.get("ref") else "") if x)
        else:
            text, _ = B.file_text(d, where)
            label = d.get("label") or Path(d["path"]).stem
        passage, head, tail = B.cut(text, d.get("from"), d.get("to"), where)
        passage = B.emend(B.bold(passage, d.get("mark"), where), d.get("emend"), where)
        passage = ("… " if head else "") + passage + (" …" if tail else "")
        addrs = [r.strip() for r in d.get("ref", "").split(",") if r.strip()] if kind == "source" else []
        items.append(link_or_tint(d.get("work") if kind == "source" else None, addrs, passage, label, notes, where))
    flush()
    key = B.terms_key(blocks)
    if key:
        items.append(("md", "\n".join(key)))

    # One pandoc run for every piece of markdown.
    md = [x[1] if x[0] in ("md", "meaning") else x[1]["md"] for x in items if x[0] != "tinted"] \
        + [x[1][1] for x in items if x[0] == "tinted"]
    html_of = dict(zip(range(len(md)), md_to_html(md)))
    n_plain = sum(1 for x in items if x[0] != "tinted")
    sources, i_plain, i_tint = [], 0, n_plain
    for kind, v in items:
        if kind == "tinted":
            label, _ = v
            h = html_of[i_tint]; i_tint += 1
            lab = f"<small>{html.escape(label)}</small><br>\n" if label else ""
            sources.append({"outsideText": f'<div style="background-color: {TINT_SOURCE};">{lab}{h}</div>'})
            continue
        h = html_of[i_plain]; i_plain += 1
        if kind == "meaning":
            sources.append({"outsideText": f'<div style="background-color: {TINT_MEANING};"><b>בנפש האדם</b><br>\n{h}</div>'})
        elif kind == "source":
            sources.append({"ref": v["ref"], "heRef": v["heRef"], "text": {"he": h, "en": ""}})
        else:
            for piece in split_blocks(h):
                sources.append({"outsideText": piece})
    sources = drop_empty_headings(sources)
    for n, x in enumerate(sources, 1):
        x["node"] = n
    title = f"{meta.get('title', '')}: {meta['subtitle']}" if meta.get("subtitle") else meta.get("title", "")
    sheet = {"title": title, "sources": sources, "nextNode": len(sources) + 1,
             "options": {"language": "hebrew", "layout": "stacked", "numbered": 0}}
    report = [f"{len(sources)} pieces: {notes['linked']} linked passage(s), {notes['text']} quotation(s) as text"]
    if cursor.text:
        report.append(cursor.report())
    report += [f"  not on Sefaria at {r} ({w}): set as text" for r, w in notes["unresolved"]]
    return sheet, report


def link_or_tint(work, addrs, passage_md, label, notes, where):
    ref = to_ref(work, addrs) if work else None
    got = resolve(ref) if ref else None
    if got:
        notes["linked"] += 1
        return ("source", {"md": passage_md, **got})
    if ref:
        notes["unresolved"].append((ref, where))
    notes["text"] += 1
    return ("tinted", (label, passage_md))


def heading_rank(x: dict) -> int | None:
    t = x.get("outsideText", "")
    if t.startswith("<p><b><big>") and t.endswith("</big></b></p>"):
        return 2
    if re.fullmatch(r"<p><b>[^<]*</b></p>", t):
        return 3
    return None


def drop_empty_headings(sources: list[dict]) -> list[dict]:
    """A heading with nothing under it (a part not yet written) is left out of the sheet."""
    out = []
    for x in reversed(sources):
        r = heading_rank(x)
        if r is not None:
            nxt = heading_rank(out[-1]) if out else 0
            if not out or (nxt is not None and nxt <= r):
                continue
        out.append(x)
    return out[::-1]


def split_blocks(h: str) -> list[str]:
    """A run of explanation HTML as one sheet piece per paragraph, heading, list or table;
    headings as the published sheets have them (<p><b><big>…</big></b></p>)."""
    h = re.sub(r"<h2[^>]*>(.*?)</h2>", r"<p><b><big>\1</big></b></p>", h, flags=re.S)
    h = re.sub(r"<h[3-6][^>]*>(.*?)</h[3-6]>", r"<p><b>\1</b></p>", h, flags=re.S)
    out = [m.group(0) for m in re.finditer(r"<(p|ul|ol|table|blockquote|div)\b.*?</\1>", h, flags=re.S)]
    return out or ([h] if h.strip() else [])


# --- the paste -------------------------------------------------------------------

PASTE = r"""(async () => {
  // Made by scripts/sefaria-sheet.py from %(src)s. Paste in the console on voices.sefaria.org, logged in.
  const SHEET = %(sheet)s;
  const ID = %(id)s, COLLECTION = %(slug)s, SUMMARY = %(summary)s, TOPICS = %(topics)s;
  const log = [], say = s => { console.log(s); log.push(s); };
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const csrf = (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '';
  const uid = window.Sefaria && Sefaria._uid;
  if (!uid) { alert('Not logged in on this tab.'); return; }
  const getJ = async u => (await fetch(u, { credentials: 'include' })).json();
  const save = async o => {
    const f = new FormData(); f.append('json', JSON.stringify(o));
    try {
      const r = await fetch('/api/sheets', { method: 'POST', body: f, credentials: 'include', headers: { 'X-CSRFToken': csrf } });
      if (r.status >= 500) return { error: 'HTTP ' + r.status, retry: true };
      return await r.json();
    } catch (e) { return { error: String(e), retry: true }; }
  };
  let id = ID;
  if (!id) {
    const r = await save({ ...SHEET, status: 'unlisted', summary: SUMMARY || '', topics: TOPICS || [] });
    if (!r.id) { alert('Not made: ' + JSON.stringify(r).slice(0, 300)); return; }
    id = r.id; say('made sheet ' + id + ' (record it: scripts/sefaria-sheet.py <dir> --record ' + id + ')');
  }
  // Save the content (an existing sheet keeps its status, summary and topics unless the record gives them),
  // then make it public; a 504 means Sefaria is still working: look again before saving again.
  let done = false, content = !!ID ? false : true;
  for (let i = 0; i < 6 && !done; i++) {
    const cur = await getJ('/api/sheets/' + id);
    if (cur.error) { say(cur.error); break; }
    if (cur.owner !== uid) { say('not your sheet'); break; }
    if (content && cur.status === 'public') { done = true; break; }
    const body = { ...SHEET, id, lastModified: cur.dateModified,
                   status: content ? 'public' : cur.status,
                   summary: SUMMARY || cur.summary || '', topics: TOPICS || cur.topics || [] };
    const r = await save(body);
    if (r.error && !r.retry && r.error !== 'Sheet updated.') { say(r.error); break; }
    if (!r.error && !content) { content = true; say('content saved'); if (cur.status === 'public') done = true; }
    await sleep(r.error ? 20000 : 1500);
  }
  say((done ? 'public: ' : 'NOT finished, paste again: ') + 'https://www.sefaria.org/sheets/' + id);
  if (COLLECTION) {
    const r = await (await fetch('/api/collections/' + encodeURIComponent(COLLECTION) + '/add/' + id,
      { method: 'POST', credentials: 'include', headers: { 'X-CSRFToken': csrf } })).json();
    say('in the collection: ' + (r.status || r.error));
  }
  alert(log.join('\n'));
})();
"""


def load_record() -> dict:
    return yaml.safe_load(RECORD.read_text(encoding="utf-8"))


def entry_for(record: dict, src_rel: str) -> dict | None:
    return next((s for s in record["sheets"] if s.get("made_from") == src_rel), None)


def beside(record: dict) -> int:
    """For each sheet: is it listed beside its first linked passages?"""
    for s in record["sheets"]:
        try:
            with urllib.request.urlopen(f"{API}/api/sheets/{s['id']}", timeout=60) as r:
                sh = json.load(r)
        except Exception as e:
            print(f"{s['id']}: {e}"); continue
        refs = list(dict.fromkeys(x["ref"] for x in sh.get("sources", []) if "ref" in x))[:3]
        hits = 0
        for ref in refs:
            with urllib.request.urlopen(f"{API}/api/related/{urllib.parse.quote(ref)}", timeout=60) as r:
                ids = {str(x.get("id")) for x in json.load(r).get("sheets", [])}
            hits += str(s["id"]) in ids
        print(f"{s['id']}  {len(refs) and f'{hits}/{len(refs)} passages tried list it' or 'no linked passages'}  {s['title']}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dir", nargs="?", help="a biur folder (holding biur.src.md)")
    ap.add_argument("--deploy", action="store_true", help="put a ביאור on Sefaria for the first time (Ronnie's command)")
    ap.add_argument("--record", type=int, metavar="ID", help="record the number of the sheet the paste made")
    ap.add_argument("--beside", action="store_true", help="check which sheets Sefaria lists beside their passages")
    a = ap.parse_args(argv)
    record = load_record()
    if a.beside:
        return beside(record)
    if not a.dir:
        ap.error("a biur folder is needed")
    src = ROOT / a.dir / "biur.src.md" if (ROOT / a.dir).is_dir() else ROOT / a.dir
    if not src.is_file():
        ap.error(f"no {src.relative_to(ROOT)}")
    rel = str(src.relative_to(ROOT))
    entry = entry_for(record, rel)
    sheet, report = build_sheet(src)
    if a.record:
        if entry:
            ap.error(f"{rel} is already sheet {entry['id']}")
        e = {"id": a.record, "title": sheet["title"], "discourse": rel.split("/")[1], "made_from": rel,
             "linked": sum(1 for x in sheet["sources"] if "ref" in x), "beside": "unchecked", "status": "public"}
        block = yaml.safe_dump([e], allow_unicode=True, sort_keys=False, width=1000)
        block = "".join("  " + ln + "\n" for ln in block.splitlines())
        RECORD.write_text(RECORD.read_text(encoding="utf-8").rstrip("\n") + "\n" + block, encoding="utf-8")
        print(f"recorded sheet {a.record} for {rel} in {RECORD.relative_to(ROOT)}")
        return 0
    if not entry and not a.deploy:
        print(f"{rel} is not on Sefaria. A ביאור goes out only at Ronnie's command: --deploy.", file=sys.stderr)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    name = rel.split("/")[1] + ("" if src.parent.name == "biur" else "-" + src.parent.name.replace("biur-", ""))
    js_ = lambda v: json.dumps(v, ensure_ascii=False)
    (OUT / f"{name}.json").write_text(json.dumps(sheet, ensure_ascii=False, indent=1), encoding="utf-8")
    paste = PASTE % {"src": rel, "sheet": js_(sheet), "id": js_(entry["id"] if entry else None),
                     "slug": js_(record["collection"].get("slug")),
                     "summary": js_((entry or {}).get("summary")), "topics": js_((entry or {}).get("topics"))}
    (OUT / f"{name}.paste.js").write_text(paste, encoding="utf-8")
    print(f"{rel} -> output/sefaria/{name}.json, {name}.paste.js "
          f"({'updates sheet ' + str(entry['id']) if entry else 'makes a new sheet'})")
    for line in report:
        print("  " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
