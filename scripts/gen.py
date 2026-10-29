import math, re, html, json

# ---------- geometry helpers (feet, y down, north up) ----------
def rot(x, y, a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return x * c - y * s, x * s + y * c

def pip(pt, poly):
    x, y = pt; ins = False
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins

def dseg(p, a, b):
    px, py = p; ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)

def drect(p, r):
    x0, y0, x1, y1 = r
    dx = max(x0 - p[0], 0, p[0] - x1); dy = max(y0 - p[1], 0, p[1] - y1)
    return math.hypot(dx, dy)

def clear(room, p, r):
    poly = room['poly']
    if not pip(p, poly): return False
    for i in range(len(poly)):
        if dseg(p, poly[i], poly[(i + 1) % len(poly)]) < r: return False
    for ob in room.get('obst', []):
        if drect(p, ob) < r: return False
    for (cx, cy, cr) in room.get('cols', []):
        if math.hypot(p[0] - cx, p[1] - cy) < r + cr: return False
    for (a, b, hw) in room.get('segobst', []):
        if dseg(p, a, b) < r + hw: return False
    return True

# ---------- rooms ----------
C = (40.35, 45.3); R = 45.3
a0 = math.atan2(40.35, 20.7)
ARC = [(C[0] + R * math.sin(t), C[1] - R * math.cos(t)) for t in [-a0 + 2 * a0 * i / 48 for i in range(49)]]
MAPLE = ARC + [(80.3, 25), (57, 25), (50.3, 32), (50.3, 44.3), (30.3, 44.3), (30.3, 40.3), (0.3, 25.6)]
OAK = [(0, 0), (41.3, 0), (41.3, 30.9), (37, 30.9), (32, 36.2), (12.3, 36.2), (7.3, 30.9), (0, 30.9)]
HICK = [(-26.7, 13.9), (0, 13.9), (0, 30.9), (-7, 30.9), (-7, 35.2), (-9, 34.4), (-26.7, 27)]
SYC = [(-26.7, -0.6), (0, -0.6), (0, 13.9), (-26.7, 13.9)]
DBL = [(-26.7, -0.6), (0, -0.6), (0, 30.9), (-7, 30.9), (-7, 35.2), (-9, 34.4), (-26.7, 27)]
FULL = [(-26.7, -0.6), (0, -0.6), (0, 0), (41.3, 0), (41.3, 30.9), (37, 30.9), (32, 36.2), (12.3, 36.2), (7.3, 30.9),
        (-7, 30.9), (-7, 35.2), (-9, 34.4), (-26.7, 27)]
BLEACH = (4, 0, 41.3, 4)
D1 = ((0, 0), (0, 30.9)); D2 = ((-26.7, 13.9), (0, 13.9))
OAKDOORS = [((4, 30.9), (6.7, 30.9)), ((37.6, 30.9), (40.7, 30.9))]
HDOORS = [((-3.5, 30.9), (-0.8, 30.9)), ((-26.7, 17.7), (-26.7, 21))]
SDOORS = [((-26.7, 6.7), (-26.7, 10)), ((-6, -0.6), (-3.3, -0.6))]

YA57 = C[1] - math.sqrt(R * R - (57 - C[0]) ** 2)
STORAGE = [(57, YA57)] + [p for p in ARC if p[0] > 57] + [(80.3, 25), (57, 25)]
WD = (0.899, 0.4375); WN = (0.4375, -0.899); WA = 25.95; W0 = (0.3, 25.6)   # Maple left wall: direction, inward normal, angle
def wallpt(s_, off): return (W0[0] + WD[0] * s_ + WN[0] * off, W0[1] + WD[1] * s_ + WN[1] * off)

SLW, SLE = (-26.7, 27), (-9, 34.4)              # Hickory slanted wall, west and east ends
SLD = ((SLE[0] - SLW[0]) / 19.19, (SLE[1] - SLW[1]) / 19.19)
def slpt(s_): return (SLW[0] + SLD[0] * s_, SLW[1] + SLD[1] * s_)
H_TV = [(slpt(2.1), slpt(6.3))]; H_WB = [(slpt(9.4), slpt(14.2))]
H_EAST = [((0, 17.8), (0, 21.4)), ((0, 21.6), (0, 25.3))]     # chalkboard, whiteboard on the moving wall to Oak
S_EAST = [((0, 2.2), (0, 6.2)), ((0, 6.3), (0, 10.3))]
WIL_DOORS = [((0, 0.2), (0, 3)), ((40.25, 4.6), (40.25, 8.6)), ((40.25, 9.0), (40.25, 13.0))]

OAKSCR = [((17, 36.2), (27.3, 36.2))]   # projector screen on the Oak whiteboard (bay wall)

