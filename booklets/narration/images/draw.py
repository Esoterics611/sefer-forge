#!/usr/bin/env python3
"""Draw the narration pictures: original vector art, one SVG (1920x1080) per plan.

Usage:
    python booklets/narration/images/draw.py                    # every drawing
    python booklets/narration/images/draw.py the-locked-gate    # one, by its plan's name

Writes booklets/narration/images/<name>.svg, which the plan's `image:` names;
scripts/build-narration.py renders it with headless Chrome and lays the series
and the title over the lower part, so keep what matters above y = 620.
Each drawing is a function below, with its own random seed, so redrawing gives
the same picture: after changing a shared helper (pine, ridge, svg), check with
`git diff` that the earlier drawings are unchanged.
"""
import math
import random
import sys
from pathlib import Path

W, H = 1920, 1080
HERE = Path(__file__).resolve().parent


def svg(defs: str, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f"<defs>{defs}</defs>{body}</svg>\n")


def pine(x: float, base: float, h: float, rnd: random.Random) -> str:
    """A spruce silhouette: a jagged cone of tiers."""
    w = h * rnd.uniform(0.32, 0.4)
    tiers = max(5, int(h / 26))
    pts = [(x, base - h)]
    left, right = [], []
    for i in range(1, tiers + 1):
        t = i / tiers
        y = base - h + t * h * 0.92
        half = w / 2 * t * rnd.uniform(0.9, 1.1)
        inner = half * 0.55
        right += [(x + half, y), (x + inner, y - h * 0.02)]
        left += [(x - half, y), (x - inner, y - h * 0.02)]
    trunk = max(2.0, h * 0.025)
    pts += right + [(x + trunk, base - h * 0.08), (x + trunk, base), (x - trunk, base), (x - trunk, base - h * 0.08)]
    pts += list(reversed(left))
    return "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + "Z"


def ridge(rnd: random.Random, y: float, amp: float, step: int = 40) -> str:
    pts = [(0, H), (0, y)]
    for x in range(0, W + step, step):
        pts.append((x, y + amp * math.sin(x / 260 + rnd.random()) + rnd.uniform(-amp, amp) * 0.3))
    pts.append((W, H))
    return "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + "Z"


def forest() -> str:
    rnd = random.Random(7)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#070b1d"/><stop offset="0.45" stop-color="#16244a"/>
      <stop offset="0.7" stop-color="#3a4d78"/><stop offset="1" stop-color="#22304f"/>
    </linearGradient>
    <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#fff6dc" stop-opacity="0.55"/><stop offset="0.25" stop-color="#e8e2c8" stop-opacity="0.22"/>
      <stop offset="1" stop-color="#9fb0d8" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="moon" cx="0.42" cy="0.4" r="0.6">
      <stop offset="0" stop-color="#fffbea"/><stop offset="1" stop-color="#e9dfbf"/>
    </radialGradient>
    <linearGradient id="path" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="#b8c2d8" stop-opacity="0.55"/><stop offset="1" stop-color="#dfe4ef" stop-opacity="0.1"/>
    </linearGradient>
    <filter id="blur8"><feGaussianBlur stdDeviation="8"/></filter>
    <filter id="blur30"><feGaussianBlur stdDeviation="30"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    for _ in range(260):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H * 0.55) ** 1.0
        if math.hypot(x - 1390, y - 210) < 260:
            continue
        r = rnd.choice([0.7, 0.9, 1.1, 1.4, 1.9])
        b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#f4f1e6" opacity="{rnd.uniform(0.3, 0.95):.2f}"/>')
    b.append('<circle cx="1390" cy="210" r="430" fill="url(#halo)"/>')
    b.append('<circle cx="1390" cy="210" r="92" fill="url(#moon)"/>')
    b.append('<circle cx="1362" cy="192" r="14" fill="#d9cfae" opacity="0.35"/>'
             '<circle cx="1418" cy="242" r="20" fill="#d9cfae" opacity="0.3"/>'
             '<circle cx="1405" cy="174" r="8" fill="#d9cfae" opacity="0.3"/>')
    b.append(f'<path d="{ridge(rnd, 440, 26)}" fill="#2b3a5e"/>')
    # mist over the far ridge
    b.append('<ellipse cx="900" cy="480" rx="900" ry="60" fill="#c9d3ea" opacity="0.18" filter="url(#blur30)"/>')
    layers = [(520, (60, 120), "#1d2947", 70), (580, (110, 200), "#131c35", 46), (650, (190, 320), "#0b1124", 30)]
    for base, (lo, hi), col, n in layers:
        trees = []
        for i in range(n):
            x = rnd.uniform(-40, W + 40)
            if base > 530 and 760 < x < 1160:          # leave the clearing open
                continue
            trees.append(pine(x, base + rnd.uniform(-12, 12), rnd.uniform(lo, hi), rnd))
        b.append(f'<path d="{" ".join(trees)}" fill="{col}"/>')
        b.append(f'<path d="{ridge(rnd, base - 6, 7, 60)}" fill="{col}"/>')
        b.append(f'<ellipse cx="960" cy="{base + 4}" rx="1100" ry="26" fill="#c9d3ea" opacity="0.08" filter="url(#blur30)"/>')
    # the path through the clearing, toward the moon
    b.append('<path d="M740,1080 C850,900 1010,800 930,700 C895,655 960,615 985,596 L1000,596 '
             'C992,620 940,655 975,705 C1060,800 960,930 1010,1080 Z" fill="url(#path)"/>')
    # the boy with his stick, walking the path at the forest's edge
    b.append('<g transform="translate(966,598)" fill="#05070f" stroke="#05070f" stroke-linecap="round">'
             '<circle cx="0" cy="-60" r="8" stroke="none"/>'
             '<path d="M-8,-51 L8,-51 L12,-21 L-12,-21 Z" stroke="none"/>'
             '<path d="M-4,-22 L-10,0 M4,-22 L9,0" stroke-width="4.5" fill="none"/>'
             '<path d="M8,-46 L20,-34" stroke-width="4" fill="none"/>'
             '<path d="M19,-78 L25,1" stroke-width="3.4" fill="none"/>'
             '</g>')
    # nearest trees framing the picture
    near = [pine(x, 1090, h, rnd) for x, h in [(40, 980), (190, 820), (330, 700), (1600, 760), (1750, 900), (1890, 1000)]]
    b.append(f'<path d="{" ".join(near)}" fill="#04060d"/>')
    return svg(defs, "".join(b))


