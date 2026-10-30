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
}


if __name__ == "__main__":
    for name in sys.argv[1:] or DRAWINGS:
        if name not in DRAWINGS:
            sys.exit(f"no drawing named {name!r}; one of: {', '.join(DRAWINGS)}")
        (HERE / f"{name}.svg").write_text(DRAWINGS[name](), encoding="utf-8")
        print(f"  {HERE / f'{name}.svg'}")
