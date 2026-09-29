"""Landa Park re-subdivision plat (Park Highlands No. 2, Comal County, TX) -> DXF polylines.

Pure Python, no dependencies. Writes:
  landa_park_plat.dxf  (AutoCAD R12 DXF: closed POLYLINE per lot, street lines, labels)
  landa_park_plat.svg  (preview)
  landa_park_plat_report.txt (lot areas, computed vs. plat lengths)

Units: feet. X = east, Y = north. Bearings are from the plat.
"""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
STREET_W = 60.0  # street width not shown on plat; scaled ~60'


def az(deg):  # azimuth (clockwise from north) -> unit vector
    r = math.radians(deg)
    return (math.sin(r), math.cos(r))


def bearing_az(ns, d, m, ew):
    a = d + m / 60.0
    if ns == "N" and ew == "E": return a
    if ns == "S" and ew == "E": return 180 - a
    if ns == "S" and ew == "W": return 180 + a
    return 360 - a


def add(p, v, s=1.0): return (p[0] + v[0] * s, p[1] + v[1] * s)
def sub(p, q): return (p[0] - q[0], p[1] - q[1])
def dist(p, q): return math.hypot(p[0] - q[0], p[1] - q[1])
def cross(a, b): return a[0] * b[1] - a[1] * b[0]


def intersect(p, u, q, v):
    """Intersection of line p+t*u with q+s*v."""
    t = cross(sub(q, p), v) / cross(u, v)
    return add(p, u, t)


# --- plat bearings -------------------------------------------------------
NY = az(bearing_az("N", 88, 22, "W"))    # New York Ave (read N 88-22 W; fits lot-line math exactly)
VA = az(bearing_az("N", 64, 39, "W"))    # Virginia Blvd
PA = az(bearing_az("N", 26, 59, "W"))    # Pennsylvania Blvd
PQ = az(bearing_az("N", 63, 1, "E"))     # perpendicular to Pennsylvania (plat: S 63-01 W)

A = (0.0, 0.0)  # virtual apex where New York Ave and Virginia Blvd lines meet (SE tip)

def ny(d): return add(A, NY, d)
def va(d): return add(A, VA, d)

# Block 2 (between New York Ave, Virginia Blvd, Pennsylvania Blvd)
# Lot lines 219.23 / 260.35 / 301.45 / 383.33 grow 41.1' per 100' -> isosceles, equal frontages.
D1, D2, D3, D4 = 533.46, 633.46, 733.46, 933.46
TN, TV = ny(D1 - 450.0), va(D1 - 426.0)   # lot 1 frontages 450' (NY) and 426' (Virginia)
C5 = ny(D4 + 68.0 + 194.0)                # NY Ave meets Pennsylvania Blvd east line

def pe(a, off=0.0):   # point on Pennsylvania east line, a = distance north from C5, off = east
    return add(add(C5, PA, a), PQ, off)

S6 = pe(218.0)                             # lot 5 west side 218'
E6 = intersect(S6, PQ, A, VA)              # 424.42' line meets Virginia Blvd
N45 = intersect(ny(D4 + 68.0), PA, S6, PQ)  # lot 4/5 line, drawn parallel to Pennsylvania

def pw(u, w):  # Block 1: u = north from lot 2/3 line, w = west from Pennsylvania west line
    return add(pe(u - 540.0), PQ, -(STREET_W + w))  # 540' offset scaled from plat

# Block 1 lots 1-2 (irregular south end)
R12 = (-150.0 + math.sqrt(157.7 ** 2 - 150.0 ** 2), 150.0)   # bottom of lot 1/2 line
P1 = (-47.5, 300.0)
def _q1():
    dr = sub(P1, R12); L = math.hypot(*dr)
    c = (145.0 ** 2 + L ** 2 - 36.3 ** 2) / (2 * 145.0 * L)
    ang = math.acos(c); ux, wy = dr[0] / L, dr[1] / L
    return (R12[0] + 145.0 * (ux * math.cos(ang) - wy * math.sin(ang)),
            R12[1] + 145.0 * (ux * math.sin(ang) + wy * math.cos(ang)))
Q1 = _q1()