def gate() -> str:
    rnd = random.Random(11)
    cx = W / 2
    defs = """
    <radialGradient id="glow" cx="0.5" cy="0.4" r="0.75">
      <stop offset="0" stop-color="#fff4d2"/><stop offset="0.18" stop-color="#f2c873"/>
      <stop offset="0.42" stop-color="#9a5a62"/><stop offset="0.75" stop-color="#2c1840"/>
      <stop offset="1" stop-color="#0d0818"/>
    </radialGradient>
    <linearGradient id="door" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#5a3c1c"/><stop offset="1" stop-color="#2a1a0c"/>
    </linearGradient>
    <linearGradient id="stone" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#8f7146"/><stop offset="0.5" stop-color="#d9b56c"/><stop offset="1" stop-color="#8f7146"/>
    </linearGradient>
    <linearGradient id="lock" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#f7dc8e"/><stop offset="0.5" stop-color="#c8963c"/><stop offset="1" stop-color="#7d5620"/>
    </linearGradient>
    <filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>
    <filter id="blur10"><feGaussianBlur stdDeviation="10"/></filter>
    <filter id="blur40"><feGaussianBlur stdDeviation="40"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#glow)"/>']
    # rays from behind the gate
    for i in range(36):
        a = math.radians(i * 10 + rnd.uniform(-3, 3))
        spread = math.radians(rnd.uniform(1.2, 2.6))
        r = 1500
        p1 = (cx + r * math.cos(a - spread), 430 + r * math.sin(a - spread))
        p2 = (cx + r * math.cos(a + spread), 430 + r * math.sin(a + spread))
        b.append(f'<path d="M{cx},430 L{p1[0]:.0f},{p1[1]:.0f} L{p2[0]:.0f},{p2[1]:.0f} Z" '
                 f'fill="#fff1c9" opacity="{rnd.uniform(0.04, 0.1):.2f}"/>')
    for _ in range(120):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H * 0.6)
        if abs(x - cx) < 420 and y < 800:
            continue
        b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.choice([0.8, 1.1, 1.5])}" fill="#fff6e0" '
                 f'opacity="{rnd.uniform(0.3, 0.8):.2f}"/>')
    # the gate: an arch of stone, two closed doors, light at the seam, the great lock
    gw, top, base = 470, 80, 840
    arch_r = gw / 2
    outer = (f"M{cx - gw / 2 - 46},{base} L{cx - gw / 2 - 46},{top + arch_r} "
             f"A{arch_r + 46},{arch_r + 46} 0 0 1 {cx + gw / 2 + 46},{top + arch_r} L{cx + gw / 2 + 46},{base} Z")
    inner = (f"M{cx - gw / 2},{base} L{cx - gw / 2},{top + arch_r + 10} "
             f"A{arch_r},{arch_r} 0 0 1 {cx + gw / 2},{top + arch_r + 10} L{cx + gw / 2},{base} Z")
    b.append(f'<path d="{outer}" fill="#fff0c0" opacity="0.5" filter="url(#blur40)"/>')
    b.append(f'<path d="{outer}" fill="url(#stone)"/>')
    for k in range(13):                               # the arch's stones
        a = math.pi + k * math.pi / 12
        x1, y1 = cx + arch_r * math.cos(a), top + arch_r + 10 + arch_r * math.sin(a)
        x2, y2 = cx + (arch_r + 46) * math.cos(a), top + arch_r + (arch_r + 46) * math.sin(a)
        b.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#6e5530" stroke-width="3"/>')
    b.append(f'<path d="{inner}" fill="url(#door)"/>')
    for side in (-1, 1):                              # door panels
        x0 = cx + side * gw / 4
        for y0, h in ((top + arch_r + 60, 200), (top + arch_r + 290, 200), (top + arch_r + 520, 150)):
            b.append(f'<rect x="{x0 - 80:.0f}" y="{y0}" width="160" height="{h}" rx="6" fill="none" '
                     f'stroke="#c9a45c" stroke-width="3" opacity="0.75"/>')
    b.append(f'<line x1="{cx}" y1="{top + 40}" x2="{cx}" y2="{base}" stroke="#fff8dc" stroke-width="10" filter="url(#blur10)"/>')
    b.append(f'<line x1="{cx}" y1="{top + 40}" x2="{cx}" y2="{base}" stroke="#fffbe8" stroke-width="3"/>')
    ly = 430
    b.append(f'<rect x="{cx - 150}" y="{ly - 62}" width="300" height="22" rx="4" fill="url(#lock)" stroke="#5a3d14" stroke-width="3"/>')
    b.append(f'<path d="M{cx - 40},{ly} L{cx - 40},{ly - 50} A40,40 0 0 1 {cx + 40},{ly - 50} L{cx + 40},{ly}" '
             f'fill="none" stroke="url(#lock)" stroke-width="16"/>')
    b.append(f'<rect x="{cx - 78}" y="{ly - 6}" width="156" height="132" rx="16" fill="url(#lock)" '
             f'stroke="#5a3d14" stroke-width="3"/>')
    b.append(f'<circle cx="{cx}" cy="{ly + 46}" r="14" fill="#2a1a0c"/>'
             f'<path d="M{cx - 7},{ly + 50} L{cx + 7},{ly + 50} L{cx + 4},{ly + 92} L{cx - 4},{ly + 92} Z" fill="#2a1a0c"/>')
    # prayers rising from the clouds toward the gate
    for _ in range(170):
        t = rnd.random()
        x = rnd.gauss(cx, 330)
        y = 1000 - t * rnd.uniform(250, 700)
        r = rnd.uniform(1.5, 4.5)
        b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r * 2.6:.1f}" fill="#ffd98a" opacity="0.25" filter="url(#blur3)"/>'
                 f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#fff3cf" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
    # clouds
    for layer, (y0, col, op) in enumerate([(760, "#b98a8a", 0.55), (840, "#6c4466", 0.75), (930, "#2e1a3a", 0.95)]):
        for _ in range(26):
            x = rnd.uniform(-100, W + 100)
            rx, ry = rnd.uniform(140, 320), rnd.uniform(50, 110)
            b.append(f'<ellipse cx="{x:.0f}" cy="{y0 + rnd.uniform(-30, 40):.0f}" rx="{rx:.0f}" ry="{ry:.0f}" '
                     f'fill="{col}" opacity="{op}" filter="url(#blur10)"/>')
        b.append(f'<rect x="0" y="{y0 + 60}" width="{W}" height="{H}" fill="{col}" opacity="{op}" filter="url(#blur40)"/>')
    return svg(defs, "".join(b))




def hills(rnd: random.Random, y: float, amp: float, waves: float, step: int = 30) -> str:
    """Smooth rolling ground from y, filled to the bottom."""
    phase = rnd.uniform(0, 6.3)
    pts = [(0, H)] + [(x, y + amp * math.sin(x / W * waves * 6.28 + phase)) for x in range(0, W + step, step)]
    return "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts + [(W, H)]) + "Z"


def stars(rnd: random.Random, n: int, top: float, bottom: float, colour: str = "#f4f1e6") -> str:
    return "".join(f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(top, bottom):.0f}" '
                   f'r="{rnd.choice([0.7, 0.9, 1.2, 1.6])}" fill="{colour}" opacity="{rnd.uniform(0.25, 0.9):.2f}"/>'
                   for _ in range(n))


def frog() -> str:
    rnd = random.Random(23)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1c1838"/><stop offset="0.3" stop-color="#4a2c58"/>
      <stop offset="0.5" stop-color="#b9586a"/><stop offset="0.62" stop-color="#f09a5a"/>
      <stop offset="0.7" stop-color="#f7c477"/>
    </linearGradient>
    <linearGradient id="pool" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f2a865"/><stop offset="1" stop-color="#7a3a4e"/>
    </linearGradient>
    <radialGradient id="sun" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#fff2c4" stop-opacity="0.9"/><stop offset="0.3" stop-color="#ffd38a" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#ffb070" stop-opacity="0"/>
    </radialGradient>
    <filter id="blur6"><feGaussianBlur stdDeviation="6"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 70, 0, 260)]
    b.append('<circle cx="1330" cy="505" r="300" fill="url(#sun)"/><circle cx="1330" cy="505" r="62" fill="#fff0c4"/>')
    b.append(f'<path d="{ridge(rnd, 455, 40, 60)}" fill="#6a3658"/>')
    b.append(f'<path d="{ridge(rnd, 500, 22, 50)}" fill="#3e2142"/>')
    # the marsh pool, holding the sky
    b.append('<path d="M380,560 C520,540 1350,535 1560,560 C1600,600 1500,640 1200,650 C900,660 500,650 400,620 C330,600 340,575 380,560 Z" fill="url(#pool)"/>')
    b.append('<rect x="1318" y="560" width="24" height="80" fill="#fff0c4" opacity="0.55" filter="url(#blur6)"/>')
    b.append(f'<path d="{ridge(rnd, 600, 10, 40)}" fill="#1a0f1e" '
             'mask="none" transform="translate(0,40)"/>')
    # reeds at the pool's edges
    reeds = []
    for cx in (420, 470, 1500, 1540, 1580):
        for _ in range(9):
            x, h = cx + rnd.uniform(-25, 25), rnd.uniform(40, 95)
            reeds.append(f"M{x:.0f},610 Q{x + rnd.uniform(-12, 12):.0f},{610 - h / 2:.0f} {x + rnd.uniform(-18, 18):.0f},{610 - h:.0f}")
    b.append(f'<path d="{" ".join(reeds)}" stroke="#1a0f1e" stroke-width="3" fill="none" stroke-linecap="round"/>')
    # the rock, and the great frog on it, facing the man
    b.append('<path d="M960,600 C980,560 1060,548 1130,552 C1190,556 1225,575 1235,600 Z" fill="#140a18"/>')
    b.append('<g transform="translate(1100,500) scale(1.25)" fill="#140a18">'
             '<ellipse cx="0" cy="0" rx="92" ry="52" transform="rotate(-12)"/>'
             '<ellipse cx="-78" cy="-24" rx="54" ry="37"/>'
             '<circle cx="-88" cy="-56" r="16"/><circle cx="-58" cy="-60" r="13"/>'
             '<ellipse cx="48" cy="22" rx="56" ry="34" transform="rotate(20 48 22)"/>'
             '<ellipse cx="0" cy="50" rx="56" ry="10"/>'
             '<path d="M-66,6 L-84,48" stroke="#140a18" stroke-width="16" stroke-linecap="round"/>'
             '<ellipse cx="-96" cy="50" rx="20" ry="6"/>'
             '<circle cx="-92" cy="-58" r="4.5" fill="#ffd98a"/>'
             '</g>')
    # the Baal Shem Tov, in his hat and long coat, standing before it
    b.append('<g transform="translate(800,600)" fill="#140a18" stroke="#140a18" stroke-linecap="round">'
             '<ellipse cx="0" cy="-88" rx="15" ry="3.5" stroke="none"/><rect x="-8" y="-100" width="16" height="12" rx="2" stroke="none"/>'
             '<circle cx="0" cy="-80" r="9" stroke="none"/><path d="M-6,-76 L6,-76 L1,-62 Z" stroke="none"/>'
             '<path d="M-11,-66 L11,-66 L18,-12 L-16,-12 Z" stroke="none"/>'
             '<path d="M-6,-13 L-8,0 M6,-13 L8,0" stroke-width="5" fill="none"/>'
             '</g>')
    b.append(f'<path d="{hills(rnd, 660, 12, 1.5)}" fill="#0c0610"/>')
    return svg(defs, "".join(b))


def road() -> str:
    rnd = random.Random(31)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2c3e6b"/><stop offset="0.28" stop-color="#7d86a8"/>
      <stop offset="0.42" stop-color="#e3a986"/><stop offset="0.5" stop-color="#f6d79c"/>
    </linearGradient>
    <radialGradient id="sun" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#fff6d8" stop-opacity="0.95"/><stop offset="0.25" stop-color="#ffe2a8" stop-opacity="0.4"/>
      <stop offset="1" stop-color="#ffd090" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="road" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="#b7a486"/><stop offset="1" stop-color="#e8d3a8"/>
    </linearGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 25, 0, 140)]
    b.append('<circle cx="560" cy="478" r="380" fill="url(#sun)"/><circle cx="560" cy="478" r="56" fill="#fff6d8"/>')
    b.append(f'<path d="{hills(rnd, 482, 14, 2.2)}" fill="#8f7f95"/>')
    b.append(f'<path d="{hills(rnd, 520, 22, 1.6)}" fill="#5f6a6a"/>')
    b.append(f'<path d="{hills(rnd, 575, 26, 1.1)}" fill="#3a4540"/>')
    # the road, from the foreground to the sun
    b.append('<path d="M1500,1080 C1400,860 1300,700 1080,610 C900,545 700,520 600,500 L620,500 '
             'C760,522 960,548 1130,610 C1380,700 1560,860 1700,1080 Z" fill="url(#road)" opacity="0.85"/>')
    # the wagon on the road, the horse toward the sunrise, two men in it
    b.append('<g transform="translate(1150,628) scale(1.3)" fill="#1b1a20" stroke="#1b1a20" stroke-linecap="round">'
             '<rect x="0" y="-46" width="112" height="30" rx="3" stroke="none"/>'
             '<circle cx="22" cy="-10" r="17" fill="none" stroke-width="4"/><circle cx="92" cy="-10" r="17" fill="none" stroke-width="4"/>'
             '<path d="M22,-27 L22,7 M5,-10 L39,-10 M92,-27 L92,7 M75,-10 L109,-10" stroke-width="2" fill="none"/>'
             '<rect x="28" y="-80" width="16" height="36" rx="5" stroke="none"/><circle cx="36" cy="-86" r="8" stroke="none"/>'
             '<ellipse cx="36" cy="-93" rx="12" ry="3" stroke="none"/>'
             '<rect x="64" y="-78" width="16" height="34" rx="5" stroke="none"/><circle cx="72" cy="-84" r="8" stroke="none"/>'
             '<ellipse cx="72" cy="-91" rx="12" ry="3" stroke="none"/>'
             '<path d="M2,-30 L-48,-36" stroke-width="3" fill="none"/>'
             '<ellipse cx="-88" cy="-40" rx="42" ry="17" stroke="none"/>'
             '<path d="M-116,-46 L-134,-76 L-122,-82 L-104,-50 Z" stroke="none"/>'
             '<ellipse cx="-140" cy="-80" rx="15" ry="8" transform="rotate(25 -140 -80)" stroke="none"/>'
             '<path d="M-114,-28 L-118,-2 M-102,-28 L-98,-2 M-74,-28 L-78,-2 M-60,-28 L-54,-2" stroke-width="5" fill="none"/>'
             '<path d="M-47,-44 Q-36,-34 -42,-16" stroke-width="5" fill="none"/>'
             '</g>')
    # birds rising over the fields
    birds = []
    for i in range(46):
        t = rnd.random()
        x = 1250 - t * 650 + rnd.gauss(0, 70)
        y = 470 - t * 330 + rnd.gauss(0, 40)
        w = rnd.uniform(7, 15) * (1.2 - t * 0.5)
        birds.append(f"M{x - w:.1f},{y:.1f} Q{x - w / 2:.1f},{y - w * 0.7:.1f} {x:.1f},{y:.1f} "
                     f"Q{x + w / 2:.1f},{y - w * 0.7:.1f} {x + w:.1f},{y:.1f}")
    b.append(f'<path d="{" ".join(birds)}" stroke="#2a2430" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
    b.append(f'<path d="{hills(rnd, 700, 18, 0.9)}" fill="#1f2622"/>')
    grass = [f"M{x:.0f},{y:.0f} l{rnd.uniform(-6, 6):.0f},-{rnd.uniform(14, 34):.0f}"
             for x, y in ((rnd.uniform(0, W), rnd.uniform(705, 760)) for _ in range(260))]
    b.append(f'<path d="{" ".join(grass)}" stroke="#1f2622" stroke-width="3" stroke-linecap="round"/>')
    return svg(defs, "".join(b))


def candle() -> str:
    rnd = random.Random(43)
    defs = """
    <radialGradient id="room" cx="0.45" cy="0.4" r="0.8">
      <stop offset="0" stop-color="#3a2c22"/><stop offset="0.6" stop-color="#1c1510"/><stop offset="1" stop-color="#0b0807"/>
    </radialGradient>
    <linearGradient id="dawn" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3c5688"/><stop offset="0.55" stop-color="#8fa4c8"/><stop offset="1" stop-color="#f2d9a6"/>
    </linearGradient>
    <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#cfe0ff" stop-opacity="0.55"/><stop offset="0.3" stop-color="#ffd9a0" stop-opacity="0.22"/>
      <stop offset="1" stop-color="#ffb060" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="flame" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="#3f7dff"/><stop offset="0.3" stop-color="#a9c8ff"/>
      <stop offset="0.6" stop-color="#fff6e0"/><stop offset="1" stop-color="#ffd27a"/>
    </linearGradient>
    <linearGradient id="wax" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#c9b48e"/><stop offset="0.45" stop-color="#f3e6c8"/><stop offset="1" stop-color="#a8936e"/>
    </linearGradient>
    <linearGradient id="wisp" x1="0" y1="1" x2="1" y2="0">
      <stop offset="0" stop-color="#bcd2ff" stop-opacity="0.7"/><stop offset="1" stop-color="#bcd2ff" stop-opacity="0"/>
    </linearGradient>
    <filter id="blur4"><feGaussianBlur stdDeviation="4"/></filter>
    <filter id="blur30"><feGaussianBlur stdDeviation="30"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>']
    # the arched window, dawn outside
    wx, wy, ww, wh = 1300, 110, 380, 560
    arch = f"M{wx},{wy + wh} L{wx},{wy + ww / 2} A{ww / 2},{ww / 2} 0 0 1 {wx + ww},{wy + ww / 2} L{wx + ww},{wy + wh} Z"
    b.append(f'<path d="M{wx - 30},{wy + wh + 20} L{wx - 30},{wy + ww / 2} A{ww / 2 + 30},{ww / 2 + 30} 0 0 1 '
             f'{wx + ww + 30},{wy + ww / 2} L{wx + ww + 30},{wy + wh + 20} Z" fill="#2a1f17"/>')
    b.append(f'<path d="{arch}" fill="url(#dawn)"/>')
    b.append("".join(f'<circle cx="{rnd.uniform(wx + 30, wx + ww - 30):.0f}" cy="{rnd.uniform(wy + 40, wy + 260):.0f}" '
                     f'r="{rnd.choice([0.8, 1.1, 1.4])}" fill="#fff" opacity="{rnd.uniform(0.3, 0.8):.2f}"/>' for _ in range(16)))
    b.append(f'<path d="M{wx + ww / 2},{wy} L{wx + ww / 2},{wy + wh} M{wx},{wy + 330} L{wx + ww},{wy + 330}" '
             f'stroke="#2a1f17" stroke-width="14"/>')
    b.append(f'<path d="M{wx},{wy + 200} L{wx - 700},{wy + 900} L{wx + ww - 200},{wy + 900} Z" fill="#9fb6e0" opacity="0.06" filter="url(#blur30)"/>')
    # the big clock on the wall, its pendulum hanging still
    cx, cy = 430, 250
    b.append(f'<rect x="{cx - 80}" y="{cy - 120}" width="160" height="440" rx="14" fill="#3a2716" stroke="#6e5530" stroke-width="4"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="66" fill="#e2d3ae" stroke="#8f7146" stroke-width="5"/>')
    for k in range(12):
        a = k * math.pi / 6
        b.append(f'<line x1="{cx + 54 * math.sin(a):.1f}" y1="{cy - 54 * math.cos(a):.1f}" '
                 f'x2="{cx + 60 * math.sin(a):.1f}" y2="{cy - 60 * math.cos(a):.1f}" stroke="#4a3a24" stroke-width="3"/>')
    b.append(f'<path d="M{cx},{cy} L{cx + 26},{cy - 22} M{cx},{cy} L{cx - 4},{cy - 50}" stroke="#2a1f12" stroke-width="5" stroke-linecap="round"/>')
    b.append(f'<rect x="{cx - 50}" y="{cy + 90}" width="100" height="200" rx="8" fill="#1e140b"/>')
    b.append(f'<line x1="{cx}" y1="{cy + 96}" x2="{cx}" y2="{cy + 240}" stroke="#c9a45c" stroke-width="3"/>'
             f'<circle cx="{cx}" cy="{cy + 250}" r="20" fill="#c9a45c"/>')
    # the table, the book, the candle burned low
    b.append(f'<rect x="0" y="640" width="{W}" height="{H - 640}" fill="#140e0a"/>'
             f'<rect x="0" y="632" width="{W}" height="12" fill="#2c2016"/>')
    b.append('<rect x="560" y="596" width="190" height="38" rx="3" fill="#3b1f16"/><rect x="566" y="600" width="178" height="6" fill="#c9a45c" opacity="0.7"/>')
    fx = 960
    b.append(f'<circle cx="{fx}" cy="380" r="420" fill="url(#halo)"/>')
    b.append(f'<ellipse cx="{fx}" cy="628" rx="90" ry="14" fill="#8f7146"/><rect x="{fx - 16}" y="560" width="32" height="68" fill="#a9874e"/>'
             f'<ellipse cx="{fx}" cy="562" rx="56" ry="11" fill="#c9a45c"/>')
    b.append(f'<rect x="{fx - 30}" y="450" width="60" height="112" rx="4" fill="url(#wax)"/>'
             f'<path d="M{fx - 30},458 q8,22 2,40 q-2,8 4,10 q6,-14 4,-48 Z" fill="#f3e6c8"/>')
    b.append(f'<line x1="{fx}" y1="450" x2="{fx}" y2="436" stroke="#1a120c" stroke-width="3"/>')
    b.append(f'<path d="M{fx},330 C{fx + 26},380 {fx + 22},430 {fx},446 C{fx - 22},430 {fx - 26},380 {fx},330 Z" '
             f'fill="#9cc0ff" opacity="0.6" filter="url(#blur4)"/>')
    b.append(f'<path d="M{fx},344 C{fx + 18},386 {fx + 16},428 {fx},442 C{fx - 16},428 {fx - 18},386 {fx},344 Z" fill="url(#flame)"/>')
    # the blue flame's light rising toward the window
    b.append(f'<path d="M{fx},336 C{fx + 40},250 {fx + 160},260 {fx + 210},170 C{fx + 250},100 {fx + 330},90 {wx + 20},150" '
             f'stroke="url(#wisp)" stroke-width="6" fill="none" filter="url(#blur4)"/>')
    return svg(defs, "".join(b))


