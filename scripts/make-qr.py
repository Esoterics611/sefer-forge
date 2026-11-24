#!/usr/bin/env python3
"""A QR code as an SVG, for print: python scripts/make-qr.py <url> <out.svg> [--ecc M]

Black modules on white, a quiet zone of four modules, no fixed size (the stylesheet sets it). Made with
ReportLab's QR encoder, which the PDF tools already install. The printed codes:

    templates/qr-sefer-forge-he.svg   https://esoterics611.github.io/he/   (the back of a printed ביאור)
"""
import sys

from reportlab.graphics.barcode.qr import QrCodeWidget


def svg(url: str, ecc: str = "M") -> str:
    w = QrCodeWidget(url, barLevel=ecc)
    w.qr.make()
    n = w.qr.getModuleCount()
    q = 4
    rects = []
    for r in range(n):
        c = 0
        while c < n:
            if w.qr.isDark(r, c):
                s = c
                while c < n and w.qr.isDark(r, c):
                    c += 1
                rects.append(f'<rect x="{s + q}" y="{r + q}" width="{c - s}" height="1"/>')
            else:
                c += 1
    size = n + 2 * q
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" shape-rendering="crispEdges">'
            f'<rect width="{size}" height="{size}" fill="#fff"/><g fill="#000">{"".join(rects)}</g></svg>\n')


def main(argv: list[str]) -> int:
    ecc = "M"
    if "--ecc" in argv:
        i = argv.index("--ecc")
        ecc = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if len(argv) != 2:
        print(__doc__)
        return 2
    url, out = argv
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg(url, ecc))
    print(f"wrote {out}: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
