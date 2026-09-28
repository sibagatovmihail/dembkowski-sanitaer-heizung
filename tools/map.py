"""Schematic service-area map around Ducherow (equirectangular, 1 km = 4 units).
Writes the inline SVG to tools/map.svg.html; paste it into index.html (#gebiet).

    python3 tools/map.py
"""
import math
from pathlib import Path

C = (53.7711, 13.7836)                      # Ducherow, Busower Str.
K = 4                                        # svg units per km
W = H = 440
R = 6371


def xy(lat, lon):
    dy = (lat - C[0]) * math.pi / 180 * R
    dx = (lon - C[1]) * math.pi / 180 * R * math.cos(C[0] * math.pi / 180)
    return W / 2 + dx * K, H / 2 - dy * K, math.hypot(dx, dy)


TOWNS = [  # name, lat, lon, label side
    ("Anklam", 53.8563, 13.6900, "l"), ("Ueckermünde", 53.7350, 14.0450, "r"),
    ("Pasewalk", 53.5063, 13.9900, "r"), ("Neubrandenburg", 53.5569, 13.2611, "r"),
    ("Friedland", 53.6650, 13.5440, "l"), ("Ferdinandshof", 53.6620, 13.8880, "r"),
    ("Torgelow", 53.6320, 14.0140, "r"), ("Usedom", 53.8740, 13.9230, "r"),
    ("Spantekow", 53.7667, 13.5500, "l"), ("Jarmen", 53.9210, 13.3420, "r"),
    ("Lassan", 53.9480, 13.8540, "r"), ("Wolgast", 54.0520, 13.7740, "r"),
    ("Strasburg", 53.5100, 13.7470, "l"),
]
# (unused) rough outline of the Kleines Haff and the Peenestrom (schematic only)
HAFF = [(53.745, 14.03), (53.77, 13.96), (53.80, 13.90), (53.83, 13.86), (53.855, 13.89),
        (53.865, 13.96), (53.885, 14.03), (53.905, 14.12), (53.92, 14.25), (53.80, 14.30),
        (53.75, 14.17), (53.735, 14.09)]
PEENE = [(53.852, 13.60), (53.856, 13.70), (53.862, 13.80), (53.875, 13.84), (53.92, 13.845),
         (53.97, 13.85), (54.02, 13.80), (54.06, 13.78), (54.12, 13.80)]


def pts(seq):
    return " ".join("%.1f,%.1f" % xy(a, b)[:2] for a, b in seq)


out = []
out.append(f'<svg class="map__svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="map-title map-desc">')
out.append('<title id="map-title">Einsatzgebiet rund um Ducherow</title>')
out.append('<desc id="map-desc">Schematische Karte: Ducherow in der Mitte, Ringe bei 15, 30 und 45 km Luftlinie. '
           'Orte: ' + ", ".join("%s (%d km)" % (n, round(xy(a, b)[2])) for n, a, b, _ in TOWNS) + '.</desc>')
out.append('<defs><clipPath id="map-clip"><rect width="%d" height="%d" rx="0"/></clipPath></defs>' % (W, H))
out.append('<g clip-path="url(#map-clip)">')
# ring labels sit where no town is: 15 km west-southwest, 30 km south-west, 45 km north-east
RING_LABEL = {15: 250, 30: 225, 45: 45}
for km in (45, 30, 15):
    out.append(f'<circle class="map__ring map__ring--{km}" cx="{W/2}" cy="{H/2}" r="{km*K}"/>')
for km in (45, 30, 15):
    a = math.radians(RING_LABEL[km])
    x, y = W / 2 + km * K * math.sin(a), H / 2 - km * K * math.cos(a)
    out.append(f'<text class="map__km" x="{x:.1f}" y="{y + 3.5:.1f}" text-anchor="middle">{km} km</text>')
for n, a, b, side in TOWNS:
    x, y, d = xy(a, b)
    anchor = "end" if side == "l" else "start"
    tx = x - 7 if side == "l" else x + 7
    out.append(f'<g class="map__town" data-km="{round(d)}"><circle cx="{x:.1f}" cy="{y:.1f}" r="3.5"/>'
               f'<text x="{tx:.1f}" y="{y + 4:.1f}" text-anchor="{anchor}">{n}</text></g>')
out.append('</g>')
out.append(f'<g class="map__home"><circle class="map__pulse" cx="{W/2}" cy="{H/2}" r="10"/>'
           f'<circle cx="{W/2}" cy="{H/2}" r="7"/><text x="{W/2}" y="{H/2 + 24}" text-anchor="middle">Ducherow</text></g>')
out.append('</svg>')
Path(__file__).with_name("map.svg.html").write_text("\n".join(out) + "\n")
for n, a, b, _ in sorted(TOWNS, key=lambda t: xy(t[1], t[2])[2]):
    print("%-15s %2d km" % (n, round(xy(a, b)[2])))