def lectern() -> str:
    """The author's introduction: an open book on a lectern by lamplight, a quill in the inkwell."""
    rnd = random.Random(53)
    defs = """
    <radialGradient id="room" cx="0.5" cy="0.42" r="0.75">
      <stop offset="0" stop-color="#4a3626"/><stop offset="0.55" stop-color="#1e1610"/><stop offset="1" stop-color="#0a0806"/>
    </radialGradient>
    <radialGradient id="lamp" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#ffe7b0" stop-opacity="0.7"/><stop offset="0.35" stop-color="#ffc870" stop-opacity="0.2"/>
      <stop offset="1" stop-color="#ffb060" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="page" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#d9c79f"/><stop offset="0.5" stop-color="#f6ead0"/><stop offset="1" stop-color="#d9c79f"/>
    </linearGradient>
    <filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>']
    # shelves of books along the back wall
    for row, y in enumerate((120, 300, 480)):
        b.append(f'<rect x="80" y="{y + 150}" width="1760" height="12" fill="#2a1d12"/>')
        x = 90
        while x < 1830:
            w, h = rnd.uniform(18, 42), rnd.uniform(100, 148)
            if not (640 < x < 1280 and row > 0):
                col = rnd.choice(["#3b2418", "#2c2a3a", "#3a3020", "#24301f", "#43261f"])
                b.append(f'<rect x="{x:.0f}" y="{y + 150 - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{col}" opacity="0.85"/>'
                         f'<rect x="{x:.0f}" y="{y + 150 - h + 14:.0f}" width="{w:.0f}" height="3" fill="#8f7146" opacity="0.5"/>')
            x += w + rnd.uniform(1, 4)
    b.append('<circle cx="960" cy="330" r="520" fill="url(#lamp)"/>')
    # the lectern and the open book
    b.append('<path d="M760,600 L1160,600 L1110,640 L810,640 Z" fill="#2c1e12"/><rect x="935" y="640" width="50" height="440" fill="#221710"/>')
    b.append('<path d="M700,600 L960,560 L960,420 L720,450 Z" fill="url(#page)"/>'
             '<path d="M1220,600 L960,560 L960,420 L1200,450 Z" fill="url(#page)"/>'
             '<path d="M960,420 L960,560" stroke="#a8936e" stroke-width="3"/>')
    for k in range(9):
        y = 468 + k * 13
        b.append(f'<path d="M{744 + k * 2},{y - k * 0.8 + 6} L{940},{y - 22 + k * 0.4}" stroke="#7a6748" stroke-width="2" opacity="0.6"/>'
                 f'<path d="M{980},{y - 22 + k * 0.4} L{1176 - k * 2},{y - k * 0.8 + 6}" stroke="#7a6748" stroke-width="2" opacity="0.6"/>')
    # the inkwell and the quill
    b.append('<ellipse cx="1260" cy="596" rx="34" ry="9" fill="#141010"/><rect x="1236" y="566" width="48" height="30" rx="6" fill="#1a1414"/>'
             '<path d="M1258,570 C1290,470 1330,400 1380,330 C1350,420 1310,490 1266,572 Z" fill="#e8dcc0"/>'
             '<path d="M1258,570 L1380,330" stroke="#8f7f60" stroke-width="2"/>')
    # the oil lamp and its flame
    b.append('<ellipse cx="560" cy="598" rx="70" ry="12" fill="#8f7146"/><path d="M500,596 C510,560 610,560 620,596 Z" fill="#c9a45c"/>'
             '<path d="M612,570 L650,560 L640,576 Z" fill="#c9a45c"/>'
             '<path d="M648,540 C660,556 658,566 648,572 C638,566 636,556 648,540 Z" fill="#fff2c0"/>'
             '<circle cx="648" cy="560" r="40" fill="#ffd890" opacity="0.35" filter="url(#blur3)"/>')
    return svg(defs, "".join(b))


def prut() -> str:
    """The hidden years: the rock like a small house on the mountain across the river Prut, at dawn."""
    rnd = random.Random(61)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1e2a4a"/><stop offset="0.35" stop-color="#5a6a8e"/>
      <stop offset="0.52" stop-color="#d9a07c"/><stop offset="0.6" stop-color="#f3cf94"/>
    </linearGradient>
    <linearGradient id="river" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e9c08c"/><stop offset="1" stop-color="#5a6a8e"/>
    </linearGradient>
    <filter id="blur20"><feGaussianBlur stdDeviation="20"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 40, 0, 200)]
    b.append(f'<path d="{ridge(rnd, 430, 30, 50)}" fill="#7a6a86"/>')
    # the mountain, and on it the rock like a small house
    b.append('<path d="M1000,560 C1150,420 1260,300 1380,250 C1480,300 1600,400 1920,520 L1920,1080 L1000,1080 Z" fill="#3e3a4e"/>')
    b.append('<path d="M1330,262 L1420,262 L1430,300 L1324,300 Z" fill="#1c1a26"/><path d="M1316,268 L1375,226 L1440,268 Z" fill="#1c1a26"/>')
    b.append('<rect x="1366" y="276" width="14" height="22" fill="#f3cf94" opacity="0.8"/>')
    b.append(f'<path d="{hills(rnd, 520, 18, 1.3)}" fill="#4c4a5c"/>')
    # the river Prut, catching the dawn
    b.append('<path d="M0,600 C300,570 700,585 1000,560 C1300,540 1600,575 1920,560 L1920,640 C1600,650 1300,630 1000,650 C700,668 300,640 0,660 Z" fill="url(#river)"/>')
    b.append('<ellipse cx="900" cy="600" rx="700" ry="20" fill="#fff0d0" opacity="0.15" filter="url(#blur20)"/>')
    # the near bank, and the young man walking toward the river with his loaf
    b.append(f'<path d="{hills(rnd, 650, 10, 0.8)}" fill="#14121c"/>')
    b.append('<g transform="translate(620,652)" fill="#14121c" stroke="#14121c" stroke-linecap="round">'
             '<ellipse cx="0" cy="-90" rx="14" ry="3.5" stroke="none"/><rect x="-8" y="-101" width="16" height="11" rx="2" stroke="none"/>'
             '<circle cx="0" cy="-82" r="9" stroke="none"/>'
             '<path d="M-11,-70 L11,-70 L17,-14 L-15,-14 Z" stroke="none"/>'
             '<path d="M-5,-15 L-10,0 M5,-15 L11,0" stroke-width="5" fill="none"/>'
             '<path d="M10,-60 L24,-44" stroke-width="4" fill="none"/><ellipse cx="27" cy="-42" rx="9" ry="6" stroke="none"/>'
             '</g>')
    return svg(defs, "".join(b))


def synagogue() -> str:
    """Rabbi Gershon of Kitov: a wooden synagogue at dusk, the souls coming like a great flock of lights."""
    rnd = random.Random(67)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0d1028"/><stop offset="0.5" stop-color="#2c2850"/><stop offset="0.75" stop-color="#6a4a6a"/>
    </linearGradient>
    <filter id="blur4"><feGaussianBlur stdDeviation="4"/></filter>
    <filter id="blur14"><feGaussianBlur stdDeviation="14"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 140, 0, 420)]
    b.append(f'<path d="{hills(rnd, 600, 14, 1.2)}" fill="#1c1830"/>')
    # the wooden synagogue: a tiered roof over a broad hall
    x0, base = 760, 610
    b.append(f'<rect x="{x0}" y="{base - 170}" width="400" height="170" fill="#120e18"/>')
    for i, (w, h, y) in enumerate([(470, 70, base - 170), (330, 60, base - 240), (200, 50, base - 300)]):
        cx = x0 + 200
        b.append(f'<path d="M{cx - w / 2},{y} L{cx - w / 2 + 40},{y - h} L{cx + w / 2 - 40},{y - h} L{cx + w / 2},{y} Z" fill="#120e18"/>')
        if i < 2:
            b.append(f'<rect x="{cx - w / 2 + 70}" y="{y - h - 10}" width="{w - 140}" height="12" fill="#120e18"/>')
    for k in range(4):
        b.append(f'<path d="M{x0 + 50 + k * 90},{base - 40} L{x0 + 50 + k * 90},{base - 110} '
                 f'A22,22 0 0 1 {x0 + 94 + k * 90},{base - 110} L{x0 + 94 + k * 90},{base - 40} Z" fill="#f5c871" opacity="0.85"/>')
    b.append(f'<ellipse cx="{x0 + 200}" cy="{base - 80}" rx="320" ry="90" fill="#f5c871" opacity="0.12" filter="url(#blur14)"/>')
    # the souls, a great flock of small lights streaming to the windows
    for _ in range(260):
        t = rnd.random()
        side = rnd.choice((-1, 1))
        x = 960 + side * (200 + t * 820) + rnd.gauss(0, 50)
        y = 470 - t * 330 + rnd.gauss(0, 45) + 120 * math.sin(t * 3)
        r = rnd.uniform(1.2, 3.4) * (1.2 - t * 0.6)
        b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r * 3:.1f}" fill="#cfd8ff" opacity="0.18" filter="url(#blur4)"/>'
                 f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#eef1ff" opacity="{rnd.uniform(0.45, 0.9):.2f}"/>')
    b.append(f'<path d="{hills(rnd, 650, 8, 0.7)}" fill="#0c0a14"/>')
    return svg(defs, "".join(b))


def ship() -> str:
    """The Land of Israel and the way there: a sailing ship at dusk off the coast, a walled city on the hills."""
    rnd = random.Random(71)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1b2246"/><stop offset="0.35" stop-color="#5b4a78"/>
      <stop offset="0.5" stop-color="#e08a6a"/><stop offset="0.56" stop-color="#f6c27a"/>
    </linearGradient>
    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#d98a6e"/><stop offset="0.3" stop-color="#5b4a78"/><stop offset="1" stop-color="#151a34"/>
    </linearGradient>
    <radialGradient id="sun" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#fff0c8" stop-opacity="0.9"/><stop offset="0.3" stop-color="#ffd090" stop-opacity="0.3"/>
      <stop offset="1" stop-color="#ffb070" stop-opacity="0"/>
    </radialGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 60, 0, 230)]
    b.append('<circle cx="560" cy="560" r="320" fill="url(#sun)"/><circle cx="560" cy="560" r="58" fill="#fff0c8"/>')
    b.append('<rect x="0" y="560" width="1920" height="520" fill="url(#sea)"/>')
    for _ in range(70):
        x, y = rnd.uniform(200, 900), rnd.uniform(570, 760)
        b.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{rnd.uniform(20, 90):.0f}" height="2" fill="#ffe2b0" opacity="{rnd.uniform(0.15, 0.5):.2f}"/>')
    # the coast: hills, and a walled city with its towers
    b.append('<path d="M1180,560 C1300,500 1420,470 1560,455 C1700,440 1820,460 1920,470 L1920,560 Z" fill="#3a2c4a"/>')
    b.append('<path d="M1440,470 L1440,440 L1460,440 L1460,428 L1480,428 L1480,440 L1560,440 L1560,420 L1580,420 L1580,440 L1660,440 '
             'L1660,430 L1690,430 L1690,445 L1740,445 L1740,470 Z" fill="#261c32"/>')
    # the ship, sails full, heading for the coast
    b.append('<g transform="translate(900,560)" fill="#14101e">'
             '<path d="M-150,0 L150,0 L120,40 L-120,40 Z"/>'
             '<path d="M-150,0 L-170,-14 L-140,-6 Z"/>'
             '<rect x="-6" y="-250" width="8" height="250"/><rect x="-96" y="-190" width="6" height="190"/><rect x="84" y="-170" width="6" height="170"/>'
             '<path d="M-2,-240 C50,-200 50,-110 -2,-60 Z" fill="#e9d9b8"/><path d="M-92,-180 C-50,-150 -50,-80 -92,-40 Z" fill="#e9d9b8"/>'
             '<path d="M88,-160 C126,-130 126,-70 88,-40 Z" fill="#e9d9b8"/>'
             '<path d="M2,-250 L30,-262 L2,-270 Z" fill="#e9d9b8"/>'
             '</g>')
    b.append('<ellipse cx="900" cy="606" rx="190" ry="8" fill="#14101e" opacity="0.5"/>')
    return svg(defs, "".join(b))


def prayer() -> str:
    """In prayer: a man wrapped in his prayer shawl, from behind, before the holy ark, its lamps and the light."""
    rnd = random.Random(79)
    defs = """
    <radialGradient id="hall" cx="0.5" cy="0.35" r="0.8">
      <stop offset="0" stop-color="#5a4430"/><stop offset="0.5" stop-color="#231a12"/><stop offset="1" stop-color="#0a0806"/>
    </radialGradient>
    <linearGradient id="curtain" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#5a1a24"/><stop offset="1" stop-color="#2e0c14"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#fff2c8" stop-opacity="0.6"/><stop offset="0.4" stop-color="#ffd890" stop-opacity="0.15"/>
      <stop offset="1" stop-color="#ffd890" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="tallit" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2a2620"/><stop offset="1" stop-color="#14120e"/>
    </linearGradient>
    <filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#hall)"/>']
    b.append('<circle cx="960" cy="300" r="560" fill="url(#glow)"/>')
    # the ark: a carved frame, the curtain, the tablets above
    b.append('<path d="M760,620 L760,230 Q960,120 1160,230 L1160,620 Z" fill="#6e5530"/>'
             '<path d="M790,620 L790,250 Q960,160 1130,250 L1130,620 Z" fill="url(#curtain)"/>')
    b.append('<path d="M900,300 L900,250 Q920,228 940,250 L940,300 Z" fill="#c9a45c"/><path d="M980,300 L980,250 Q1000,228 1020,250 L1020,300 Z" fill="#c9a45c"/>')
    b.append('<path d="M840,600 L840,340 M1080,600 L1080,340" stroke="#c9a45c" stroke-width="3" opacity="0.6"/>')
    # the lamps hanging on either side
    for x in (640, 1280):
        b.append(f'<line x1="{x}" y1="0" x2="{x}" y2="300" stroke="#8f7146" stroke-width="3"/>'
                 f'<path d="M{x - 26},300 L{x + 26},300 L{x + 12},336 L{x - 12},336 Z" fill="#c9a45c"/>'
                 f'<circle cx="{x}" cy="290" r="30" fill="#ffe0a0" opacity="0.45" filter="url(#blur3)"/>'
                 f'<path d="M{x},270 C{x + 8},282 {x + 7},292 {x},298 C{x - 7},292 {x - 8},282 {x},270 Z" fill="#fff4cc"/>')
    # the man praying, wrapped in the prayer shawl, its stripes and fringes
    b.append('<g transform="translate(960,650) scale(0.85)">'
             '<path d="M-170,0 C-168,-90 -150,-140 -96,-162 C-70,-172 -58,-190 -56,-214 C-54,-262 -30,-286 0,-286 '
             'C30,-286 54,-262 56,-214 C58,-190 70,-172 96,-162 C150,-140 168,-90 170,0 Z" fill="url(#tallit)"/>'
             '<path d="M-58,-206 C-30,-222 30,-222 58,-206 L56,-190 C28,-204 -28,-204 -56,-190 Z" fill="#e6dcc4"/>'
             '<path d="M-166,-56 C-60,-80 60,-80 166,-56" stroke="#e6dcc4" stroke-width="10" fill="none"/>'
             '<path d="M-168,-34 C-60,-58 60,-58 168,-34" stroke="#e6dcc4" stroke-width="5" fill="none"/>'
             '</g>')
    b.append(f'<rect x="0" y="640" width="{W}" height="{H - 640}" fill="#120d09"/>')
    return svg(defs, "".join(b))