lots = []  # (block, lot, [points])
for k in range(3, 20):
    u0, u1 = (k - 3) * 100.0, (k - 2) * 100.0
    lots.append(("1", str(k), [pw(u0, 0), pw(u1, 0), pw(u1, 300), pw(u0, 300)]))
lots.append(("1", "2", [pw(0, 0), pw(0, 150), pw(*R12), pw(-150, 0)]))
lots.append(("1", "1", [pw(0, 150), pw(0, 300), pw(*P1), pw(*Q1), pw(*R12)]))

# Block 2, east of Pennsylvania
lots.append(("2", "12", [pe(768), pe(1018), pe(768, 250)]))
lots.append(("2", "11", [pe(668), pe(768), pe(768, 250), pe(668, 350)]))
for lot, a0 in (("10", 568), ("9", 468), ("8", 368)):
    lots.append(("2", lot, [pe(a0), pe(a0 + 100), pe(a0 + 100, 350), pe(a0, 350)]))
lots.append(("2", "6", [S6, pe(368), pe(368, 350), E6]))
lots.append(("2", "5", [C5, S6, N45, ny(D4 + 68.0)]))
lots.append(("2", "4", [ny(D4 + 68.0), N45, E6, va(D4), ny(D4)]))
lots.append(("2", "3", [ny(D4), va(D4), va(D3), ny(D3)]))
lots.append(("2", "7", [ny(D3), va(D3), va(D2), ny(D2)]))   # lot no. as read on plat - verify
lots.append(("2", "2", [ny(D2), va(D2), va(D1), ny(D1)]))
lots.append(("2", "1", [ny(D1), va(D1), TV, TN]))


# --- streets ---------------------------------------------------------------
def offset_polyline(pts, d):
    """Offset an open polyline d to the right of travel direction."""
    segs = []
    for p, q in zip(pts, pts[1:]):
        v = sub(q, p); L = math.hypot(*v); v = (v[0] / L, v[1] / L)
        n = (v[1], -v[0])
        segs.append((add(p, n, d), v))
    out = [segs[0][0]]
    for (p0, v0), (p1, v1) in zip(segs, segs[1:]):
        out.append(intersect(p0, v0, p1, v1))
    last_p, last_v = segs[-1]
    out.append(add(last_p, last_v, dist(pts[-2], pts[-1])))
    return out

va_west = [va(-250), E6, pe(368, 350), pe(668, 350), pe(1018), pe(1130, -112)]
va_east = offset_polyline(va_west, STREET_W)
ny_north = [ny(-250), C5]
ny_south_start = add(ny(-250), az(bearing_az("S", 1, 38, "W")), STREET_W)
ny_south_end = intersect(ny_south_start, NY, C5, PA)
pa_east_south = [ny_south_end, pe(-800)]
pa_east_north = [C5, pe(1018)]
pa_west = [pe(-800, -STREET_W), pe(1300, -STREET_W)]
sw_street = [pw(-150, 0), pw(*R12), pw(*Q1), add(pw(*Q1), sub(pw(*Q1), pw(*R12)), 0.8)]

streets = [va_west, va_east, ny_north, [ny_south_start, ny_south_end],
           pa_east_south, pa_east_north, pa_west]


# --- labels ----------------------------------------------------------------
def centroid(pts):
    a = cx = cy = 0.0
    for p, q in zip(pts, pts[1:] + pts[:1]):
        c = cross(p, q); a += c; cx += (p[0] + q[0]) * c; cy += (p[1] + q[1]) * c
    return (cx / (3 * a), cy / (3 * a)), abs(a) / 2

def text_angle(v):
    ang = math.degrees(math.atan2(v[1], v[0]))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    return ang

texts = []  # (x, y, height, rotation, string, layer)
for blk, lot, pts in lots:
    c, _ = centroid(pts)
    texts.append((c[0], c[1], 18, 0, lot, "LOT-NUM"))

mid = lambda p, q: ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
def street_label(p, v, s, h=22):
    texts.append((p[0], p[1], h, text_angle(v), s, "STREET-NAME"))

