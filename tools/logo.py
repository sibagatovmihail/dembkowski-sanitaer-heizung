"""Rebuild the business's current logo as SVG, text converted to outlines.

Source: the logo on the business's Cylex listing (250 x 250 JPG, logo area
about 157 x 49 px). Every coordinate below is measured on that image, in its
pixels; the SVG keeps that coordinate system (viewBox around x 44-206, y 94-150).

  - "Dembkowski"        Verdana Bold, navy #1F3B78, ink x 54-181.5, baseline 128
  - "Meisterbetrieb"    Titillium Web 400, orange, tucked above "mbkowsk"
  - flame               orange outline, two tongues, above the end of the name
  - pipe                light-blue rounded rectangle behind, open where the name
                        sits on it; the orange bar covers its lower right
  - "Sanitär - Heizung" Titillium Web 400, white on the orange bar

    python3 tools/logo.py   ->  assets/logo.svg, assets/logo-negativ.svg, assets/favicon.svg
Needs tools/fonts/TitilliumWeb-300.ttf and -400.ttf (Google Fonts, OFL; gitignored).
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = Path(__file__).resolve().parent.parent
NAVY, ORANGE, PIPE = "#1F3B78", "#F68A3F", "#A4C0E6"
X0, Y0, W, H = 44, 94, 162, 56                 # viewBox, in source pixels


class Face:
    def __init__(self, path):
        self.font = TTFont(path)
        self.cmap = self.font.getBestCmap()
        self.gs = self.font.getGlyphSet()
        self.hmtx = self.font["hmtx"]
        b = BoundsPen(self.gs); self.gs[self.cmap[ord("H")]].draw(b)
        self.cap = b.bounds[3]

    def layout(self, text, tracking=0.0):
        out, x = [], 0
        for ch in text:
            g = self.cmap[ord(ch)]
            out.append((g, x)); x += self.hmtx[g][0] + tracking
        return out

    def ink(self, items):
        b = BoundsPen(self.gs)
        for g, x in items:
            self.gs[g].draw(TransformPen(b, (1, 0, 0, 1, x, 0)))
        return b.bounds

    def fit(self, text, left, right, baseline, cap=None):
        """outline `text`: ink runs from left to right; with `cap` given the size
        comes from the cap height and the letter-spacing makes up the width"""
        items = self.layout(text)
        xmin, _, xmax, _ = self.ink(items)
        if cap:
            s = cap / self.cap
            tr = ((right - left) / s - (xmax - xmin)) / (len(text) - 1)
            items = self.layout(text, tr)
            xmin, _, xmax, _ = self.ink(items)
        else:
            s = (right - left) / (xmax - xmin)
        pen = SVGPathPen(self.gs, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip("."))
        for g, x in items:
            t = (s, 0, 0, -s, left - xmin * s + x * s - X0, baseline - Y0)
            self.gs[g].draw(TransformPen(pen, t))
        return pen.getCommands(), s * self.cap


verdana = Face("/System/Library/Fonts/Supplemental/Verdana Bold.ttf")
tit300 = Face(ROOT / "tools/fonts/TitilliumWeb-300.ttf")
tit400 = Face(ROOT / "tools/fonts/TitilliumWeb-400.ttf")

name, name_cap = verdana.fit("Dembkowski", 54, 181.5, 128)
master, _ = tit400.fit("Meisterbetrieb", 120.2, 164.8, 114.1, cap=3.9)       # small, letter-spaced
tagline, tag_cap = tit400.fit("Sanitär - Heizung", 89.4, 193.4, 144.0, cap=10.6)
print("cap heights: name %.1f (measured ~13.5), tagline %.1f (measured ~11)" % (name_cap, tag_cap))

# pipe: rounded rectangle (stroke centre), open on top where the name sits
L, R, T, B, r = 47.6 - X0, 203 - X0, 122.8 - Y0, 139.6 - Y0, 4.4
gap_l, gap_r = 52.2 - X0, 182.4 - X0
pipe = (f"M{gap_r:.1f} {T:.1f}H{R - r:.1f}A{r} {r} 0 0 1 {R:.1f} {T + r:.1f}V{B - r:.1f}"
        f"A{r} {r} 0 0 1 {R - r:.1f} {B:.1f}H{L + r:.1f}A{r} {r} 0 0 1 {L:.1f} {B - r:.1f}"
        f"V{T + r:.1f}A{r} {r} 0 0 1 {L + r:.1f} {T:.1f}H{gap_l:.1f}")
bar = (85.6 - X0, 129.9 - Y0, 197 - 85.6, 147.6 - 129.9, 2.6)       # x, y, w, h, radius

# flame: two tongues as an outline, drawn in source pixels around x 170-186, y 96-113
fx, fy = -X0, -Y0
flame = (f"M{171.6+fx:.1f} {112.2+fy:.1f}"
         f"C{169.6+fx:.1f} {109.2+fy:.1f} {170.4+fx:.1f} {105.4+fy:.1f} {173.2+fx:.1f} {102.6+fy:.1f}"
         f"C{174.6+fx:.1f} {101.2+fy:.1f} {175.3+fx:.1f} {99.3+fy:.1f} {174.9+fx:.1f} {97.2+fy:.1f}"
         f"C{178.4+fx:.1f} {99.4+fy:.1f} {179.6+fx:.1f} {102.8+fy:.1f} {178.8+fx:.1f} {106.2+fy:.1f}"
         f"C{180.2+fx:.1f} {105.6+fy:.1f} {181.3+fx:.1f} {104.3+fy:.1f} {181.8+fx:.1f} {102.6+fy:.1f}"
         f"C{184.6+fx:.1f} {105.2+fy:.1f} {185.6+fx:.1f} {109.2+fy:.1f} {183.4+fx:.1f} {112.2+fy:.1f}")
flame_in = (f"M{175.2+fx:.1f} {112.2+fy:.1f}"
            f"C{174.2+fx:.1f} {110.2+fy:.1f} {175+fx:.1f} {108.2+fy:.1f} {176.8+fx:.1f} {106.6+fy:.1f}"
            f"C{177.6+fx:.1f} {108.6+fy:.1f} {179.4+fx:.1f} {109.6+fy:.1f} {179.6+fx:.1f} {112.2+fy:.1f}")


def svg(name_fill, title="Meisterbetrieb Dembkowski, Sanitär - Heizung"):
    bx, by, bw, bh, br = bar
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
<title id="t">{title}</title>
<path d="{pipe}" fill="none" stroke="{PIPE}" stroke-width="1.9"/>
<path d="{name}" fill="{name_fill}"/>
<path d="{master}" fill="{ORANGE}"/>
<g fill="none" stroke="{ORANGE}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="{flame}"/><path d="{flame_in}"/></g>
<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="{br}" fill="{ORANGE}"/>
<path d="{tagline}" fill="#fff"/>
</svg>
'''


(ROOT / "assets/logo.svg").write_text(svg(NAVY))
(ROOT / "assets/logo-negativ.svg").write_text(svg("#FFFFFF"))

# favicon: navy tile, white D (Verdana Bold) and the orange flame
items = verdana.layout("D")
xmin, ymin, xmax, ymax = verdana.ink(items)
s = 34 / (ymax - ymin)
pen = SVGPathPen(verdana.gs, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip("."))
verdana.gs[items[0][0]].draw(TransformPen(pen, (s, 0, 0, -s, 12 - xmin * s, 52)))
(ROOT / "assets/favicon.svg").write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="{NAVY}"/>
<path fill="#fff" d="{pen.getCommands()}"/>
<g transform="translate(-126 -88) scale(1)" fill="none" stroke="{ORANGE}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M{171.6} {112.2}C169.6 109.2 170.4 105.4 173.2 102.6C174.6 101.2 175.3 99.3 174.9 97.2C178.4 99.4 179.6 102.8 178.8 106.2C180.2 105.6 181.3 104.3 181.8 102.6C184.6 105.2 185.6 109.2 183.4 112.2"/></g>
</svg>
''')
print("written")