def flame(x: float, y: float, h: float = 30) -> str:
    """A small candle flame with its glow, its tip at (x, y)."""
    return (f'<circle cx="{x}" cy="{y + h * 0.6}" r="{h * 1.6}" fill="#ffd890" opacity="0.28" filter="url(#blur3)"/>'
            f'<path d="M{x},{y} C{x + h * 0.32},{y + h * 0.45} {x + h * 0.3},{y + h * 0.8} {x},{y + h} '
            f'C{x - h * 0.3},{y + h * 0.8} {x - h * 0.32},{y + h * 0.45} {x},{y} Z" fill="#fff2c4"/>')


def window(x: float, y: float, w: float, h: float, sky: str, frame: str = "#1e1610") -> str:
    """An arched window onto `sky` (a fill), with its frame and cross bars."""
    arch = f"M{x},{y + h} L{x},{y + w / 2} A{w / 2},{w / 2} 0 0 1 {x + w},{y + w / 2} L{x + w},{y + h} Z"
    return (f'<path d="M{x - 22},{y + h + 16} L{x - 22},{y + w / 2} A{w / 2 + 22},{w / 2 + 22} 0 0 1 {x + w + 22},{y + w / 2} '
            f'L{x + w + 22},{y + h + 16} Z" fill="{frame}"/><path d="{arch}" fill="{sky}"/>'
            f'<path d="M{x + w / 2},{y} L{x + w / 2},{y + h} M{x},{y + h * 0.55} L{x + w},{y + h * 0.55}" stroke="{frame}" stroke-width="12"/>')


ROOM_DEFS = """
    <radialGradient id="room" cx="0.5" cy="0.42" r="0.8">
      <stop offset="0" stop-color="#46321f"/><stop offset="0.55" stop-color="#1d150e"/><stop offset="1" stop-color="#0a0806"/>
    </radialGradient>
    <linearGradient id="night" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0e1430"/><stop offset="1" stop-color="#2c3660"/>
    </linearGradient>
    <radialGradient id="warm" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#ffe0a0" stop-opacity="0.45"/><stop offset="1" stop-color="#ffc070" stop-opacity="0"/>
    </radialGradient>
    <filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>
    <filter id="blur10"><feGaussianBlur stdDeviation="10"/></filter>
    """


def sabbath_table() -> str:
    """His ways and customs: the Sabbath candles lit, the cup of wine and his pipe on the table by the window."""
    rnd = random.Random(83)
    b = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>', window(1240, 120, 360, 480, "url(#night)")]
    b.append("".join(f'<circle cx="{rnd.uniform(1260, 1580):.0f}" cy="{rnd.uniform(140, 420):.0f}" r="{rnd.choice([0.8, 1.2, 1.6])}" '
                     f'fill="#fff" opacity="{rnd.uniform(0.3, 0.9):.2f}"/>' for _ in range(24)))
    b.append('<circle cx="860" cy="430" r="420" fill="url(#warm)"/>')
    b.append(f'<rect x="0" y="600" width="{W}" height="{H - 600}" fill="#1a120b"/><rect x="0" y="592" width="{W}" height="14" fill="#3a2a1a"/>')
    b.append('<path d="M300,600 L1700,600 L1740,640 L260,640 Z" fill="#e8dcc0" opacity="0.9"/>')     # the white cloth
    for x in (700, 860):                                                                                # the two candlesticks
        b.append(f'<ellipse cx="{x}" cy="596" rx="44" ry="10" fill="#c9a45c"/><rect x="{x - 8}" y="470" width="16" height="126" fill="#c9a45c"/>'
                 f'<ellipse cx="{x}" cy="470" rx="26" ry="7" fill="#c9a45c"/><rect x="{x - 11}" y="380" width="22" height="90" fill="#f3ead2"/>'
                 + flame(x, 336, 40))
    b.append('<path d="M1030,596 L1090,596 L1076,560 L1068,520 L1100,470 L1020,470 L1052,520 L1044,560 Z" fill="#c9a45c"/>'   # the cup
             '<ellipse cx="1060" cy="472" rx="40" ry="7" fill="#7a1c24"/>')
    b.append('<path d="M1160,590 L1420,520" stroke="#3b2414" stroke-width="7" stroke-linecap="round"/>'                     # the pipe
             '<path d="M1408,524 C1404,496 1446,488 1452,512 L1446,540 C1436,548 1416,546 1412,534 Z" fill="#4a2c18"/>')
    return svg(ROOM_DEFS, "".join(b))


def letter_rain() -> str:
    """The Rabbi of Polonne: his study by night, the Baal Shem Tov's letter with its seal, rain at the window."""
    rnd = random.Random(89)
    b = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>', window(1220, 110, 380, 500, "url(#night)")]
    rain = " ".join(f"M{x:.0f},{y:.0f} l-6,26" for x, y in ((rnd.uniform(1230, 1590), rnd.uniform(120, 600)) for _ in range(140)))
    b.append(f'<path d="{rain}" stroke="#9fb0d8" stroke-width="2" opacity="0.6"/>')
    b.append('<circle cx="780" cy="440" r="440" fill="url(#warm)"/>')
    b.append(f'<rect x="0" y="600" width="{W}" height="{H - 600}" fill="#1a120b"/><rect x="0" y="592" width="{W}" height="14" fill="#3a2a1a"/>')
    for x, h, c in ((260, 220, "#3b2418"), (300, 260, "#2c2a3a"), (346, 200, "#43261f"), (382, 240, "#24301f")):  # books
        b.append(f'<rect x="{x}" y="{592 - h}" width="{38}" height="{h}" fill="{c}"/><rect x="{x}" y="{592 - h + 18}" width="38" height="4" fill="#8f7146" opacity="0.6"/>')
    b.append('<ellipse cx="560" cy="590" rx="40" ry="9" fill="#c9a45c"/><rect x="552" y="500" width="16" height="90" fill="#c9a45c"/>'
             '<rect x="549" y="430" width="22" height="70" fill="#f3ead2"/>' + flame(560, 388, 40))
    b.append('<path d="M760,590 L1100,560 L1130,598 L790,620 Z" fill="#efe3c6"/>'                         # the letter
             + "".join(f'<path d="M{800 + k * 4},{590 - k * 2 + 10} L{1080},{566 + k * 0.4}" stroke="#7a6748" stroke-width="2" opacity="0.5"/>'
                       for k in range(0)))
    for k in range(5):
        b.append(f'<path d="M{805},{596 - k * 6} L{1090},{570 - k * 5}" stroke="#7a6748" stroke-width="2" opacity="0.45"/>')
    b.append('<circle cx="1000" cy="600" r="18" fill="#8a1c22"/><circle cx="1000" cy="600" r="10" fill="#a8282e"/>')   # the seal
    b.append('<path d="M1150,590 C1190,520 1240,470 1300,420 C1270,480 1220,540 1160,594 Z" fill="#e8dcc0"/>')            # the quill
    return svg(ROOM_DEFS, "".join(b))


def lvov_synagogue() -> str:
    """The Mokhiach of Polonne, part one: the great synagogue of Lvov, the preacher at its door."""
    rnd = random.Random(97)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#20284e"/><stop offset="0.6" stop-color="#7a6a8a"/><stop offset="1" stop-color="#d8a88a"/>
    </linearGradient>
    <linearGradient id="stone" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#8a7a6a"/><stop offset="1" stop-color="#4a3e36"/>
    </linearGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 50, 0, 200)]
    b.append('<path d="M0,620 L0,470 L180,470 L180,420 L260,420 L260,500 L420,500 L420,440 L520,440 L520,620 Z" fill="#3a3040"/>'
             '<path d="M1400,620 L1400,450 L1520,450 L1520,400 L1600,400 L1600,480 L1760,480 L1760,430 L1920,430 L1920,620 Z" fill="#3a3040"/>')
    b.append('<path d="M620,620 L620,300 L700,300 L700,250 L1220,250 L1220,300 L1300,300 L1300,620 Z" fill="url(#stone)"/>')
    for k in range(12):                                                    # the parapet
        b.append(f'<rect x="{700 + k * 44}" y="226" width="26" height="26" fill="#5a4e44"/>')
    for x in (700, 840, 1040, 1180):                                       # tall windows
        b.append(f'<path d="M{x},540 L{x},380 A30,30 0 0 1 {x + 60},380 L{x + 60},540 Z" fill="#f5c871" opacity="0.8"/>')
    b.append('<path d="M920,620 L920,450 A40,40 0 0 1 1000,450 L1000,620 Z" fill="#f5c871" opacity="0.9"/>')  # the open door, lit
    b.append('<g transform="translate(960,620)" fill="#0f0c10">'                                        # the preacher
             '<ellipse cx="0" cy="-92" rx="14" ry="3.5"/><rect x="-8" y="-104" width="16" height="12" rx="2"/>'
             '<circle cx="0" cy="-84" r="9"/><path d="M-12,-72 L12,-72 L19,-6 L-19,-6 Z"/>'
             '<path d="M-6,-8 L-7,0 L-2,0 L-1,-8 Z M2,-8 L3,0 L8,0 L6,-8 Z"/></g>')
    b.append(f'<rect x="0" y="620" width="{W}" height="{H - 620}" fill="#1a1620"/>')
    return svg(defs, "".join(b))


def kitov_house() -> str:
    """The Mokhiach of Polonne, part two: the house in Kitov at night, the jester at the attic window, one candle below."""
    rnd = random.Random(101)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#080a18"/><stop offset="1" stop-color="#22264a"/>
    </linearGradient>
    <radialGradient id="moon" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#e8e2c8" stop-opacity="0.6"/><stop offset="1" stop-color="#9fb0d8" stop-opacity="0"/>
    </radialGradient>
    <filter id="blur6"><feGaussianBlur stdDeviation="6"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 120, 0, 380)]
    b.append('<circle cx="420" cy="200" r="260" fill="url(#moon)"/><circle cx="420" cy="200" r="54" fill="#e8e2c8"/>'
             '<circle cx="440" cy="190" r="50" fill="#141832"/>')
    b.append(f'<path d="{hills(rnd, 610, 10, 1)}" fill="#141228"/>')
    b.append('<path d="M760,620 L760,430 L1160,430 L1160,620 Z" fill="#1a1622"/><path d="M720,436 L960,270 L1200,436 Z" fill="#120f18"/>')
    b.append('<rect x="930" y="330" width="60" height="56" fill="#2a2440"/>')                          # the attic window
    b.append('<path d="M940,384 C930,350 950,330 960,334 C972,330 990,350 980,384 Z" fill="#05040a" filter="url(#blur6)"/>'
             '<circle cx="952" cy="352" r="3" fill="#c94a3a"/><circle cx="968" cy="352" r="3" fill="#c94a3a"/>')
    b.append('<rect x="830" y="500" width="80" height="70" fill="#f5c871" opacity="0.85"/>'             # the lit window
             '<path d="M870,500 L870,570 M830,535 L910,535" stroke="#1a1622" stroke-width="6"/>'
             '<rect x="1020" y="500" width="80" height="70" fill="#0c0a12"/>')
    b.append(f'<rect x="0" y="620" width="{W}" height="{H - 620}" fill="#0c0a14"/>')
    return svg(defs, "".join(b))


