#!/usr/bin/env python3
"""Cut a session's page photos into overlapping strips for OCR.

Usage:
    python scripts/ocr-strips.py discourses/003-breishis/sessions/002
    python scripts/ocr-strips.py <session> --lines 5          # lines per strip (default 6)
    python scripts/ocr-strips.py <session> --columns 2        # a photo of two columns

A whole page photo shown at once is scaled down until small print blurs, and
that is where words get dropped. Each strip here is a few lines of the photo
at full resolution, rotated upright (EXIF), in contrast-stretched grayscale.
Cuts fall in the white space between text lines, never through a line, and
each strip repeats the last line of the one before it, so every line is read
whole at least once and the overlap shows where one strip continues the next.
When no line pattern is found the photo is cut into fixed overlapping strips.

With --columns N the photo is first split into N columns, right to left
(Hebrew reading order), each cut into strips of its own.

Writes output/strips/<discourse>-<session>/<photo>-<column><NN>.png and prints
each strip with the lines it holds. Never changes the photos.
"""
from __future__ import annotations

import sys
from pathlib import Path

import forgelib as F

try:
    from PIL import Image, ImageFilter, ImageOps
except ImportError:
    print("Missing dependency. Install with: pip install -r requirements.txt")
    sys.exit(1)

OUT = Path("output/strips")
LINES = 6
FALLBACK_STRIPS = 9          # strips per column when no line pattern is found
FALLBACK_OVERLAP = 0.15


def prepare(path: Path) -> Image.Image:
    im = ImageOps.exif_transpose(Image.open(path)).convert("L")
    im = ImageOps.autocontrast(im, cutoff=1)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))


def text_bands(im: Image.Image) -> list[tuple[int, int]]:
    """(top, bottom) rows of each text line, from the ink along each row of the
    column's middle (the edges carry the facing page)."""
    w, h = im.size
    scale = 600 / w
    small = im.resize((600, max(1, int(h * scale))))
    sw, sh = small.size
    px = small.load()
    x0, x1 = int(sw * 0.12), int(sw * 0.88)
    ink = []
    for y in range(sh):
        dark = sum(1 for x in range(x0, x1, 2) if px[x, y] < 110)
        ink.append(dark / ((x1 - x0) / 2))
    s = sorted(ink)
    floor, peak = s[len(s) // 10], s[int(len(s) * 0.95)]
    if peak - floor < 0.04:
        return []
    cut = floor + (peak - floor) * 0.18
    bands, start = [], None
    for y, v in enumerate(ink + [0.0]):
        if v > cut and start is None:
            start = y
        elif v <= cut and start is not None:
            if y - start >= 2:
                bands.append((int(start / scale), int(y / scale)))
            start = None
    if len(bands) < 4:
        return []
    # Merge slivers (a line's ascenders split off) into their line.
    heights = sorted(b - a for a, b in bands)
    typical = heights[len(heights) // 2]
    merged: list[list[int]] = []
    for a, b in bands:
        if merged and (b - a < typical * 0.45 or a - merged[-1][1] < typical * 0.15):
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return [(a, b) for a, b in merged]


def strips_for(im: Image.Image, lines: int) -> list[tuple[int, int, str]]:
    """(top, bottom, which lines) for each strip of one column image."""
    w, h = im.size
    bands = text_bands(im)
    if not bands:
        step = h / FALLBACK_STRIPS
        pad = int(step * FALLBACK_OVERLAP)
        return [(max(0, int(i * step) - pad), min(h, int((i + 1) * step) + pad), "fixed cut")
                for i in range(FALLBACK_STRIPS)]
    gap = lambda i: (bands[i][1] + bands[i + 1][0]) // 2 if i + 1 < len(bands) else min(h, bands[i][1] + 20)
    out, first = [], 0
    while first < len(bands):
        last = min(len(bands) - 1, first + lines - 1)
        top = 0 if first == 0 else gap(first - 1)
        bottom = h if last == len(bands) - 1 else gap(last)
        out.append((top, bottom, f"lines {first + 1}–{last + 1} of {len(bands)}"))
        if last == len(bands) - 1:
            break
        first = last                      # the next strip repeats this strip's last line
    return out


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    opts = {a.split("=")[0]: a for a in argv if a.startswith("--")}

    def opt(name: str, default: int) -> int:
        if name in argv:
            return int(argv[argv.index(name) + 1])
        return int(opts[name].split("=")[1]) if name in opts and "=" in opts[name] else default

    lines, columns = opt("--lines", LINES), opt("--columns", 1)
    args = [a for a in args if not a.isdigit()]
    if len(args) != 1:
        print("Usage: python scripts/ocr-strips.py <session-path> [--lines N] [--columns N]")
        return 1
    session = Path(args[0].rstrip("/"))
    photos = F.image_files(session)
    if not photos:
        print(f"No photos in {session / 'images'}")
        return 1
    out = OUT / f"{F.discourse_of(session).name}-{session.name}"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()
    for photo in photos:
        im = prepare(photo)
        w, h = im.size
        print(f"{photo.name}  ({w}×{h})")
        for c in range(columns):
            # Right to left: column a is the rightmost. A 3% overlap keeps edge letters.
            x1 = int(w * (columns - c) / columns + w * 0.03) if c else w
            x0 = max(0, int(w * (columns - c - 1) / columns - w * 0.03))
            col = im.crop((x0, 0, min(w, x1), h))
            tag = "abcdefgh"[c] if columns > 1 else ""
            for n, (top, bottom, what) in enumerate(strips_for(col, lines), 1):
                f = out / f"{photo.stem}-{tag}{n:02d}.png"
                col.crop((0, top, col.size[0], bottom)).save(f)
                print(f"  {f}   {what}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
