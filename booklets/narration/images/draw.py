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


DRAWINGS = {
    "the-boy-who-was-not-afraid": forest,
    "the-locked-gate": gate,
    "the-frog-in-the-wilderness": frog,
    "the-speech-of-the-birds": road,
    "the-passing-of-the-baal-shem-tov": candle,
}


if __name__ == "__main__":
    for name in sys.argv[1:] or DRAWINGS:
        if name not in DRAWINGS:
            sys.exit(f"no drawing named {name!r}; one of: {', '.join(DRAWINGS)}")
        (HERE / f"{name}.svg").write_text(DRAWINGS[name](), encoding="utf-8")
        print(f"  {HERE / f'{name}.svg'}")