def thunder() -> str:
    """The Maggid of Mezritch: a night of thunder and lightning over the small house, one window lit."""
    rnd = random.Random(103)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0c0e1c"/><stop offset="1" stop-color="#2a2e4a"/>
    </linearGradient>
    <filter id="blur8"><feGaussianBlur stdDeviation="8"/></filter>
    <filter id="blur30"><feGaussianBlur stdDeviation="30"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    for _ in range(30):                                                   # storm clouds
        b.append(f'<ellipse cx="{rnd.uniform(-100, W + 100):.0f}" cy="{rnd.uniform(40, 300):.0f}" rx="{rnd.uniform(160, 360):.0f}" '
                 f'ry="{rnd.uniform(50, 110):.0f}" fill="#3a3e5a" opacity="0.55" filter="url(#blur30)"/>')
    bolt = "M1180,60 L1120,230 L1170,230 L1080,420 L1140,410 L1050,560"
    b.append(f'<path d="{bolt}" stroke="#e6ecff" stroke-width="16" fill="none" opacity="0.35" filter="url(#blur8)"/>'
             f'<path d="{bolt}" stroke="#ffffff" stroke-width="4" fill="none"/>')
    b.append('<path d="M700,60 L660,170 L690,170 L640,280" stroke="#e6ecff" stroke-width="3" fill="none" opacity="0.6"/>')
    b.append('<ellipse cx="1120" cy="300" rx="380" ry="260" fill="#c8d2ff" opacity="0.08" filter="url(#blur30)"/>')
    b.append(f'<path d="{hills(rnd, 600, 12, 1.1)}" fill="#14162a"/>')
    b.append('<path d="M780,612 L780,480 L1000,480 L1000,612 Z" fill="#100f1a"/><path d="M750,486 L890,390 L1030,486 Z" fill="#0c0b14"/>'
             '<rect x="830" y="520" width="60" height="50" fill="#f5c871" opacity="0.9"/>'
             '<path d="M860,520 L860,570 M830,545 L890,545" stroke="#100f1a" stroke-width="5"/>')
    b.append(f'<rect x="0" y="618" width="{W}" height="{H - 618}" fill="#0c0d18"/>')
    return svg(defs, "".join(b))


def sukkah() -> str:
    """The Maggid's household and disciples: a sukkah at night, its lamp lit, the stars through its roof of branches."""
    rnd = random.Random(107)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0a0e22"/><stop offset="1" stop-color="#262c52"/>
    </linearGradient>
    <radialGradient id="warm" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#ffe0a0" stop-opacity="0.55"/><stop offset="1" stop-color="#ffc070" stop-opacity="0"/>
    </radialGradient>
    <filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 160, 0, 420)]
    b.append(f'<path d="{hills(rnd, 610, 8, 1.2)}" fill="#141830"/>')
    b.append('<circle cx="960" cy="470" r="330" fill="url(#warm)"/>')
    b.append('<path d="M640,620 L640,300 L1280,300 L1280,620 Z" fill="#3a2a1c" opacity="0.35"/>')     # the booth's light
    for x in (640, 1280):
        b.append(f'<rect x="{x - 10}" y="290" width="20" height="330" fill="#2a1d12"/>')
    b.append('<rect x="630" y="290" width="660" height="16" fill="#2a1d12"/>')
    for k in range(40):                                                   # the roof of branches
        x = 630 + k * 17 + rnd.uniform(-6, 6)
        b.append(f'<path d="M{x:.0f},{292 + rnd.uniform(-6, 4):.0f} q{rnd.uniform(-30, 30):.0f},-{rnd.uniform(20, 50):.0f} '
                 f'{rnd.uniform(-50, 50):.0f},-{rnd.uniform(30, 70):.0f}" stroke="#1c2a18" stroke-width="{rnd.uniform(4, 8):.1f}" fill="none"/>')
    b.append('<path d="M650,330 C760,350 860,340 960,330 C1060,340 1160,350 1270,330 L1270,620 L650,620 Z" fill="#c9b48e" opacity="0.18"/>')  # the cloth walls
    b.append('<line x1="960" y1="306" x2="960" y2="400" stroke="#8f7146" stroke-width="3"/>'
             '<path d="M936,400 L984,400 L972,436 L948,436 Z" fill="#c9a45c"/>' + flame(960, 376, 28))
    b.append('<rect x="760" y="520" width="400" height="16" fill="#2a1d12"/><rect x="780" y="536" width="12" height="84" fill="#2a1d12"/>'
             '<rect x="1128" y="536" width="12" height="84" fill="#2a1d12"/>')
    b.append(f'<rect x="0" y="620" width="{W}" height="{H - 620}" fill="#0e1020"/>')
    return svg(defs, "".join(b))


def wagon(x: float, y: float, scale: float = 1.0, fill: str = "#14101a", people: int = 2) -> str:
    """A horse and wagon, the horse facing left, its wheels on y."""
    heads = "".join(f'<rect x="{28 + 36 * k}" y="-80" width="16" height="36" rx="5" stroke="none"/><circle cx="{36 + 36 * k}" cy="-86" r="8" stroke="none"/>'
                    f'<ellipse cx="{36 + 36 * k}" cy="-93" rx="12" ry="3" stroke="none"/>' for k in range(people))
    return (f'<g transform="translate({x},{y}) scale({scale})" fill="{fill}" stroke="{fill}" stroke-linecap="round">'
            '<rect x="0" y="-46" width="112" height="30" rx="3" stroke="none"/>'
            '<circle cx="22" cy="-10" r="17" fill="none" stroke-width="4"/><circle cx="92" cy="-10" r="17" fill="none" stroke-width="4"/>'
            '<path d="M22,-27 L22,7 M5,-10 L39,-10 M92,-27 L92,7 M75,-10 L109,-10" stroke-width="2" fill="none"/>' + heads +
            '<path d="M2,-30 L-48,-36" stroke-width="3" fill="none"/><ellipse cx="-88" cy="-40" rx="42" ry="17" stroke="none"/>'
            '<path d="M-116,-46 L-134,-76 L-122,-82 L-104,-50 Z" stroke="none"/>'
            '<ellipse cx="-140" cy="-80" rx="15" ry="8" transform="rotate(25 -140 -80)" stroke="none"/>'
            '<path d="M-114,-28 L-118,-2 M-102,-28 L-98,-2 M-74,-28 L-78,-2 M-60,-28 L-54,-2" stroke-width="5" fill="none"/>'
            '<path d="M-47,-44 Q-36,-34 -42,-16" stroke-width="5" fill="none"/></g>')


def lake_study_house() -> str:
    """Rabbi Nachman of Horodenka: the study house built on the water at dawn, the bathhouse beside it."""
    rnd = random.Random(109)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2a3a64"/><stop offset="0.5" stop-color="#a88aa0"/><stop offset="0.58" stop-color="#f2cf9a"/>
    </linearGradient>
    <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e6c49a"/><stop offset="1" stop-color="#2a3a64"/>
    </linearGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 30, 0, 160)]
    b.append(f'<path d="{ridge(rnd, 470, 18, 60)}" fill="#6a5a7a"/>')
    b.append('<rect x="0" y="520" width="1920" height="560" fill="url(#water)"/>')
    for _ in range(60):
        x, y = rnd.uniform(0, W), rnd.uniform(530, 640)
        b.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{rnd.uniform(30, 120):.0f}" height="2" fill="#fff0d0" opacity="{rnd.uniform(0.15, 0.45):.2f}"/>')
    # the study house on its piles over the water, the bathhouse beside it
    house = ('<rect x="760" y="380" width="300" height="120" fill="#1e1a2a"/><path d="M730,386 L910,300 L1090,386 Z" fill="#181424"/>'
             '<rect x="800" y="420" width="50" height="50" fill="#f5c871"/><rect x="960" y="420" width="50" height="50" fill="#f5c871" opacity="0.4"/>'
             '<rect x="1100" y="430" width="140" height="70" fill="#1e1a2a"/><path d="M1086,434 L1170,392 L1254,434 Z" fill="#181424"/>'
             '<path d="M1190,392 L1190,360" stroke="#181424" stroke-width="12"/>')
    piles = "".join(f'<rect x="{x}" y="500" width="10" height="22" fill="#181424"/>' for x in range(770, 1240, 46))
    b.append(house + piles)
    b.append(f'<g transform="translate(0,1022) scale(1,-1)" opacity="0.25">{house}</g>')
    b.append('<path d="M1240,500 L1700,500 L1760,520 L1240,520 Z" fill="#181424"/>')
    b.append(f'<rect x="0" y="640" width="{W}" height="{H - 640}" fill="#141a30" opacity="0.6"/>')
    return svg(defs, "".join(b))


def tefillin() -> str:
    """Rabbi Yitzchak of Drohobych: tefillin and their open bag on the table, a thaler beside them, lamplight."""
    b = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>', '<circle cx="960" cy="420" r="460" fill="url(#warm)"/>']
    b.append(f'<rect x="0" y="600" width="{W}" height="{H - 600}" fill="#1a120b"/><rect x="0" y="592" width="{W}" height="14" fill="#3a2a1a"/>')
    b.append('<path d="M560,592 C560,520 600,470 690,462 C780,470 820,520 820,592 Z" fill="#4a1a24"/>'      # the velvet bag
             '<path d="M600,500 C640,480 740,480 780,500" stroke="#c9a45c" stroke-width="4" fill="none"/>')
    # the head tefillin: a black box on its base, the strap looping on the table
    b.append('<rect x="900" y="470" width="110" height="110" fill="#0c0b0b"/><rect x="886" y="574" width="138" height="18" fill="#0c0b0b"/>'
             '<path d="M906,480 L1004,480 M906,525 L1004,525" stroke="#2a2828" stroke-width="2"/>'
             '<path d="M1024,584 C1120,600 1180,560 1150,520 C1120,480 1060,500 1090,540 C1120,580 1240,590 1300,572" '
             'stroke="#0c0b0b" stroke-width="9" fill="none"/>')
    # the hand tefillin
    b.append('<rect x="1150" y="500" width="80" height="72" fill="#0c0b0b"/><rect x="1140" y="568" width="100" height="16" fill="#0c0b0b"/>'
             '<path d="M1240,580 C1320,560 1380,600 1440,586" stroke="#0c0b0b" stroke-width="8" fill="none"/>')
    b.append('<ellipse cx="1500" cy="586" rx="38" ry="10" fill="#d6d0c4"/><ellipse cx="1500" cy="582" rx="38" ry="10" fill="#c8c0b0"/>')  # the thaler
    b.append('<ellipse cx="420" cy="590" rx="60" ry="11" fill="#8f7146"/><path d="M370,588 C380,556 460,556 470,588 Z" fill="#c9a45c"/>'
             + flame(452, 520, 34))
    return svg(ROOM_DEFS, "".join(b))


def nemirov_psalms() -> str:
    """Tzaddikim of his generation, part one: the psalms rising over Nemirov by night, the Tatars' fires far off."""
    rnd = random.Random(113)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0a0c20"/><stop offset="1" stop-color="#2c2a4e"/>
    </linearGradient>
    <filter id="blur4"><feGaussianBlur stdDeviation="4"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 140, 0, 400)]
    b.append(f'<path d="{hills(rnd, 560, 6, 0.6)}" fill="#1c1a30"/>')
    for _ in range(14):                                                    # the Tatars' fires on the far plain
        x = rnd.uniform(1350, 1880)
        b.append(f'<circle cx="{x:.0f}" cy="{rnd.uniform(552, 566):.0f}" r="{rnd.uniform(2, 4):.1f}" fill="#ff8a40" opacity="0.9"/>'
                 f'<circle cx="{x:.0f}" cy="560" r="12" fill="#ff8a40" opacity="0.18" filter="url(#blur4)"/>')
    # the town: roofs, the synagogue, lit windows
    town = []
    x = 260
    while x < 1240:
        w, h = rnd.uniform(60, 120), rnd.uniform(50, 110)
        town.append(f'<rect x="{x:.0f}" y="{600 - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="#100e1c"/>'
                    f'<path d="M{x - 8:.0f},{600 - h + 2:.0f} L{x + w / 2:.0f},{600 - h - 34:.0f} L{x + w + 8:.0f},{600 - h + 2:.0f} Z" fill="#0c0a16"/>')
        if rnd.random() < 0.6:
            town.append(f'<rect x="{x + w / 2 - 9:.0f}" y="{600 - h * 0.6:.0f}" width="18" height="18" fill="#f5c871" opacity="0.85"/>')
        x += w + rnd.uniform(4, 16)
    b.append("".join(town))
    b.append('<rect x="660" y="430" width="200" height="170" fill="#100e1c"/><path d="M640,434 L760,370 L880,434 Z" fill="#0c0a16"/>'
             + "".join(f'<path d="M{690 + k * 50},560 L{690 + k * 50},480 A14,14 0 0 1 {718 + k * 50},480 L{718 + k * 50},560 Z" fill="#f5c871"/>' for k in range(3)))
    # the psalms rising from the synagogue, small lights going up
    for _ in range(120):
        t = rnd.random()
        x = 760 + rnd.gauss(0, 60 + t * 260)
        y = 420 - t * 380
        b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(1.2, 3):.1f}" fill="#ffe7b0" opacity="{0.9 - t * 0.6:.2f}"/>')
    b.append(f'<rect x="0" y="600" width="{W}" height="{H - 600}" fill="#0c0b16"/>')
    return svg(defs, "".join(b))