ROOMS = {
 'Maple': dict(tag='Maple', poly=MAPLE, obst=[(56.6, 0, 81, 25)], cols=[(30.3, 32, 0.6)], storage=STORAGE,
    glass=[ARC, [(37, 44.3), (44, 44.3)]], doors=[((31, 44.3), (36, 44.3)), ((44.6, 44.3), (49.6, 44.3))],
    walls=[((57, 14), (57, 25))], tv=[((56.75, 16.5), (56.75, 22.5))], opened=[((57, YA57), (57, 14))], zone=(16, 10, 52, 32), front='N', caps=dict(rounds=12, longs=24, seats=96), per=8,
    labels=[(40.35, -1.6, 'Windows (front)', 0), (40.35, 47.4, 'Doors', 0), (55.6, 19.5, 'TV', -90), (67.5, 17.5, 'Storage', 0)], dims='Seating area about 57 ft wide and 44 ft deep, plus storage'),
 'Willow': dict(tag='Willow', poly=[(0, 0), (40.25, 0), (40.25, 20), (0, 20)], obst=[(0, 4, 2.2, 20), (37.5, 4.4, 40.25, 13.2)],
    glass=[[(0, 20), (40.25, 20)]], doors=WIL_DOORS, counter=(0, 4, 2.2, 20), tv=[((17, 0), (23, 0))],
    zone=(4, 1.2, 37, 18.8), front='N', fill_rows=True, caps=dict(rounds=5, longs=13, seats=25), per=5,
    labels=[(20, 21.7, 'Windows', 0), (-1.6, 12, 'Counter with sink', -90), (20, -1.6, 'TV wall (front)', 0), (42, 8.8, 'Storage', 90)], dims='20 ft by 40 ft'),
 'Oak': dict(tag='Oak', poly=OAK, screen=OAKSCR, obst=[BLEACH], bleach=BLEACH, doors=OAKDOORS, closed=[D1],
    zone=(1.5, 5, 39.8, 30), front='S', caps=dict(rounds=9, longs=26, seats=72), per=8,
    labels=[(22.6, -1.5, 'Pull-out seats (stored)', 0), (22, 38.6, 'Whiteboard and projector screen (front)', 0), (-1.6, 15.5, 'Moving wall', -90)],
    dims='41 ft by 31 ft, plus a 5 ft bay'),
 'Full Oak': dict(tag='Oak', poly=FULL, screen=OAKSCR, obst=[BLEACH], bleach=BLEACH, doors=OAKDOORS + HDOORS + SDOORS, opened=[D1, D2],
    zone=(-6.5, 5, 39.8, 30), zone2=(-25, 5, 39.8, 26.5), front='S', caps=dict(rounds=9, longs=26, seats=72), per=8,
    labels=[(22.6, -1.9, 'Pull-out seats (stored)', 0), (22, 39, 'Whiteboard and projector screen (front)', 0)], dims='68 ft by 31 ft'),
 'Double Meeting Room': dict(tag='Oak', poly=DBL, doors=HDOORS + SDOORS, closed=[D1], opened=[D2],
    tv=H_TV, boards=H_WB + H_EAST + S_EAST,
    zone=(-25.5, 0.6, -1.2, 26.3), front='E', caps=dict(rounds=7, longs=14, seats=56), per=8,
    labels=[(1.6, 15, 'Moving wall, whiteboards (front)', 90)], dims='27 ft by 28 to 35 ft'),
 'Hickory': dict(tag='Oak', poly=HICK, doors=HDOORS, closed=[((0, 13.9), (0, 30.9)), D2],
    tv=H_TV, boards=H_WB + H_EAST,
    zframe=(-9.46, 32.91, 202.7, 17, 19), filt=True, fvec=(-0.3857, 0.9226),
    only=['Banquet', 'Lecture', 'Panel', 'Classroom', 'Horseshoe', 'Pod', 'Boardroom', 'Cabaret', 'Exam', 'Long Table Dinner', 'Runway'],
    zone=(-25.5, 15, -1.2, 26.3), front='W', caps=dict(rounds=3, longs=6, seats=24), per=8,
    labels=[(-13, 12.6, 'Moving wall', 0), (1.4, 22, 'Moving wall', 90), (-18.6, 32.6, 'TV and whiteboard (front)', 22.7)], dims='27 ft by 13 to 21 ft'),
 'Sycamore': dict(tag='Oak', poly=SYC, doors=SDOORS, closed=[((0, -0.6), (0, 13.9)), D2],
    boards=S_EAST, zone=(-25.5, 0.6, -1.2, 12.8), front='E', caps=dict(rounds=2, longs=4, seats=16), per=8,
    labels=[(-13, 15.6, 'Moving wall', 0), (1.6, 6.65, 'Whiteboards (front)', 90)], dims='27 ft by 14 ft'),
}
ORDER = ['Maple', 'Willow', 'Oak', 'Full Oak', 'Double Meeting Room', 'Hickory', 'Sycamore']

# ---------- zone frame ----------
def frame(room):
    if room.get('zframe'):
        ox, oy, th, W, D = room['zframe']; return (ox, oy), th, W, D
    x0, y0, x1, y1 = room.get('usezone') or room['zone']; f = room['front']
    if f == 'N': return (x0, y0), 0, x1 - x0, y1 - y0
    if f == 'S': return (x1, y1), 180, x1 - x0, y1 - y0
    if f == 'W': return (x0, y1), -90, y1 - y0, x1 - x0
    if f == 'E': return (x1, y0), 90, y1 - y0, x1 - x0

class L:  # layout in zone frame, flattened to room coords
    def __init__(s, room):
        s.room = room; s.o, s.th, s.W, s.D = frame(room)
        s.longs = []; s.rounds = []; s.chairs = []
    def _w(s, u, v):
        x, y = rot(u, v, s.th); return s.o[0] + x, s.o[1] + y
    def long(s, u, v, a=0, chairs=()):
        x, y = s._w(u, v); s.longs.append((x, y, a + s.th))
        for cx, cy, ph in chairs:
            dx, dy = rot(cx, cy, a); s.chair(u + dx, v + dy, ph + a)
    def chair(s, u, v, ph=0):
        x, y = s._w(u, v); s.chairs.append((x, y, ph + s.th))
    def presenter(s):
        s.long(s.W / 2, 3.0, 0, [(0, -2.25, 180)])
    def counts(s):
        return len(s.longs), len(s.rounds), len(s.chairs)