street_label(add(mid(pe(-500), pe(-500, -STREET_W)), PA, 0), PA, "PENNSYLVANIA BOULEVARD")
street_label(add(mid(pe(700), pe(700, -STREET_W)), PA, 0), PA, "N 26-59' W")
street_label(add(ny(600), az(bearing_az("S", 1, 38, "W")), STREET_W / 2), NY, "NEW YORK AVE.  N 88-22' W")
street_label(add(va(700), az(bearing_az("N", 25, 21, "E")), STREET_W / 2), VA, "VIRGINIA BOULEVARD  N 64-39' W")
street_label(add(pe(520, 350), PQ, STREET_W / 2), PA, "VIRGINIA BLVD.")
texts.append((*pw(900, 150), 30, text_angle(PA), "BLK 1", "BLOCK"))
bc, _ = centroid(lots[-6][2]); texts.append((bc[0] + 60, bc[1] + 40, 30, 0, "BLK 2", "BLOCK"))
b3 = add(ny(700), az(bearing_az("S", 1, 38, "W")), 250); texts.append((*b3, 30, 0, "BLK 3", "BLOCK"))
texts.append((*add(pe(-500, -STREET_W), PQ, -420), 26, 0,
               "RE-SUBDIVISION, PARK HIGHLANDS No. 2 - COMAL CO., TX   SCALE 1\"=200'", "TITLE"))

# plat dimensions placed on their lines
def dim(p, q, s, off=10):
    v = sub(q, p); L = math.hypot(*v); n = (-v[1] / L, v[0] / L)
    m = add(mid(p, q), n, off)
    texts.append((m[0], m[1], 10, text_angle(v), s, "DIM"))

for k in range(3, 20):
    dim(pw((k - 3) * 100, 0), pw((k - 2) * 100, 0), "100'")
dim(pw(0, 150), pw(0, 300), "S 63-01' W 300'")
dim(pw(0, 0), pw(-150, 0), "150'"); dim(pw(-150, 0), pw(*R12), "157.7'")
dim(pw(*R12), pw(*Q1), "145'"); dim(pw(*Q1), pw(*P1), "36.3'"); dim(pw(*P1), pw(0, 300), "47.5'")
dim(pe(768), pe(1018), "250'"); dim(pe(768, 250), pe(1018), "353.55'")
dim(pe(768), pe(768, 250), "250'"); dim(pe(668, 350), pe(768, 250), "141.42'")
for a0 in (368, 468, 568, 668): dim(pe(a0), pe(a0, 350), "350'")
for a0 in (368, 468, 568): dim(pe(a0 + 100, 350), pe(a0, 350), "100'")
dim(S6, pe(368), "150'"); dim(C5, S6, "218'"); dim(S6, E6, "424.42'")
dim(ny(D4 + 68.0), C5, "194'"); dim(ny(D4), ny(D4 + 68.0), "68'")
dim(ny(D3), ny(D4), "200'"); dim(ny(D2), ny(D3), "100'"); dim(ny(D1), ny(D2), "100'"); dim(TN, ny(D1), "450'")
dim(va(D4), E6, "~80'"); dim(va(D3), va(D4), "200'"); dim(va(D2), va(D3), "100'"); dim(va(D1), va(D2), "100'")
dim(TV, va(D1), "426'"); dim(TN, TV, "36'")
dim(ny(D4), va(D4), "383 1/3'"); dim(ny(D3), va(D3), "301.45'")
dim(ny(D2), va(D2), "260.35'"); dim(ny(D1), va(D1), "219.23'")


# --- DXF (R12) -------------------------------------------------------------
LAYERS = {"LOTS": 7, "STREETS": 1, "STREET-NAME": 3, "LOT-NUM": 2, "DIM": 8, "BLOCK": 4, "TITLE": 7}