def friday_road() -> str:
    """Tzaddikim of his generation, part two: the wagon stopped on a dark road on Friday night, far candles in a window."""
    rnd = random.Random(127)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0a0c1e"/><stop offset="0.7" stop-color="#2c3058"/><stop offset="1" stop-color="#4a4a72"/>
    </linearGradient>
    <filter id="blur4"><feGaussianBlur stdDeviation="4"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 220, 0, 460)]
    b.append(f'<path d="{hills(rnd, 540, 16, 1.4)}" fill="#2a2c46"/>')
    b.append('<rect x="1400" y="470" width="150" height="80" fill="#0a0a14"/><path d="M1384,474 L1475,420 L1566,474 Z" fill="#0a0a14"/>'
             '<rect x="1440" y="492" width="34" height="30" fill="#f5c871"/><rect x="1490" y="492" width="34" height="30" fill="#f5c871"/>'
             '<circle cx="1482" cy="507" r="44" fill="#f5c871" opacity="0.25" filter="url(#blur4)"/>')
    b.append('<path d="M300,1080 C500,820 900,640 1440,556 L1480,556 C960,650 640,830 520,1080 Z" fill="#5a5a7a" opacity="0.7"/>')
    b.append(wagon(760, 612, 1.25, "#060610", people=2))
    b.append('<path d="M640,612 C600,600 590,596 560,598" stroke="#060610" stroke-width="3"/>')
    return svg(defs, "".join(b))


def forest_clearing() -> str:
    """Opponents and testers: the two wagons facing each other in the forest, the Zohar open between them, the robbers fleeing."""
    rnd = random.Random(131)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1a2440"/><stop offset="1" stop-color="#5a6a7a"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#ffe7b0" stop-opacity="0.6"/><stop offset="1" stop-color="#ffd890" stop-opacity="0"/>
    </radialGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    for base, (lo, hi), col, n in [(520, (120, 220), "#2a3444", 60), (600, (220, 380), "#141a26", 34)]:
        trees = [pine(rnd.choice([rnd.uniform(-40, 640), rnd.uniform(1280, W + 40)]), base + rnd.uniform(-10, 10), rnd.uniform(lo, hi), rnd)
                 for _ in range(n)]
        b.append(f'<path d="{" ".join(trees)}" fill="{col}"/>')
    b.append(f'<path d="{hills(rnd, 600, 6, 0.8)}" fill="#1c2230"/>')
    b.append('<circle cx="960" cy="540" r="240" fill="url(#glow)"/>')
    b.append(wagon(800, 604, 1.0, "#0c0e16", people=1))
    b.append('<g transform="translate(1120,604) scale(-1,1)">' + wagon(0, 0, 1.0, "#0c0e16", people=1) + '</g>')
    b.append('<path d="M930,560 L960,552 L990,560 L990,570 L960,562 L930,570 Z" fill="#f3ead2"/>')       # the open Zohar
    for x in (420, 470, 1500, 1560):                                                                   # the robbers fleeing
        b.append(f'<g transform="translate({x},600) scale({0.9 if x < 960 else -0.9},0.9)" fill="#0a0c12">'
                 '<circle cx="0" cy="-70" r="8"/><path d="M-8,-62 L10,-60 L14,-30 L-6,-30 Z"/>'
                 '<path d="M-4,-30 L-18,0 M6,-30 L16,-2 M10,-56 L28,-44" stroke="#0a0c12" stroke-width="5" stroke-linecap="round"/></g>')
    b.append(f'<rect x="0" y="604" width="{W}" height="{H - 604}" fill="#0e121c"/>')
    return svg(defs, "".join(b))


def dream_palace() -> str:
    """Opponents who drew close, part one: the splendid palace of the dream, its windows lit, a man looking in."""
    rnd = random.Random(137)
    defs = """
    <radialGradient id="sky" cx="0.5" cy="0.4" r="0.8">
      <stop offset="0" stop-color="#4a3a6a"/><stop offset="0.6" stop-color="#1a1834"/><stop offset="1" stop-color="#08081a"/>
    </radialGradient>
    <linearGradient id="marble" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e8dcc0"/><stop offset="1" stop-color="#9a8a70"/>
    </linearGradient>
    <filter id="blur20"><feGaussianBlur stdDeviation="20"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 160, 0, 500)]
    b.append('<ellipse cx="960" cy="420" rx="620" ry="260" fill="#f5c871" opacity="0.12" filter="url(#blur20)"/>')
    b.append('<rect x="520" y="300" width="880" height="300" fill="url(#marble)"/>'
             '<path d="M480,306 L960,170 L1440,306 Z" fill="#d6c8a8"/><rect x="480" y="300" width="960" height="16" fill="#b8a88a"/>')
    for k in range(9):                                                     # columns and lit arched windows
        x = 560 + k * 100
        b.append(f'<rect x="{x - 8}" y="330" width="16" height="270" fill="#c8b898"/>')
        if k < 8:
            b.append(f'<path d="M{x + 22},560 L{x + 22},400 A28,28 0 0 1 {x + 78},400 L{x + 78},560 Z" fill="#ffd37a"/>')
    b.append('<rect x="500" y="596" width="920" height="10" fill="#b8a88a"/>')
    b.append('<g transform="translate(1530,606)" fill="#08081a">'                                      # the teacher, looking in
             '<circle cx="0" cy="-84" r="9"/><ellipse cx="0" cy="-92" rx="14" ry="3.5"/><rect x="-8" y="-104" width="16" height="12" rx="2"/>'
             '<path d="M-12,-72 L12,-72 L18,-8 L-18,-8 Z"/><path d="M-6,-8 L-8,0 L-2,0 L0,-8 Z M2,-8 L4,0 L9,0 L7,-8 Z"/></g>')
    b.append(f'<rect x="0" y="606" width="{W}" height="{H - 606}" fill="#0a0a18"/>')
    return svg(defs, "".join(b))


def moonlit_gemara() -> str:
    """Opponents who drew close, part two: the Gemara open in the moonlight at a window, the night outside."""
    rnd = random.Random(139)
    defs = """
    <radialGradient id="room" cx="0.6" cy="0.4" r="0.8">
      <stop offset="0" stop-color="#2a3048"/><stop offset="0.6" stop-color="#121420"/><stop offset="1" stop-color="#06070c"/>
    </radialGradient>
    <linearGradient id="night" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0e1430"/><stop offset="1" stop-color="#3a4a78"/>
    </linearGradient>
    <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#cfdcff" stop-opacity="0.22"/><stop offset="1" stop-color="#cfdcff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="page" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#b8c0d0"/><stop offset="0.5" stop-color="#e8ecf4"/><stop offset="1" stop-color="#b8c0d0"/>
    </linearGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>', window(1080, 110, 400, 480, "url(#night)", "#141624")]
    b.append('<circle cx="1180" cy="230" r="46" fill="#eef0f8"/>')
    b.append("".join(f'<circle cx="{rnd.uniform(1100, 1460):.0f}" cy="{rnd.uniform(130, 420):.0f}" r="{rnd.choice([0.8, 1.2])}" fill="#fff" opacity="0.7"/>' for _ in range(20)))
    b.append('<path d="M1080,590 L1480,590 L1180,600 L520,640 Z" fill="url(#beam)"/>')
    b.append(f'<rect x="0" y="600" width="{W}" height="{H - 600}" fill="#0c0d16"/><rect x="0" y="592" width="{W}" height="12" fill="#1c1e2c"/>')
    b.append('<path d="M640,598 L900,560 L900,450 L660,476 Z" fill="url(#page)"/><path d="M1160,598 L900,560 L900,450 L1140,476 Z" fill="url(#page)"/>')
    b.append('<rect x="860" y="490" width="80" height="56" fill="none" stroke="#5a6070" stroke-width="2"/>')       # the Gemara's page
    for k in range(7):
        b.append(f'<path d="M{690 + k * 2},{500 + k * 12} L{850},{482 + k * 11}" stroke="#5a6070" stroke-width="2" opacity="0.6"/>'
                 f'<path d="M{950},{482 + k * 11} L{1110 - k * 2},{500 + k * 12}" stroke="#5a6070" stroke-width="2" opacity="0.6"/>')
    return svg(defs, "".join(b))


def man(x: float, y: float, scale: float = 1.0, fill: str = "#0c0a12") -> str:
    """A standing man in hat and long coat, his feet at (x, y)."""
    return (f'<g transform="translate({x},{y}) scale({scale})" fill="{fill}">'
            '<ellipse cx="0" cy="-90" rx="14" ry="3.5"/><rect x="-8" y="-102" width="16" height="12" rx="2"/>'
            '<circle cx="0" cy="-82" r="9"/><path d="M-6,-78 L6,-78 L1,-64 Z"/>'
            '<path d="M-12,-68 L12,-68 L18,-10 L-18,-10 Z"/><path d="M-6,-11 L-8,0 L-2,0 L0,-11 Z M2,-11 L4,0 L9,0 L7,-11 Z"/></g>')


def hilltop_view() -> str:
    """Seeing from afar: a man on a hilltop at dusk over a wide plain, a covered wagon far below, a town on the horizon."""
    rnd = random.Random(149)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#22284a"/><stop offset="0.5" stop-color="#8a6a7e"/><stop offset="0.62" stop-color="#e8a878"/>
    </linearGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 40, 0, 220)]
    b.append('<path d="M1300,520 L1300,500 L1330,500 L1330,488 L1350,488 L1350,500 L1420,500 L1420,478 L1436,478 L1436,500 L1500,500 L1500,520 Z" fill="#4a3a52"/>')
    b.append(f'<path d="{hills(rnd, 520, 8, 0.7)}" fill="#5a4a62"/>')
    b.append('<path d="M1360,522 C1200,540 900,560 700,620 L760,620 C960,566 1220,544 1380,522 Z" fill="#b89a8a" opacity="0.6"/>')
    b.append('<g transform="translate(1000,566) scale(0.45)" fill="#2a2234"><path d="M0,-40 C0,-90 140,-90 140,-40 Z"/>'
             '<rect x="0" y="-40" width="140" height="26"/><circle cx="26" cy="-8" r="16"/><circle cx="114" cy="-8" r="16"/>'
             '<ellipse cx="-50" cy="-34" rx="38" ry="15"/><path d="M-76,-40 L-92,-66 L-80,-72 L-64,-44 Z"/></g>')
    b.append('<path d="M0,1080 L0,470 C140,440 300,450 420,500 C520,540 600,580 640,620 L640,1080 Z" fill="#1a1422"/>')
    b.append(man(300, 452, 1.1, "#0c0a12"))
    b.append(f'<rect x="0" y="620" width="{W}" height="{H - 620}" fill="#120e18"/>')
    return svg(defs, "".join(b))


def snowy_road() -> str:
    """Wonders on the road: a wagon on a snowy road under the moon, a long pipe stem trailing smoke from it."""
    rnd = random.Random(151)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0e1430"/><stop offset="1" stop-color="#3a4a72"/>
    </linearGradient>
    <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#e8eeff" stop-opacity="0.5"/><stop offset="1" stop-color="#9fb0d8" stop-opacity="0"/>
    </radialGradient>
    <filter id="blur6"><feGaussianBlur stdDeviation="6"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 100, 0, 360)]
    b.append('<circle cx="1480" cy="200" r="260" fill="url(#halo)"/><circle cx="1480" cy="200" r="56" fill="#eef2ff"/>')
    b.append(f'<path d="{hills(rnd, 520, 14, 1.2)}" fill="#8a96b8"/>')
    trees = [pine(x, 530, rnd.uniform(80, 150), rnd) for x in (rnd.uniform(0, 600) for _ in range(18))]
    b.append(f'<path d="{" ".join(trees)}" fill="#1e2440"/>')
    b.append(f'<path d="{hills(rnd, 600, 8, 0.8)}" fill="#c8d0e4"/>')
    b.append(wagon(900, 610, 1.3, "#141a2c", people=1))
    b.append('<path d="M1000,546 L1140,520" stroke="#141a2c" stroke-width="6" stroke-linecap="round"/>'
             '<path d="M1132,524 C1128,504 1158,500 1160,516 L1156,532 C1148,538 1136,536 1134,528 Z" fill="#141a2c"/>'
             '<path d="M1150,500 C1170,470 1140,450 1166,420 C1190,392 1170,370 1196,344" stroke="#e8eeff" stroke-width="6" fill="none" opacity="0.5" filter="url(#blur6)"/>')
    b.append(f'<rect x="0" y="620" width="{W}" height="{H - 620}" fill="#1a2036"/>')
    return svg(defs, "".join(b))


def castle() -> str:
    """Leaseholders and noblemen, part one: the nobleman's castle on a hill above the village, its tower lit, a river below."""
    rnd = random.Random(157)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1a1e3a"/><stop offset="0.6" stop-color="#5a5070"/><stop offset="1" stop-color="#b8887a"/>
    </linearGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 60, 0, 260)]
    b.append('<path d="M700,620 C820,440 1100,420 1240,620 Z" fill="#2a2234"/>')
    b.append('<rect x="860" y="330" width="260" height="150" fill="#1a1422"/>'
             + "".join(f'<rect x="{860 + k * 40}" y="314" width="22" height="18" fill="#1a1422"/>' for k in range(7))
             + '<rect x="900" y="220" width="70" height="120" fill="#1a1422"/>'
             + "".join(f'<rect x="{900 + k * 26}" y="206" width="16" height="16" fill="#1a1422"/>' for k in range(3))
             + '<rect x="922" y="250" width="22" height="30" fill="#f5c871"/>'
             + '<rect x="1040" y="380" width="22" height="30" fill="#f5c871" opacity="0.6"/>')
    village = "".join(f'<rect x="{x}" y="560" width="70" height="44" fill="#1a1422"/><path d="M{x - 8},562 L{x + 35},536 L{x + 78},562 Z" fill="#14101a"/>'
                      f'<rect x="{x + 26}" y="576" width="16" height="14" fill="#f5c871" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>'
                      for x in (300, 420, 1340, 1460, 1580))
    b.append(village)
    b.append('<path d="M0,606 C500,590 1400,600 1920,590 L1920,622 C1400,630 500,622 0,630 Z" fill="#8a7a9a" opacity="0.7"/>')
    b.append(f'<rect x="0" y="626" width="{W}" height="{H - 626}" fill="#100c16"/>')
    return svg(defs, "".join(b))