BACK2 = [(-1.5, 2.25, 0), (1.5, 2.25, 0)]

def lecture(room, head=False):
    l = L(room); W, D = l.W, l.D; cap = room['caps']['seats']
    v0 = 7.0
    if head:
        v0 = 9.5
        if W >= 14:
            l.long(W / 2 - 3, 3.2, 0, [(-1.5, -2.25, 180), (1.5, -2.25, 180)]); l.long(W / 2 + 3, 3.2, 0, [(-1.5, -2.25, 180), (1.5, -2.25, 180)])
        else:
            l.long(W / 2, 3.2, 0, [(-1.5, -2.25, 180), (1.5, -2.25, 180)])
        cap -= len(l.chairs)
    p = 1.9
    if W >= 16:
        n = min(8, int(((W - 4) / 2) / p)); us = [W / 2 - 2 - p * (i + .5) for i in range(n)] + [W / 2 + 2 + p * (i + .5) for i in range(n)]
    else:
        n = min(10, int((W - 2.5) / p)); us = [W / 2 + p * (i - (n - 1) / 2) for i in range(n)]
    if room.get('fill_rows') and W >= 16:   # shallow room: use more, shorter rows so the seat limit is reached
        rmax = int((D - v0 - 0.8) / 3.2) + 1; n2 = max(1, cap // (2 * rmax))
        if n2 < n:
            n = n2; us = [W / 2 - 2 - p * (i + .5) for i in range(n)] + [W / 2 + 2 + p * (i + .5) for i in range(n)]
    if room.get('spread'):   # spread the chairs evenly over the whole room
        rows, n = room['spread']
        if W >= 16:
            p = min(3.0, (W - 4) / 2 / n)
            us = [W / 2 - 2 - p * (i + .5) for i in range(n)] + [W / 2 + 2 + p * (i + .5) for i in range(n)]
        else:   # narrow room: one block, no center aisle
            p = min(3.0, (W - 2) / n); us = [W / 2 + p * (i - (n - 1) / 2) for i in range(n)]
        a = 9.5 if head else 5
        for r in range(rows):
            for u in us: l.chair(u, a + (D - 1.5 - a) * r / (rows - 1), 0)
        return l
    v = v0; seats = 0
    while v + 0.8 <= D and seats + len(us) <= cap:
        for u in us: l.chair(u, v, 0)
        seats += len(us); v += 3.2
    return l

def lecture_entry(room, name):
    if name == 'Hickory':   # rows run straight east-west and face south, not along the slanted wall
        return lecture(dict(room, zframe=None, zone=(-25.5, 15.1, -1.2, 31.0), front='S', fill_rows=True))
    if name == 'Willow':
        return lecture(dict(room, spread=(3, 4)))
    return lecture(room)

def panel_entry(room, name):
    if name == 'Hickory':   # audience faces east, panel table along the east moving wall facing west
        return lecture(dict(room, zframe=None, zone=(-25.5, 15.1, -1.2, 29.7), front='E'), head=True)
    if name == 'Sycamore':
        return lecture(dict(room, spread=(4, 3)), head=True)
    return lecture(room, head=True)

def classroom(room, vee=0):
    l = L(room); W, D = l.W, l.D; caps = room['caps']
    nb = min(2, int(((W - 4) / 2) / 6))
    l.long(W / 2, 2.0, 0, [(0, -2.25, 180)])   # teacher table and chair at the front
    v = 10.0 if vee else 7.0; pitch = 6.0 if vee else 5.5
    if vee and nb == 0: return None
    while v + 3.2 <= D:
        row = []
        if nb:
            for side in (-1, 1):
                for j in range(nb):
                    du = side * (2 + 6 * (j + .5)); a = -side * vee
                    dx, dy = rot(du, 0, a); row.append((W / 2 + dx, v + dy, a))
        else:
            n = max(1, int(W / 6))
            row = [(W / 2 + 6 * (i - (n - 1) / 2), v, 0) for i in range(n)]
        if len(l.longs) - 1 + len(row) > caps['longs'] or len(l.chairs) - 1 + 2 * len(row) > caps['seats']: break   # teacher table not counted
        for u, vv, a in row: l.long(u, vv, a, BACK2)
        v += pitch
    return l

def classroom_entry(room, name):
    if name == 'Hickory':   # face east toward the moving wall with the boards; 4 student tables plus the teacher table
        return classroom(dict(room, zframe=None, zone=(-25.5, 15.1, -1.2, 29.7), front='E', caps=dict(room['caps'], longs=4)))
    return classroom(room)

def conference_entry(room, name):
    if name == 'Maple':      # long east-west ring across the main floor
        return ring(dict(room, zone=(11, 12, 53, 30.5), usezone=None), 6, 1)
    if name == 'Full Oak':   # long east-west ring across Oak and the Double Meeting Room
        return ring(dict(room, usezone=room['zone2']), 9, 1)
    if name == 'Double Meeting Room':   # one table longer along the moving wall
        return ring(room, 3, 1)
    if name in ('Willow', 'Oak'):   # long east-west ring
        return ring(room, 6, 1)
    return ring(room, 2, 1)

def ring(room, amax, bmax, closed=True):
    l = L(room); W, D = l.W, l.D; caps = room['caps']
    best = None
    for a in range(amax, 0, -1):
        for b in range(bmax, 0, -1):
            n = (2 * a if closed else a) + 2 * b
            need_w = 6 * a + 5.5
            need_d = (6 * b + 5 + 5.5) if closed else (6 * b + 2.5 + 3 + 5.5)
            if need_w <= W and need_d <= D and n <= caps['longs'] and 2 * n + (0 if closed else 1) <= caps['seats']:
                if best is None or n > best[2]: best = (a, b, n)
    if not best: return None
    a, b, n = best
    if closed:
        vc = D / 2
        top, bot = vc - 3 * b - 1.25, vc + 3 * b + 1.25
        for i in range(a):
            u = W / 2 + 6 * (i - (a - 1) / 2)
            l.long(u, top, 180, BACK2); l.long(u, bot, 0, BACK2)
        vs = [vc + 6 * (j - (b - 1) / 2) for j in range(b)]
    else:
        bot = D - 3.8
        for i in range(a):
            l.long(W / 2 + 6 * (i - (a - 1) / 2), bot, 0, BACK2)
        vs = [bot - 1.25 - 3 - 6 * j for j in range(b)]
        l.presenter()
    for vv in vs:
        l.long(W / 2 - (3 * a - 1.25), vv, 90, BACK2); l.long(W / 2 + (3 * a - 1.25), vv, -90, BACK2)
    l.key = (a, b)
    return l

def horseshoe(room):
    l = L(room); W, D = l.W, l.D; cap = min(room['caps']['seats'] - 1, 20)
    Rr = min((W - 3) / 2, (D - 8.5) / 1.34, 9.5)
    if Rr < 4: return None
    tmax = 110; n = min(cap, int(Rr * math.radians(2 * tmax) / 2.15) + 1)
    vc = 6.8 + 0.34 * Rr
    for i in range(n):
        t = -tmax + 2 * tmax * i / (n - 1)
        l.chair(W / 2 + Rr * math.sin(math.radians(t)), vc + Rr * math.cos(math.radians(t)), -t)
    l.presenter(); return l

def pod(room):
    l = L(room); W, D = l.W, l.D; cap = room['caps']['seats'] - 1
    nu = int((W - 6.6) / 8.5) + 1; v = 10.8
    us = [W / 2 + 8.5 * (i - (nu - 1) / 2) for i in range(nu)]
    while v + 3.3 <= D:
        for u in us:
            if len(l.chairs) + 5 > cap: break
            for k in range(5):
                t = 72 * k + 36
                l.chair(u + 2.3 * math.sin(math.radians(t)), v + 2.3 * math.cos(math.radians(t)), -t)
        v += 8.5
    if len(l.chairs) < 10: return None
    l.presenter(); return l

def exam(room):
    l = L(room); W, D = l.W, l.D; caps = room['caps']
    nu = int((W + 2) / 8); v = 6.5
    us = [W / 2 + 8 * (i - (nu - 1) / 2) for i in range(nu)]
    while v + 3.2 <= D and len(l.longs) + nu <= min(caps['longs'], caps['seats']):
        for u in us: l.long(u, v, 0, [(0, 2.25, 0)])
        v += 5.5
    return l if l.longs else None

def boardroom(room):
    l = L(room); W, D = l.W, l.D; caps = room['caps']
    along_v = D >= W; Lg = D if along_v else W; Sh = W if along_v else D
    if Sh < 10.5: return None
    k = min(3, int((Lg - 7) / 6), caps['longs'] // 2, (caps['seats'] - 4) // 4)
    if k < 1: return None
    for i in range(k):
        off = 6 * (i - (k - 1) / 2)
        if along_v:
            l.long(W / 2 - 1.25, D / 2 + off, 90, BACK2); l.long(W / 2 + 1.25, D / 2 + off, -90, BACK2)
        else:
            l.long(W / 2 + off, D / 2 - 1.25, 180, BACK2); l.long(W / 2 + off, D / 2 + 1.25, 0, BACK2)
    e = 3 * k + 1.0
    for s2 in (-1.25, 1.25):
        if along_v:
            l.chair(W / 2 + s2, D / 2 - e, 180); l.chair(W / 2 + s2, D / 2 + e, 0)
        else:
            l.chair(W / 2 - e, D / 2 + s2, 90); l.chair(W / 2 + e, D / 2 + s2, -90)
    return l

def jobfair(room, name):
    l = L(room); W, D = l.W, l.D; caps = room['caps']
    if name == 'Maple':
        Rt = R - 4.6; n = 6; t0, t1 = -50, 17
        for i in range(n):
            t = t0 + (t1 - t0) * i / (n - 1)
            x, y = C[0] + Rt * math.sin(math.radians(t)), C[1] - Rt * math.cos(math.radians(t))
            l.longs.append((x, y, t))
            for cx in (-1.5, 1.5):
                dx, dy = rot(cx, -2.25, t); l.chairs.append((x + dx, y + dy, t + 180))
        for s_ in (11, 21):
            x, y = wallpt(s_, 3.5); l.longs.append((x, y, WA))
            for cx in (-1.5, 1.5):
                dx, dy = rot(cx, 2.25, WA); l.chairs.append((x + dx, y + dy, WA))
        return l
    if W < 16 or D < 12: return None
    def col(n, lo, hi): return [lo + (hi - lo) * (i + .5) / n for i in range(n)]
    ns = max(1, int((D - 3) / 9)); nbk = max(0, int((W - 14) / 9))
    items = [(3.3, v, 90) for v in col(ns, 1.5, D - 1.5)] + [(W - 3.3, v, -90) for v in col(ns, 1.5, D - 1.5)] + [(u, D - 3.3, 0) for u in col(nbk, 7.5, W - 7.5)]
    for u, v, a in items[:caps['longs']]: l.long(u, v, a, BACK2)
    return l

def _tbl(l, x, y, a):   # table in room coords with two chairs on its "back" side (local +y)
    l.longs.append((x, y, a))
    for cx in (-1.5, 1.5):
        dx, dy = rot(cx, 2.25, a); l.chairs.append((x + dx, y + dy, a))

def jobfair_entry(room, name):
    if name == 'Willow':   # west table moved under the TV, plus one more there
        l = jobfair(room, name)
        keep = [t for t in l.longs if t[0] > 8]
        l.chairs = [c for c in l.chairs if c[0] > 8]; l.longs = keep
        for x in (15.5, 24.5): _tbl(l, x, 3.3, 180)   # 3 ft gap between them
        return l
    if name == 'Double Meeting Room':   # 2 north, 1 south, 2 on the west wall, 2 on the east moving wall
        l = L(room)
        for x in (-8.03, -18.68): _tbl(l, x, 3.9, 180)
        sx, sy = slpt(9.6); _tbl(l, sx + 0.3857 * 3.5, sy - 0.9226 * 3.5, 22.7)   # along the slanted south wall
        for y in (9.0, 18.0): _tbl(l, -22.2, y, 90)
        for y in (10.0, 19.0): _tbl(l, -3.5, y, -90)
        return l
    if name == 'Full Oak':   # same table along the slanted south wall as in the Double Meeting Room
        l = jobfair(room, name)
        sx, sy = slpt(9.6); _tbl(l, sx + 0.3857 * 3.5, sy - 0.9226 * 3.5, 22.7)
        return l
    return jobfair(room, name)

def facing(x, y, tx, ty):
    fx, fy = tx - x, ty - y
    return math.degrees(math.atan2(fx, -fy))

def rounds(room, cabaret=False, pitch0=9.0, rc=4.3):
    cap = room['caps']['rounds']; poly = room['poly']
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    best = None
    pitch = pitch0
    while pitch <= 16:
        for stag in (False, True):
            rp = pitch * (0.87 if stag else 1)
            off = 0
            while off < rp:
                pts = []; y = min(ys) + 4.3 + off; r = 0
                while y < max(ys):
                    # valid x intervals
                    iv = []; x = min(xs); cur = None
                    while x <= max(xs):
                        ok = clear(room, (x, y), rc)
                        if ok and cur is None: cur = x
                        if not ok and cur is not None: iv.append((cur, x - .25)); cur = None
                        x += .25
                    for a, b in iv:
                        n = int((b - a) / pitch) + 1
                        if stag and r % 2 == 1: n = max(n - 1, 1 if (b - a) < pitch else n - 1)
                        if n <= 0: continue
                        mid = (a + b) / 2
                        for q in [(mid + pitch * (i - (n - 1) / 2), y) for i in range(n)]:
                            if all(math.hypot(q[0] - t[0], q[1] - t[1]) >= 8.8 for t in pts): pts.append(q)
                    y += rp; r += 1
                if len(pts) <= cap:
                    key = (len(pts), pitch, not stag)
                    if best is None or key > best[0]: best = (key, pts)
                off += 0.5
        pitch += 0.5
    l = L(room); l.rounds = best[1]
    fv = room.get('fvec') or {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}[room['front']]
    per = room['per']
    for (x, y) in l.rounds:
        if cabaret:
            for t in (-100, -50, 0, 50, 100):
                dx, dy = rot(-fv[0], -fv[1], t); cx, cy = x + 3.5 * dx, y + 3.5 * dy
                l.chairs.append((cx, cy, facing(cx, cy, x, y)))
        else:
            for k in range(per):
                t = 360 * k / per + (0 if per % 2 else 360 / per / 2)
                cx, cy = x + 3.5 * math.sin(math.radians(t)), y + 3.5 * math.cos(math.radians(t))
                l.chairs.append((cx, cy, facing(cx, cy, x, y)))
    return l

def banquet(room, name):
    if name == 'Willow':
        l = rounds(room); l.note = 'food on the counter'; return l
    if name in ('Oak', 'Full Oak'):
        food = [(16.15 + 6 * i, 34.55, 0) for i in range(3)]   # food tables under the whiteboard, in the bay
        if name == 'Full Oak':   # food tables along the west wall of the Double Meeting Room, between the doors
            food = [(-25.05, 4.2 + 6 * i, 90) for i in range(4)]   # 4 tables end to end; the west doors are only storage
        food = [t for t in food if all(clear(room, p, 0.2) for p in corners(*t))]
        room['segobst'] = [(rot(-3, 0, a) and (x + rot(-3, 0, a)[0], y + rot(-3, 0, a)[1]), (x + rot(3, 0, a)[0], y + rot(3, 0, a)[1]), 1.25 + 2.5) for x, y, a in food]
        l = rounds(room); del room['segobst']
        l.food = food; return l
    if name != 'Maple': return rounds(room)
    ss = [7.8 + 6 * i for i in range(4)]
    CK = (46.9, 40.5)   # check-in table: short end against the right-hand wall by the doors; chair behind it facing the doors
    room['segobst'] = [(wallpt(ss[0] - 3, 1.65), wallpt(ss[-1] + 3, 1.65), 1.25 + 2.5),
                       ((CK[0] - 3, CK[1] - 1.5), (CK[0] + 3, CK[1] - 1.5), 1.25 + 2.0),
                       ((38.3, 44.3), (38.3, 37.5), 2.5)]   # keep a walkway in from the doors
    l = rounds(room); del room['segobst']
    l.longs.append((CK[0], CK[1], 0)); l.chairs.append((CK[0], CK[1] - 2.25, 180))
    l.xlabels = [(CK[0] - 9.6, CK[1] + 0.1, 'Check-in', 0)]; l.longword = 'check-in table'
    l.food = [(*wallpt(s_, 1.65), WA) for s_ in ss]
    l.xlabels += [(*wallpt(16.8, -2.0), 'Food tables', WA)]
    return l

def cabaret(room, name):
    """Round tables with chairs on the far side, every chair turned toward the speaker table; food tables on a side wall."""
    sx, sy = slpt(9.6)
    SPK = {   # speaker table (x, y, angle); its 2 chairs sit between the table and the wall
        'Maple': (40.35, 6.4, 180), 'Willow': (20, 3.3, 180), 'Oak': (22.15, 32.8, 0), 'Full Oak': (22.15, 32.8, 0),
        'Double Meeting Room': (-3.4, 13.9, -90), 'Hickory': (sx + 0.3857 * 3.4, sy - 0.9226 * 3.4, 22.7), 'Sycamore': (-3.4, 6.65, -90)}
    west4 = [(-25.05, 4.2 + 6 * i, 90) for i in range(4)]
    FOOD = {
        'Maple': [(*wallpt(7.8 + 6 * i, 1.65), WA) for i in range(4)], 'Willow': [],
        'Oak': [(1.65, 12 + 6 * i, 90) for i in range(3)], 'Full Oak': west4, 'Double Meeting Room': west4,
        'Hickory': [(-25.05, 17.4, 90), (-25.05, 23.4, 90)], 'Sycamore': [(-25.05, 3.2, 90), (-25.05, 9.2, 90)]}
    spk = SPK[name]; food = FOOD[name]
    def seg(t, hw):
        x, y, a = t; d = rot(3, 0, a); return ((x - d[0], y - d[1]), (x + d[0], y + d[1]), hw)
    room['segobst'] = [seg(spk, 1.25 + 4.0)] + [seg(t, 1.25 + 2.5) for t in food]
    MANUAL = {'Double Meeting Room': [(-16.5, 5.0), (-16.5, 13.9), (-16.5, 22.8), (-9.5, 5.0), (-9.5, 22.8)],
              'Sycamore': [(-14.5, 3.7), (-14.5, 9.6)]}
    if name in MANUAL:
        del room['segobst']; l = L(room); l.rounds = list(MANUAL[name])
    else:
        small = name == 'Hickory'
        l = rounds(room, pitch0=8.0 if small else 9.0, rc=4.0 if small else 4.3); del room['segobst']
    if name == 'Willow':   # no tables along the TV wall, beside the speaker
        l.rounds = [p for p in l.rounds if p[1] > 10]
    if name == 'Maple':    # no tables by the doors; a check-in table goes there instead
        l.rounds = [p for p in l.rounds if p[1] < 35]
    fx, fy = spk[0], spk[1]
    l.chairs = []
    per = 5
    for (x, y) in l.rounds:   # chairs on the side away from the speaker, all turned toward the speaker
        dx, dy = x - fx, y - fy; dn = math.hypot(dx, dy); ux, uy = dx / dn, dy / dn
        sp = 70 if name == 'Sycamore' else 90   # narrower fan of chairs where the room is tight
        for t in (-sp, -sp / 2, 0, sp / 2, sp)[:per]:
            vx, vy = rot(ux, uy, t); cx, cy = x + 3.5 * vx, y + 3.5 * vy
            l.chairs.append((cx, cy, facing(cx, cy, fx, fy)))
    keep = []
    for c in l.chairs:   # two tables can share the chair spot between them; keep one
        if all(math.hypot(c[0] - k[0], c[1] - k[1]) >= 1.35 for k in keep): keep.append(c)
    l.chairs = keep
    l.longs = []; _tbl(l, *spk); l.longword = 'speaker table'
    bx, by = rot(0, 1, spk[2])
    if abs(by) > 0.7: l.xlabels = [(spk[0] - bx * 3.0, spk[1] - by * 3.0, 'Speaker', 0)]
    else: l.xlabels = [(spk[0] - 0.5, spk[1] + 4.8, 'Speaker', 0)]   # vertical table: label past its end
    if name == 'Maple':   # same check-in table as banquet: short end on the right-hand wall, chair facing the doors
        l.longs.append((46.9, 40.5, 0)); l.chairs.append((46.9, 38.25, 180))
        l.xlabels.append((46.9 - 9.6, 40.6, 'Check-in', 0))
        l.longparts = ['1 speaker table', '1 check-in table']
    if food: l.food = food
    else: l.note = 'food on the counter'
    return l

def theatre(room, name):
    if name not in ('Oak', 'Full Oak'): return None
    l = L(room); l.ext = (4, 0, 41.3, 21); return l

SETUPS = [
 ('Banquet', banquet),
 ('Lecture', lambda r, n: lecture_entry(r, n)),
 ('Panel', lambda r, n: panel_entry(r, n)),
 ('Job Fair', jobfair_entry),
 ('Classroom', lambda r, n: classroom_entry(r, n)),
 ('Classroom V', lambda r, n: classroom(r, vee=15)),
 ('Conference', lambda r, n: conference_entry(r, n)),
 ('Square', lambda r, n: ring(r, 3, 2)),
 ('U-Shape', lambda r, n: ring(dict(r, zone=(16, 8.5, 52, 32), usezone=None), 3, 2, closed=False) if n == 'Maple' else ring(r, 3, 2, closed=False)),
 ('Horseshoe', lambda r, n: horseshoe(dict(r, zframe=None, zone=(-25.5, 15.1, -1.2, 29.7), front='E')) if n == 'Hickory' else horseshoe(r)),
 ('Pod', lambda r, n: pod(r)),
 ('Theatre Seating', lambda r, n: theatre(r, n)),
 ('Boardroom', lambda r, n: boardroom(dict(r, zframe=None, zone=(-25.5, 15.1, -1.2, 27.5), front='N')) if n == 'Hickory' else boardroom(r)),
 ('Cabaret', cabaret),
 ('Exam', lambda r, n: exam(r)),
]

# ---------- validation ----------
def corners(x, y, a, w=6, h=2.5):
    return [(x + dx, y + dy) for dx, dy in (rot(sx * w / 2, sy * h / 2, a) for sx in (-1, 1) for sy in (-1, 1))]

def check(name, sname, l):
    room = ROOMS[name]; bad = 0
    obst = [] if getattr(l, 'ext', None) else None
    for x, y, a in l.longs:
        for p in corners(x, y, a):
            if not clear(room, p, 0.3): bad += 1
    for x, y, a in l.chairs:
        if not clear(room, (x, y), 0.75): bad += 1
    for x, y in l.rounds:
        if not clear(room, (x, y), 2.6): bad += 1
    if bad: print('  pre-overlap bad', sname, name, bad)
    # overlaps between chairs
    ch = l.chairs
    for i in range(len(ch)):
        for j in range(i + 1, len(ch)):
            if math.hypot(ch[i][0] - ch[j][0], ch[i][1] - ch[j][1]) < 1.35: bad += 1
    return bad

# ---------- svg ----------
def f(v): return ('%.2f' % v).rstrip('0').rstrip('.')
def pts(p): return ' '.join(f(x) + ',' + f(y) for x, y in p)

def svg(name, l=None, title=''):
    room = ROOMS[name]; poly = room['poly']
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    pad = 4.2
    x0, y0, x1, y1 = min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad + 3.2
    w = x1 - x0; fs = max(1.3, w / 33); sw = max(0.28, w / 190)
    o = [f'<svg viewBox="{f(x0)} {f(y0)} {f(w)} {f(y1 - y0)}" role="img" aria-label="{html.escape(title)}" style="--sw:{f(sw)}px;--fs:{f(fs)}px">']
    o.append(f'<polygon class="fl" points="{pts(poly)}"/>')
    ext = getattr(l, 'ext', None) if l else None
    if 'bleach' in room:
        b = ext or room['bleach']
        o.append(f'<rect class="bl" x="{f(b[0])}" y="{f(b[1])}" width="{f(b[2] - b[0])}" height="{f(b[3] - b[1])}"/>')
        step = 2.6 if ext else 1.0
        yy = b[1] + step
        while yy < b[3] - 0.1:
            o.append(f'<line class="bll" x1="{f(b[0])}" y1="{f(yy)}" x2="{f(b[2])}" y2="{f(yy)}"/>'); yy += step
        if ext:
            o.append(f'<text class="lb in" x="{f((b[0] + b[2]) / 2)}" y="{f(b[3] + 2.6)}" text-anchor="middle">150 fixed seats, facing the whiteboards</text>')
    if 'storage' in room:
        o.append(f'<polygon class="st" points="{pts(room["storage"])}"/>')
    for m in (getattr(l, 'marks', []) if l else []):
        if m[0] == 'rect':
            o.append(f'<rect class="mk" x="{f(m[1])}" y="{f(m[2])}" width="{f(m[3] - m[1])}" height="{f(m[4] - m[2])}" rx="1"/>')
            o.append(f'<text class="lb" x="{f((m[1] + m[3]) / 2)}" y="{f((m[2] + m[4]) / 2)}" text-anchor="middle" dominant-baseline="middle">{html.escape(m[5])}</text>')
        else:
            o.append(f'<circle class="mk" cx="{f(m[1])}" cy="{f(m[2])}" r="{f(m[3])}"/>')
            o.append(f'<text class="lb" x="{f(m[1])}" y="{f(m[2])}" text-anchor="middle" dominant-baseline="middle">{html.escape(m[4])}</text>')
    if 'counter' in room:
        b = room['counter']; o.append(f'<rect class="ct" x="{f(b[0])}" y="{f(b[1])}" width="{f(b[2] - b[0])}" height="{f(b[3] - b[1])}"/>')
    for a, b in room.get('opened', []):
        o.append(f'<line class="dv open" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>')
    if l:
        for x, y in l.rounds: o.append(f'<circle class="tb" cx="{f(x)}" cy="{f(y)}" r="2.5"/>')
        for x, y, a in l.longs: o.append(f'<rect class="tb" x="-3" y="-1.25" width="6" height="2.5" rx=".3" transform="translate({f(x)} {f(y)}) rotate({f(a)})"/>')
        for x, y, a in getattr(l, 'food', []): o.append(f'<rect class="tb fd" x="-3" y="-1.25" width="6" height="2.5" rx=".3" transform="translate({f(x)} {f(y)}) rotate({f(a)})"/>')
        for x, y, a in l.chairs: o.append(f'<use href="#chr" transform="translate({f(x)} {f(y)}) rotate({f(a)})"/>')
    o.append(f'<polygon class="wl" points="{pts(poly)}"/>')
    for a, b in room.get('walls', []): o.append(f'<line class="wl" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>')
    for cx, cy, cr in room.get('cols', []): o.append(f'<circle class="col" cx="{f(cx)}" cy="{f(cy)}" r="{f(cr)}"/>')
    for a, b in room.get('closed', []): o.append(f'<line class="dv" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>')
    for g in room.get('glass', []): o.append(f'<polyline class="gl" points="{pts(g)}"/>')
    for a, b in room.get('boards', []): o.append(f'<line class="wbl" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>')
    for a, b in room.get('screen', []): o.append(f'<line class="scl" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>')
    for a, b in room.get('tv', []): o.append(f'<line class="tvl" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>')
    for a, b in room.get('doors', []): o.append(f'<line class="dr" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>')
    for lx, ly, t, r in room.get('labels', []) + (getattr(l, 'xlabels', []) if l else []):
        if ext and 'stored' in t: t = 'Pull-out seats (open)'
        tr = f' transform="rotate({r} {f(lx)} {f(ly)})"' if r else ''
        o.append(f'<text class="lb" x="{f(lx)}" y="{f(ly)}" text-anchor="middle" dominant-baseline="middle"{tr}>{html.escape(t)}</text>')
    if not l and name == 'Full Oak':
        for lx, ly, t in ((20.6, 17, 'Oak'), (-13.3, 23, 'Hickory'), (-13.3, 7, 'Sycamore')):
            o.append(f'<text class="lb in big" x="{lx}" y="{ly}" text-anchor="middle">{t}</text>')
    # scale bar
    bx, by = min(xs), max(ys) + pad + 0.4
    o.append(f'<path class="sb" d="M{f(bx)} {f(by)}v1.2h10v-1.2"/><text class="lb" x="{f(bx + 11)}" y="{f(by + 1.3)}">10 ft</text>')
    o.append('</svg>')
    return ''.join(o)

def plural(n, w): return f'{n} {w}' + ('' if n == 1 else 's')

def caption(l):
    if getattr(l, 'ext', None): return '150 fixed seats'
    nl, nr, nc = l.counts(); parts = []
    if nr: parts.append(plural(nr, getattr(l, 'roundword', 'round table')))
    if getattr(l, 'longparts', None): parts += l.longparts
    elif nl: parts.append(plural(nl, getattr(l, 'longword', 'long table')))
    if nc: parts.append(plural(nc, 'chair'))
    if getattr(l, 'food', None): parts.append(plural(len(l.food), 'food table'))
    if getattr(l, 'note', None): parts.append(l.note)
    return ', '.join(parts)

def filt(room, l):
    keep = []; gone = []
    for t in l.longs:
        (keep if all(clear(room, p, 0.3) for p in corners(*t)) else gone).append(t)
    def near(c, ts): return any(math.hypot(c[0] - t[0], c[1] - t[1]) < 2.8 for t in ts)
    l.longs = keep
    l.chairs = [c for c in l.chairs if clear(room, c[:2], 0.75) and not (near(c, gone) and not near(c, keep))]
    return l

def build(setups=None):
    out = {}; report = []
    for sname, fn in (setups or SETUPS):
        figs = []; prev = {}
        for name in ORDER:
            room = ROOMS[name]
            room['usezone'] = room.get('zone2') if sname in ('Job Fair', 'Exam', 'Lecture', 'Panel', 'Mixer') else None
            if room.get('only') and sname not in room['only']: continue
            l = fn(room, name)
            if l is not None and room.get('filt'): l = filt(room, l)
            if l is None or (not l.chairs and not getattr(l, 'ext', None)): continue
            if sname == 'Square':
                c = ring(room, 2, 1)
                if c and getattr(c, 'key', None) == getattr(l, 'key', 0): continue
            bad = check(name, sname, l)
            report.append((sname, name, caption(l), bad))
            cap = caption(l); tag = room['tag'].lower()
            title = f'{sname} in {name}: {cap}'
            figs.append(f'<figure data-room="{room["tag"]}"><button type="button" class="plan" data-cap="{html.escape(sname)} · {html.escape(name)} · {html.escape(cap)}">{svg(name, l, title)}</button><figcaption><span class="tag tag-{tag}">{html.escape(name)}</span>{html.escape(cap)}</figcaption></figure>')
        out[sname] = figs
    empties = {n: f'<figure data-room="{ROOMS[n]["tag"]}"><button type="button" class="plan" data-cap="{n} · {ROOMS[n]["dims"]}">{svg(n, None, n + " floor plan")}</button><figcaption><span class="tag tag-{ROOMS[n]["tag"].lower()}">{n}</span>Floor plan. {ROOMS[n]["dims"]}</figcaption></figure>' for n in ORDER}
    return out, empties, report

if __name__ == '__main__':
    out, empties, report = build()
    for r in report: print(r)
    json.dump({'setups': out, 'empties': empties}, open('plans.json', 'w'))