def dxf():
    o = []
    w = lambda c, v: o.extend([str(c), str(v)])
    w(0, "SECTION"); w(2, "HEADER"); w(9, "$ACADVER"); w(1, "AC1009"); w(9, "$INSUNITS"); w(70, 2)
    w(0, "ENDSEC")
    w(0, "SECTION"); w(2, "TABLES"); w(0, "TABLE"); w(2, "LAYER"); w(70, len(LAYERS))
    for name, col in LAYERS.items():
        w(0, "LAYER"); w(2, name); w(70, 0); w(62, col); w(6, "CONTINUOUS")
    w(0, "ENDTAB"); w(0, "ENDSEC")
    w(0, "SECTION"); w(2, "ENTITIES")
    def poly(pts, layer, closed):
        w(0, "POLYLINE"); w(8, layer); w(66, 1); w(10, 0); w(20, 0); w(30, 0); w(70, 1 if closed else 0)
        for x, y in pts:
            w(0, "VERTEX"); w(8, layer); w(10, f"{x:.4f}"); w(20, f"{y:.4f}"); w(30, 0)
        w(0, "SEQEND"); w(8, layer)
    for _, _, pts in lots: poly(pts, "LOTS", True)
    for s in streets: poly(s, "STREETS", False)
    poly(sw_street, "STREETS", False)
    for x, y, h, rot, s, layer in texts:
        w(0, "TEXT"); w(8, layer); w(10, f"{x:.4f}"); w(20, f"{y:.4f}"); w(30, 0); w(40, h); w(1, s)
        w(50, f"{rot:.4f}"); w(72, 1); w(11, f"{x:.4f}"); w(21, f"{y:.4f}"); w(31, 0); w(73, 2)
    w(0, "ENDSEC"); w(0, "EOF")
    return "\n".join(o) + "\n"


def svg():
    allp = [p for _, _, pts in lots for p in pts] + [p for s in streets for p in s]
    x0 = min(p[0] for p in allp) - 150; x1 = max(p[0] for p in allp) + 150
    y0 = min(p[1] for p in allp) - 150; y1 = max(p[1] for p in allp) + 150
    T = lambda p: (p[0] - x0, y1 - p[1])
    col = {"LOT-NUM": "#b8860b", "STREET-NAME": "#1a7f37", "DIM": "#666", "BLOCK": "#1f6feb", "TITLE": "#000"}
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x1-x0:.0f} {y1-y0:.0f}" '
         f'width="{(x1-x0)/2:.0f}" height="{(y1-y0)/2:.0f}"><rect width="100%" height="100%" fill="#fff"/>']
    for _, _, pts in lots:
        s.append('<polygon fill="#f4f1e8" stroke="#000" stroke-width="2" points="' +
                 " ".join("%.1f,%.1f" % T(p) for p in pts) + '"/>')
    for st in streets + [sw_street]:
        s.append('<polyline fill="none" stroke="#c00" stroke-width="2" points="' +
                 " ".join("%.1f,%.1f" % T(p) for p in st) + '"/>')
    for x, y, h, rot, t, layer in texts:
        X, Y = T((x, y))
        s.append(f'<text x="{X:.1f}" y="{Y:.1f}" font-size="{h}" font-family="Arial" fill="{col[layer]}" '
                 f'text-anchor="middle" dominant-baseline="middle" transform="rotate({-rot:.2f} {X:.1f} {Y:.1f})">'
                 f'{t.replace("&", "&amp;").replace(chr(34), "&quot;")}</text>')
    s.append("</svg>")
    return "\n".join(s)


def report():
    r = ["LANDA PARK PLAT - lot areas (closed polylines)", ""]
    for blk, lot, pts in lots:
        _, area = centroid(pts)
        r.append(f"Block {blk} Lot {lot:>2}: {area:10.0f} sq ft  ({area/43560:.3f} ac)")
    r += ["", "Checks against plat:",
          f"  424.42' line computed: {dist(S6, E6):.2f}'",
          f"  383 1/3' line computed: {dist(ny(D4), va(D4)):.2f}'",
          f"  36' cutoff at SE tip computed: {dist(TN, TV):.2f}'",
          f"  Lot 4 Virginia frontage computed: {dist(va(D4), E6):.2f}' (not labeled)",
          "", "Assumptions: street widths 60'; Block 1 placed 540' south of Block 2 along",
          "Pennsylvania (scaled); lot 4/5 line parallel to Pennsylvania; NY Ave read as N 88-22 W;",
          "lot number '7' in Block 2 as read - verify."]
    return "\n".join(r) + "\n"


if __name__ == "__main__":
    for name, fn in (("landa_park_plat.dxf", dxf), ("landa_park_plat.svg", svg),
                     ("landa_park_plat_report.txt", report)):
        with open(os.path.join(HERE, name), "w") as f:
            f.write(fn())
    print(report())