def gateway() -> str:
    """Leaseholders and noblemen, part two: the covered wagon under the low gateway, the lintel lifted above its hood."""
    rnd = random.Random(163)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#141a34"/><stop offset="1" stop-color="#4a4a6a"/>
    </linearGradient>
    <radialGradient id="warm" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#ffe0a0" stop-opacity="0.5"/><stop offset="1" stop-color="#ffc070" stop-opacity="0"/>
    </radialGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 80, 0, 300)]
    b.append('<rect x="560" y="330" width="800" height="290" fill="#1e1a26"/><path d="M520,336 L960,200 L1400,336 Z" fill="#16121e"/>')
    b.append('<circle cx="960" cy="470" r="230" fill="url(#warm)"/>')
    b.append('<rect x="780" y="420" width="360" height="200" fill="#3a2e2a"/>')                      # the gateway's opening
    b.append('<rect x="760" y="392" width="400" height="22" fill="#2a1e14"/>'                        # the lintel, lifted
             '<path d="M760,414 L780,414 L780,430 M1140,414 L1160,414" stroke="#2a1e14" stroke-width="4" fill="none"/>')
    b.append('<g transform="translate(900,616)" fill="#100c14"><path d="M-10,-50 C-10,-150 230,-150 230,-50 Z" fill="#cfc4b0"/>'
             '<rect x="-10" y="-50" width="240" height="34"/><circle cx="30" cy="-10" r="20"/><circle cx="190" cy="-10" r="20"/></g>')
    b.append('<rect x="1240" y="500" width="10" height="120" fill="#2a1e14"/><path d="M1226,500 L1264,500 L1256,530 L1234,530 Z" fill="#c9a45c"/>'
             '<circle cx="1245" cy="514" r="26" fill="#ffd890" opacity="0.4"/>')
    b.append(f'<rect x="0" y="620" width="{W}" height="{H - 620}" fill="#0e0c14"/>')
    return svg(defs, "".join(b))


def purse() -> str:
    """Charity and money: an empty purse and the last gold coin on the table by a candle, the door open to the night."""
    b = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>']
    b.append('<path d="M1260,120 L1520,120 L1520,600 L1260,600 Z" fill="url(#night)"/><path d="M1240,110 L1260,110 L1260,600 L1240,600 Z M1520,110 L1540,110 L1540,600 L1520,600 Z M1240,100 L1540,100 L1540,120 L1240,120 Z" fill="#1e1610"/>'
             '<path d="M1520,120 L1620,150 L1620,580 L1520,600 Z" fill="#2a1d12"/>')
    b.append('<circle cx="800" cy="440" r="440" fill="url(#warm)"/>')
    b.append(f'<rect x="0" y="600" width="{W}" height="{H - 600}" fill="#1a120b"/><rect x="0" y="592" width="{W}" height="14" fill="#3a2a1a"/>')
    b.append('<ellipse cx="600" cy="590" rx="40" ry="9" fill="#c9a45c"/><rect x="592" y="500" width="16" height="90" fill="#c9a45c"/>'
             '<rect x="589" y="430" width="22" height="70" fill="#f3ead2"/>' + flame(600, 388, 40))
    b.append('<path d="M820,592 C800,560 830,520 880,520 C940,520 960,560 940,592 Z" fill="#5a3a22"/>'        # the empty purse, slack
             '<path d="M850,522 C860,500 900,500 910,522" stroke="#3a2414" stroke-width="5" fill="none"/>')
    b.append('<ellipse cx="1030" cy="588" rx="30" ry="8" fill="#e8c060"/><ellipse cx="1030" cy="584" rx="30" ry="8" fill="#f5d878"/>')
    return svg(ROOM_DEFS, "".join(b))


def stockings_line() -> str:
    """Simple Jews and hidden tzaddikim: the craftsman's small house at dawn, wool stockings drying on a line, the synagogue beyond."""
    rnd = random.Random(167)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2c3c66"/><stop offset="0.55" stop-color="#c8a090"/><stop offset="0.65" stop-color="#f2d09a"/>
    </linearGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 20, 0, 140)]
    b.append(f'<path d="{hills(rnd, 540, 8, 0.8)}" fill="#6a5a72"/>')
    b.append('<rect x="1300" y="420" width="220" height="140" fill="#3a2e44"/><path d="M1284,424 L1410,360 L1536,424 Z" fill="#30263a"/>'
             '<path d="M1380,370 L1380,330 L1440,330 L1440,372" fill="#30263a"/>'
             + "".join(f'<path d="M{1330 + k * 60},540 L{1330 + k * 60},470 A14,14 0 0 1 {1358 + k * 60},470 L{1358 + k * 60},540 Z" fill="#f5c871" opacity="0.7"/>' for k in range(3)))
    b.append('<rect x="420" y="440" width="260" height="170" fill="#241c2c"/><path d="M400,446 L550,370 L700,446 Z" fill="#1c1624"/>'
             '<rect x="470" y="500" width="54" height="50" fill="#f5c871"/><path d="M497,500 L497,550 M470,525 L524,525" stroke="#241c2c" stroke-width="5"/>')
    b.append('<path d="M700,470 L700,610 M1120,470 L1120,610" stroke="#241c2c" stroke-width="8"/><path d="M700,480 Q910,520 1120,480" stroke="#241c2c" stroke-width="3" fill="none"/>')
    for k in range(9):                                                         # the stockings on the line
        x = 740 + k * 42
        y = 480 + 40 * math.sin(math.pi * (x - 700) / 420) * 0.9
        col = rnd.choice(["#8a6a5a", "#5a5a7a", "#7a7060", "#6a4a4a"])
        b.append(f'<path d="M{x},{y:.0f} L{x + 16},{y:.0f} L{x + 16},{y + 54:.0f} L{x + 30},{y + 64:.0f} L{x + 30},{y + 74:.0f} L{x + 2},{y + 74:.0f} L{x},{y + 60:.0f} Z" fill="{col}"/>')
    b.append(f'<rect x="0" y="610" width="{W}" height="{H - 610}" fill="#16121c"/>')
    return svg(defs, "".join(b))


def knife() -> str:
    """Fit and unfit: the shochet's long knife on its cloth by the whetstone, a turnip set aside at the end of the table."""
    b = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>', '<circle cx="960" cy="380" r="520" fill="url(#warm)"/>']
    b.append('<path d="M180,620 L420,380 L1500,380 L1740,620 Z" fill="#4a3220"/>'                        # the tabletop, from above
             '<path d="M180,620 L1740,620 L1740,640 L180,640 Z" fill="#2a1d12"/>')
    b.append('<path d="M560,470 L1300,470 L1340,560 L520,560 Z" fill="#efe6d0"/>')                       # the white cloth
    b.append('<path d="M720,500 L1200,488 C1222,488 1230,500 1214,510 L720,522 Z" fill="#dfe3ea"/>'       # the long blade
             '<path d="M720,500 L1200,488" stroke="#ffffff" stroke-width="3"/>'
             '<rect x="590" y="496" width="136" height="28" rx="8" fill="#3b2414"/>')                     # its handle
    b.append('<path d="M1380,440 L1560,440 L1580,480 L1400,480 Z" fill="#7a7a82"/><path d="M1380,440 L1560,440 L1566,452 L1384,452 Z" fill="#9a9aa2"/>')
    b.append('<ellipse cx="1600" cy="580" rx="46" ry="40" fill="#c8a8d0"/><ellipse cx="1590" cy="566" rx="16" ry="10" fill="#e8d8ec" opacity="0.6"/>'
             '<path d="M1600,542 C1588,512 1574,496 1560,488 M1602,542 C1608,510 1620,496 1636,488 M1601,542 L1600,494" stroke="#4a6a3a" stroke-width="7" fill="none"/>')
    b.append('<ellipse cx="400" cy="520" rx="70" ry="13" fill="#8f7146"/><path d="M342,518 C354,480 446,480 458,518 Z" fill="#c9a45c"/>'
             '<path d="M450,500 L490,486 L478,504 Z" fill="#c9a45c"/>' + flame(488, 440, 40))
    return svg(ROOM_DEFS, "".join(b))


def sickroom() -> str:
    """Healings, part one: a sickroom at night, the bed by the window, a bottle of medicine and a candle on the sill."""
    rnd = random.Random(173)
    b = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>', window(1100, 110, 360, 470, "url(#night)")]
    b.append("".join(f'<circle cx="{rnd.uniform(1120, 1440):.0f}" cy="{rnd.uniform(130, 400):.0f}" r="{rnd.choice([0.8, 1.2, 1.6])}" fill="#fff" opacity="{rnd.uniform(0.3, 0.9):.2f}"/>' for _ in range(22)))
    b.append('<circle cx="1220" cy="560" r="300" fill="url(#warm)"/>')
    b.append('<rect x="1080" y="586" width="400" height="20" fill="#3a2a1a"/>')                          # the sill
    b.append('<rect x="1150" y="526" width="34" height="60" rx="4" fill="#4a6a5a" opacity="0.9"/><rect x="1158" y="510" width="18" height="18" fill="#3a2414"/>')
    b.append('<ellipse cx="1380" cy="584" rx="30" ry="7" fill="#c9a45c"/><rect x="1372" y="520" width="16" height="64" fill="#f3ead2"/>' + flame(1380, 482, 34))
    b.append('<path d="M240,620 L240,420 L300,420 L300,500 L920,500 L920,460 L980,460 L980,620 Z" fill="#2a1d12"/>'   # the bed
             '<path d="M300,500 L920,500 L920,560 L300,560 Z" fill="#d8ccb0"/><ellipse cx="380" cy="490" rx="70" ry="26" fill="#efe6d0"/>'
             '<path d="M440,500 C560,470 760,470 900,500 L900,520 L440,520 Z" fill="#b8a890"/>')
    b.append(f'<rect x="0" y="620" width="{W}" height="{H - 620}" fill="#120c08"/>')
    return svg(ROOM_DEFS, "".join(b))


def snowstorm_tavern() -> str:
    """Healings, part two: the tavern in a snowstorm at night, its door shut fast, a rider coming through the snow."""
    rnd = random.Random(179)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2a3048"/><stop offset="1" stop-color="#7a8298"/>
    </linearGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    b.append(f'<path d="{hills(rnd, 560, 10, 0.9)}" fill="#c8ccd8"/>')
    b.append('<rect x="980" y="400" width="420" height="190" fill="#2a2430"/><path d="M950,406 L1190,300 L1430,406 Z" fill="#221c28"/>'
             '<path d="M1000,404 L1190,320 L1380,404" stroke="#e8ecf4" stroke-width="10" fill="none"/>'
             '<rect x="1060" y="470" width="60" height="50" fill="#f5c871"/><rect x="1290" y="470" width="60" height="50" fill="#f5c871" opacity="0.8"/>'
             '<rect x="1170" y="480" width="60" height="110" fill="#14101a"/>')
    b.append('<g transform="translate(560,600) scale(1.2)" fill="#14121c">'                           # the rider
             '<ellipse cx="0" cy="-44" rx="46" ry="18"/><path d="M-36,-50 L-58,-84 L-46,-90 L-24,-56 Z"/>'
             '<ellipse cx="-62" cy="-88" rx="16" ry="8" transform="rotate(25 -62 -88)"/>'
             '<path d="M-30,-30 L-34,0 M-16,-30 L-12,0 M18,-30 L14,0 M32,-30 L38,0" stroke="#14121c" stroke-width="5"/>'
             '<circle cx="4" cy="-96" r="8"/><path d="M-6,-88 L14,-88 L18,-56 L-10,-56 Z"/></g>')
    flakes = "".join(f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, 640):.0f}" r="{rnd.uniform(1.2, 3.5):.1f}" fill="#ffffff" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>' for _ in range(420))
    b.append(flakes)
    b.append(f'<rect x="0" y="610" width="{W}" height="{H - 610}" fill="#9aa0b4"/>')
    return svg(defs, "".join(b))


def cradle() -> str:
    """Sons for the childless, part one: a cradle by the window at dawn, a pair of small shoes beside it."""
    rnd = random.Random(181)
    defs = ROOM_DEFS.replace('<stop offset="0" stop-color="#0e1430"/><stop offset="1" stop-color="#2c3660"/>',
                             '<stop offset="0" stop-color="#4a5a8a"/><stop offset="1" stop-color="#f2cf9a"/>')
    b = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>', window(1180, 110, 380, 480, "url(#night)")]
    b.append('<path d="M1180,590 L700,620 L1560,620 Z" fill="#f2cf9a" opacity="0.12"/>')
    b.append(f'<rect x="0" y="606" width="{W}" height="{H - 606}" fill="#1a120b"/>')
    b.append('<path d="M620,600 C620,480 1000,480 1000,600" stroke="#3a2a1a" stroke-width="14" fill="none"/>'     # the rockers
             '<path d="M640,540 L980,540 L960,470 L660,470 Z" fill="#5a3a22"/><path d="M660,470 L960,470 L950,450 L670,450 Z" fill="#6a4a2a"/>'
             '<path d="M960,470 C1000,420 980,380 940,370 L930,450 Z" fill="#5a3a22"/>'
             '<path d="M680,470 C760,440 860,440 940,468" fill="#efe6d0"/>')
    b.append('<path d="M1080,600 C1080,580 1100,570 1120,574 L1140,600 Z M1150,600 C1150,580 1170,570 1190,574 L1210,600 Z" fill="#8a5a3a"/>')
    return svg(defs, "".join(b))


def forest_house() -> str:
    """Sons for the childless, part two: a small house alone in a dark forest, candles in its window, the loaded wagon on the road."""
    rnd = random.Random(191)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#080a18"/><stop offset="1" stop-color="#262c4a"/>
    </linearGradient>
    <radialGradient id="warm" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#ffe0a0" stop-opacity="0.5"/><stop offset="1" stop-color="#ffc070" stop-opacity="0"/>
    </radialGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 120, 0, 300)]
    for base, (lo, hi), col, n in [(540, (140, 240), "#141a2a", 70), (620, (260, 420), "#0a0e18", 30)]:
        trees = []
        for _ in range(n):
            x = rnd.uniform(-40, W + 40)
            if 760 < x < 1240:
                continue
            trees.append(pine(x, base + rnd.uniform(-10, 10), rnd.uniform(lo, hi), rnd))
        b.append(f'<path d="{" ".join(trees)}" fill="{col}"/>')
    b.append('<circle cx="1000" cy="500" r="220" fill="url(#warm)"/>')
    b.append('<rect x="900" y="450" width="200" height="140" fill="#14101a"/><path d="M880,454 L1000,380 L1120,454 Z" fill="#0e0a14"/>'
             '<rect x="940" y="490" width="56" height="46" fill="#f5c871"/><rect x="1010" y="490" width="56" height="46" fill="#f5c871"/>')
    b.append(wagon(650, 616, 1.0, "#080a12", people=0))
    b.append('<path d="M650,570 L762,570 L762,560 C740,540 680,540 650,560 Z" fill="#080a12"/>')
    b.append(f'<rect x="0" y="616" width="{W}" height="{H - 616}" fill="#0a0c14"/>')
    return svg(defs, "".join(b))


def whirlwind() -> str:
    """Demons, sorcerers and harmful spirits: a dark spirit rolling like a whirlwind out of the tollkeeper's house at night."""
    rnd = random.Random(193)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0c0e20"/><stop offset="1" stop-color="#3a3858"/>
    </linearGradient>
    <filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 100, 0, 360)]
    b.append(f'<path d="{hills(rnd, 600, 8, 1)}" fill="#1c1a2c"/>')
    b.append('<rect x="560" y="420" width="380" height="180" fill="#1a1622"/><path d="M530,426 L750,320 L970,426 Z" fill="#141018"/>'
             '<rect x="610" y="470" width="60" height="54" fill="#f5c871"/><rect x="820" y="470" width="60" height="54" fill="#f5c871" opacity="0.7"/>'
             '<rect x="720" y="490" width="60" height="110" fill="#2a2030"/>')
    spiral = []
    for k in range(260):                                                   # the whirlwind leaving through the door
        t = k / 260
        a = t * 22
        r = 20 + t * 150
        x = 800 + t * 620 + r * math.cos(a)
        y = 560 - t * 220 + r * 0.45 * math.sin(a)
        spiral.append(f"{x:.0f},{y:.0f}")
    b.append(f'<polyline points="{" ".join(spiral)}" stroke="#05040a" stroke-width="16" fill="none" opacity="0.7" filter="url(#blur3)"/>'
             f'<polyline points="{" ".join(spiral)}" stroke="#2a2440" stroke-width="3" fill="none" opacity="0.6"/>')
    b.append(f'<rect x="0" y="606" width="{W}" height="{H - 606}" fill="#0e0c18"/>')
    return svg(defs, "".join(b))


def river_crossing() -> str:
    """False accusations and dangers: a ford across the wide river at sunset, people crossing with their bundles before the Sabbath."""
    rnd = random.Random(197)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2a2a54"/><stop offset="0.5" stop-color="#c8786a"/><stop offset="0.58" stop-color="#f4c07a"/>
    </linearGradient>
    <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f0b878"/><stop offset="1" stop-color="#3a3a64"/>
    </linearGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 20, 0, 160)]
    b.append('<circle cx="1440" cy="510" r="60" fill="#ffe8b8"/>')
    b.append(f'<path d="{ridge(rnd, 500, 14, 60)}" fill="#5a4060"/>')
    b.append('<rect x="0" y="520" width="1920" height="560" fill="url(#water)"/>')
    for _ in range(50):
        x, y = rnd.uniform(0, W), rnd.uniform(530, 620)
        b.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{rnd.uniform(30, 120):.0f}" height="2" fill="#fff0d0" opacity="{rnd.uniform(0.15, 0.4):.2f}"/>')
    for k, x in enumerate(range(620, 1300, 90)):                            # the people wading across
        y = 586 - k * 3
        b.append(f'<g transform="translate({x},{y})" fill="#1a1424"><circle cx="0" cy="-58" r="7"/>'
                 '<path d="M-9,-50 L9,-50 L12,-8 L-12,-8 Z"/>'
                 f'<ellipse cx="{12 if k % 2 else -12}" cy="-56" rx="12" ry="9"/></g>'
                 f'<ellipse cx="{x}" cy="{y - 6}" rx="22" ry="3" fill="#fff0d0" opacity="0.35"/>')
    b.append(f'<rect x="0" y="608" width="{W}" height="{H - 608}" fill="#1a1a34"/>')
    return svg(defs, "".join(b))


def pillar_of_fire() -> str:
    """The Garden of Eden and Gehinnom: a pillar of fire over a grave in the cemetery at night, the road passing by."""
    rnd = random.Random(199)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#06070f"/><stop offset="1" stop-color="#1e1c30"/>
    </linearGradient>
    <linearGradient id="fire" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="#fff4c8"/><stop offset="0.3" stop-color="#ffb24a"/><stop offset="1" stop-color="#ff7a30" stop-opacity="0"/>
    </linearGradient>
    <filter id="blur8"><feGaussianBlur stdDeviation="8"/></filter>
    <filter id="blur30"><feGaussianBlur stdDeviation="30"/></filter>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 160, 0, 420)]
    b.append(f'<path d="{hills(rnd, 570, 10, 1)}" fill="#14121e"/>')
    b.append('<ellipse cx="960" cy="380" rx="200" ry="320" fill="#ffb24a" opacity="0.18" filter="url(#blur30)"/>'
             '<path d="M920,580 C900,420 940,260 960,80 C980,260 1020,420 1000,580 Z" fill="url(#fire)" filter="url(#blur8)"/>'
             '<path d="M940,580 C930,450 950,330 960,200 C970,330 990,450 980,580 Z" fill="url(#fire)"/>')
    for x, h in ((520, 60), (640, 48), (760, 56), (930, 70), (1140, 52), (1260, 62), (1380, 46)):      # gravestones
        b.append(f'<path d="M{x - 22},{600} L{x - 22},{600 - h} A22,22 0 0 1 {x + 22},{600 - h} L{x + 22},{600} Z" fill="#2a2638"/>')
    b.append('<path d="M0,640 C600,610 1300,610 1920,600 L1920,620 C1300,630 600,632 0,660 Z" fill="#3a3650" opacity="0.6"/>')
    b.append(f'<rect x="0" y="600" width="{W}" height="{H - 600}" fill="#0e0c16"/>')
    return svg(defs, "".join(b))


def dog_river() -> str:
    """Sin, repentance and reincarnation: a dog swimming in the dark river at dusk, a fisherman's boat with its net."""
    rnd = random.Random(211)
    defs = """
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1e2244"/><stop offset="0.55" stop-color="#8a6a80"/><stop offset="0.62" stop-color="#d8a080"/>
    </linearGradient>
    <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#b8889a"/><stop offset="1" stop-color="#1e2244"/>
    </linearGradient>
    """
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(rnd, 40, 0, 200)]
    b.append(f'<path d="{ridge(rnd, 470, 12, 60)}" fill="#3a3050"/>')
    trees = [pine(rnd.uniform(1200, 1920), 500, rnd.uniform(60, 120), rnd) for _ in range(30)]
    b.append(f'<path d="{" ".join(trees)}" fill="#2a2440"/>')
    b.append('<rect x="0" y="500" width="1920" height="580" fill="url(#water)"/>')
    b.append('<g transform="translate(1200,560)" fill="#14101e"><path d="M-120,0 L120,0 L90,26 L-90,26 Z"/>'           # the boat
             '<circle cx="-40" cy="-28" r="9"/><path d="M-50,-20 L-30,-20 L-26,0 L-54,0 Z"/>'
             '<path d="M20,0 L60,-60 L64,-58 L26,0 Z"/></g>'
             '<path d="M1260,500 C1300,520 1340,540 1380,560" stroke="#14101e" stroke-width="2" fill="none"/>'
             + "".join(f'<path d="M{1300 + k * 10},{520 + k * 6} l-6,30" stroke="#14101e" stroke-width="1.5"/>' for k in range(8)))
    b.append('<g transform="translate(720,580)" fill="#100c18"><ellipse cx="0" cy="0" rx="34" ry="10"/>'                     # the dog's head in the water
             '<ellipse cx="-30" cy="-12" rx="16" ry="12"/><path d="M-36,-22 L-30,-38 L-22,-22 Z"/><ellipse cx="-46" cy="-8" rx="9" ry="6"/></g>'
             '<ellipse cx="720" cy="586" rx="70" ry="6" fill="#ffffff" opacity="0.2"/><ellipse cx="720" cy="596" rx="110" ry="5" fill="#ffffff" opacity="0.12"/>')
    b.append(f'<rect x="0" y="620" width="{W}" height="{H - 620}" fill="#141632"/>')
    return svg(defs, "".join(b))


def bell() -> str:
    """His last days: the bell on its string in the big house at dusk, the string running out through the door to the small house."""
    defs = ROOM_DEFS.replace('<stop offset="0" stop-color="#0e1430"/><stop offset="1" stop-color="#2c3660"/>',
                             '<stop offset="0" stop-color="#2a2a52"/><stop offset="1" stop-color="#c8907a"/>')
    b = [f'<rect width="{W}" height="{H}" fill="url(#room)"/>']
    b.append('<rect x="1240" y="200" width="280" height="420" fill="url(#night)"/><rect x="1226" y="190" width="308" height="14" fill="#1e1610"/>'
             '<rect x="1226" y="190" width="14" height="430" fill="#1e1610"/><rect x="1520" y="190" width="14" height="430" fill="#1e1610"/>')
    b.append('<rect x="1340" y="470" width="120" height="100" fill="#14101a"/><path d="M1326,474 L1400,428 L1474,474 Z" fill="#100c14"/>'
             '<rect x="1380" y="500" width="30" height="28" fill="#f5c871"/>')
    b.append('<path d="M760,120 L760,250" stroke="#8f7146" stroke-width="3"/>'
             '<path d="M720,320 C720,260 740,240 760,240 C780,240 800,260 800,320 L812,334 L708,334 Z" fill="#c9a45c"/>'
             '<circle cx="760" cy="342" r="10" fill="#a8874e"/>')
    b.append('<path d="M760,250 C900,280 1100,300 1240,330 C1300,345 1360,400 1400,500" stroke="#c8b898" stroke-width="2.5" fill="none"/>')
    b.append('<circle cx="760" cy="300" r="220" fill="url(#warm)"/>')
    b.append(f'<rect x="0" y="620" width="{W}" height="{H - 620}" fill="#120c08"/>')
    return svg(defs, "".join(b))


DRAWINGS = {
    "the-boy-who-was-not-afraid": forest,
    "the-locked-gate": gate,
    "the-frog-in-the-wilderness": frog,
    "the-speech-of-the-birds": road,
    "the-passing-of-the-baal-shem-tov": candle,
    "the-authors-introduction": lectern,
    "the-hidden-years-and-the-revelation": prut,
    "rabbi-gershon-of-kitov": synagogue,
    "the-land-of-israel-and-the-way-there": ship,
    "in-prayer": prayer,
    "his-ways-and-customs": sabbath_table,
    "the-rabbi-of-polonne": letter_rain,
    "the-mokhiach-of-polonne-part-one": lvov_synagogue,
    "the-mokhiach-of-polonne-part-two": kitov_house,
    "the-maggid-of-mezritch": thunder,
    "the-maggids-household-and-disciples": sukkah,
    "rabbi-nachman-of-horodenka": lake_study_house,
    "rabbi-yitzchak-of-drohobych": tefillin,
    "tzaddikim-of-his-generation-part-one": nemirov_psalms,
    "tzaddikim-of-his-generation-part-two": friday_road,
    "opponents-and-testers": forest_clearing,
    "opponents-who-drew-close-part-one": dream_palace,
    "opponents-who-drew-close-part-two": moonlit_gemara,
    "seeing-from-afar": hilltop_view,
    "wonders-on-the-road": snowy_road,
    "leaseholders-and-noblemen-part-one": castle,
    "leaseholders-and-noblemen-part-two": gateway,
    "charity-and-money": purse,
    "simple-jews-and-hidden-tzaddikim": stockings_line,
    "fit-and-unfit": knife,
    "healings-part-one": sickroom,
    "healings-part-two": snowstorm_tavern,
    "sons-for-the-childless-part-one": cradle,
    "sons-for-the-childless-part-two": forest_house,
    "demons-sorcerers-and-harmful-spirits": whirlwind,
    "false-accusations-and-dangers": river_crossing,
    "the-garden-of-eden-and-gehinnom": pillar_of_fire,
    "sin-repentance-and-reincarnation": dog_river,
    "his-last-days": bell,
}


if __name__ == "__main__":
    for name in sys.argv[1:] or DRAWINGS:
        if name not in DRAWINGS:
            sys.exit(f"no drawing named {name!r}; one of: {', '.join(DRAWINGS)}")
        (HERE / f"{name}.svg").write_text(DRAWINGS[name](), encoding="utf-8")
        print(f"  {HERE / f'{name}.svg'}")
