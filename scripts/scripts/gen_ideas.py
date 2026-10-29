import math, json, sys
from gen import *
import gen

BOTH = [(-1.5, 2.25, 0), (1.5, 2.25, 0), (-1.5, -2.25, 180), (1.5, -2.25, 180)]

def add_round(l, u, v, n=8, cab=False, chairs=True):
    x, y = l._w(u, v); l.rounds.append((x, y))
    if not chairs: return
    ts = (-100, -50, 0, 50, 100) if cab else [360 * k / n + (0 if n % 2 else 180 / n) for k in range(n)]
    for t in ts:
        cx, cy = l._w(u + 3.5 * math.sin(math.radians(t)), v + 3.5 * math.cos(math.radians(t)))
        l.chairs.append((cx, cy, facing(cx, cy, x, y)))

def food(l, u, v, a):
    x, y = l._w(u, v)
    if not hasattr(l, 'food'): l.food = []
    l.food.append((x, y, a + l.th))

def mark_rect(l, u0, v0, u1, v1, label):
    (xa, ya), (xb, yb) = l._w(u0, v0), l._w(u1, v1)
    l.marks = getattr(l, 'marks', []) + [('rect', min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb), label)]

def maple_food(l):
    ss = [7.8 + 6 * i for i in range(4)]
    l.food = [(*wallpt(s_, 1.65), WA) for s_ in ss]
    l.xlabels = [(*wallpt(16.8, -2.0), 'Food tables', WA)]

# 1. Center Floor: rounds around an open floor
def centerfloor(room, name):
    l = L(room); W, D = l.W, l.D; cap = room['caps']['rounds']
    if name == 'Maple':
        for rad, t0, t1, n in ((40.0, -46, 13, 5), (30.0, -44, 14, 4)):
            for i in range(n):
                t = math.radians(t0 + (t1 - t0) * i / (n - 1))
                x, y = C[0] + rad * math.sin(t), C[1] - rad * math.cos(t)
                assert clear(room, (x, y), 4.25), (x, y)
                l.rounds.append((x, y))
                for k in range(8):
                    a = math.radians(45 * k + 22.5); cx, cy = x + 3.5 * math.sin(a), y + 3.5 * math.cos(a)
                    l.chairs.append((cx, cy, facing(cx, cy, x, y)))
        l.marks = [('circle', 40.6, 31.0, 7.6, 'Open floor')]
        maple_food(l); return l
    if name == 'Full Oak':   # open floor in the Double Meeting Room half, tables fill Oak, food under the whiteboard
        food = [(16.15 + 6 * i, 34.55, 0) for i in range(3)]
        r2 = dict(room, obst=room.get('obst', []) + [(-27, -1, -0.5, 36)],
                  segobst=[((x - 3, y), (x + 3, y), 1.25 + 2.5) for x, y, a in food])
        l = gen.rounds(r2); l.room = room
        l.food = food
        l.marks = [('rect', -24.0, 2.0, -3.0, 25.0, 'Open floor')]
        return l
    if W < 27 or D < 17: return None
    nb = int((W - 8.6) / 9.2 + 1e-6) + 1; us = [4.3 + (W - 8.6) * i / (nb - 1) for i in range(nb)]
    ns = int((D - 8.6) / 9.2 + 1e-6) + 1
    if ns < 2: return None   # no room for tables along the sides
    vs = [D - 4.3 - (D - 8.6) * j / (ns - 1) for j in range(ns)]
    pos = [(u, D - 4.3) for u in us] + [(uu, v) for v in vs[1:] for uu in (4.3, W - 4.3)]
    for u, v in pos[:cap]: add_round(l, u, v)
    mark_rect(l, 9.8, 1.0, W - 9.8, D - 9.8, 'Open floor')
    return l

# 2. Long Table Dinner: long rows, chairs on both sides
def longdinner(room, name, kmax=6, rp=9):
    l = L(room); W, D = l.W, l.D; caps = room['caps']
    along_v = D >= W; Lg, Sh = (D, W) if along_v else (W, D)
    if Sh < 6.5: return None
    k = min(int((Lg - 3) / 6), kmax); n = int((Sh - 6.5) / 9) + 1
    while n * k > caps['longs'] or 4 * n * k > caps['seats']:
        if n > 2 and k <= 6: n -= 1
        elif k > 3: k -= 1
        elif n > 1: n -= 1
        elif k > 1: k -= 1
        else: return None
    if k < 2: return None
    for i in range(n):
        for j in range(k):
            ac = rp * (i - (n - 1) / 2); al = 6 * (j - (k - 1) / 2)
            if along_v: l.long(W / 2 + ac, D / 2 + al, 90, BOTH)
            else: l.long(W / 2 + al, D / 2 + ac, 0, BOTH)
    return l

def ltd(room, name):   # Long Table Dinner with food tables
    BAY = [(16.15 + 6 * i, 34.55, 0) for i in range(3)]   # under the Oak whiteboard
    if name == 'Maple':
        l = longdinner(room, name)
        if l: maple_food(l)
        return l
    if name == 'Willow':
        l = longdinner(room, name)
        if l: l.note = 'food on the counter'
        return l
    if name == 'Oak':
        l = longdinner(room, name)
        if l: l.food = list(BAY)
        return l
    if name == 'Full Oak':   # rows run the full width of Oak and the Double Meeting Room
        l = longdinner(dict(room, usezone=room['zone2']), name, kmax=10, rp=12)
        if l: l.food = list(BAY); l.room = room
        return l
    if name == 'Double Meeting Room':   # food on the west wall, rows to the east of it
        l = longdinner(dict(room, usezone=None, zone=(-21, 0.6, -1.2, 26.3)), name)
        if l: l.food = [(-25.05, 4.2 + 6 * i, 90) for i in range(4)]; l.room = room
        return l
    if name == 'Hickory':   # straight east-west rows; food along the slanted south wall
        l = longdinner(dict(room, zframe=None, usezone=None, zone=(-25.5, 15.1, -1.2, 25.0), front='N'), name)
        if l:   # food along the slanted south wall
            l.food = [(gen.slpt(s_)[0] + 0.3857 * 1.65, gen.slpt(s_)[1] - 0.9226 * 1.65, 22.7) for s_ in (6.6, 12.6)]; l.room = room
        return l
    if name == 'Sycamore':   # food along the north wall (west part), rows below it
        l = longdinner(dict(room, usezone=None, zone=(-25.5, 4.5, -1.2, 12.8)), name)
        if l: l.food = [(-22.5, 1.05, 0), (-16.5, 1.05, 0)]; l.room = room
        return l
    return longdinner(room, name)

# 3. Talk and Tables: chairs in front, rounds behind
def talktables(room, name):
    l = L(room); W, D = l.W, l.D; caps = room['caps']
    if W < 16: return None
    p = 1.9; n = min(8, int(((W - 4) / 2) / p), max(1, (caps['seats'] - 10) // 4))
    us = [W / 2 - 2 - p * (i + .5) for i in range(n)] + [W / 2 + 2 + p * (i + .5) for i in range(n)]
    for r in range(2):
        for u in us: l.chair(u, 7 + 3.2 * r, 0)
    vr = 7 + 3.2 + 0.8 + 2.2 + 4.3; nr = int((W - 8.6) / 9.6 + 1e-6) + 1; placed = 0
    while vr + 4.3 <= D + 0.01:
        m = nr
        while m > 0:   # use fewer tables in a row if one would hit a wall or column
            t = L(room)
            for i in range(m): add_round(t, W / 2 + 9.6 * (i - (m - 1) / 2), vr, cab=True)
            if all(clear(room, (x, y), 0.8) for x, y, _ in t.chairs): break
            m -= 1
        for i in range(m):
            if placed >= caps['rounds'] or len(l.chairs) + 5 > caps['seats']: break
            add_round(l, W / 2 + 9.6 * (i - (m - 1) / 2), vr, cab=True); placed += 1
        vr += 9.6
    return l if placed else None

# 4. Runway: a line of tables down the middle, chairs facing it from both sides
def runway(room, name):
    l = L(room); W, D = l.W, l.D; caps = room['caps']
    along_v = D >= W * 0.8; Lg, Sh = (D, W) if along_v else (W, D)
    rows = 2 if Sh >= 17.5 else (1 if Sh >= 11.2 else 0)
    if not rows: return None
    k = min(5, int((Lg - 4) / 6), caps['longs'])
    if k < 2: return None
    n = int(k * 6 / 1.9)
    while rows * 2 * n > caps['seats']:
        if rows > 1: rows -= 1
        else: n -= 1
    for i in range(k):
        al = 6 * (i - (k - 1) / 2)
        if along_v: l.long(W / 2, D / 2 + al, 90)
        else: l.long(W / 2 + al, D / 2, 0)
    for side in (-1, 1):
        for r in range(rows):
            ac = side * (1.25 + 2.6 + 3.0 * r)
            for j in range(n):
                al = 1.9 * (j - (n - 1) / 2)
                if along_v: l.chair(W / 2 + ac, D / 2 + al, 90 if side < 0 else -90)
                else: l.chair(W / 2 + al, D / 2 + ac, 180 if side < 0 else 0)
    return l

# 5. Workshop Stations: islands of two tables, people rotate between them
def stations(room, name):
    l = L(room); W, D = l.W, l.D; caps = room['caps']
    v0 = 9.7
    nu = int((W - 9.5) / 12 + 1e-6) + 1 if W >= 9.5 else 0
    nv = int((D - v0 - 4.25) / 11 + 1e-6) + 1 if D >= v0 + 4.25 else 0
    if nu * nv < 2: return None
    for r in range(nv):
        for i in range(nu):
            if len(l.longs) + 2 > caps['longs'] - 1 or len(l.chairs) + 6 > caps['seats'] - 1: break
            u = W / 2 + 12 * (i - (nu - 1) / 2); v = v0 + 11 * r
            l.long(u, v - 1.25, 180, BACK2); l.long(u, v + 1.25, 0, BACK2)
            l.chair(u - 4.0, v, 90); l.chair(u + 4.0, v, -90)
    l.presenter(); return l

def stations_custom(room, name, pu=12, v0=9.7, rows=None, check=False):
    """rows: list of island counts per row (centered); check: drop islands that hit a wall."""
    l = L(room); W, D = l.W, l.D; caps = room['caps']
    if rows is None:
        nu = int((W - 9.5) / pu + 1e-6) + 1; nv = int((D - v0 - 4.25) / 11 + 1e-6) + 1; rows = [nu] * nv
    for r, nu in enumerate(rows):
        for i in range(nu):
            if len(l.longs) + 2 > caps['longs'] - 1 or len(l.chairs) + 6 > caps['seats'] - 1: break
            u = W / 2 + pu * (i - (nu - 1) / 2); v = v0 + 11 * r
            t = L(room)
            t.long(u, v - 1.25, 180, BACK2); t.long(u, v + 1.25, 0, BACK2)
            t.chair(u - 4.0, v, 90); t.chair(u + 4.0, v, -90)
            if check and not (all(clear(room, p, 0.3) for tb in t.longs for p in corners(*tb)) and all(clear(room, c[:2], 0.75) for c in t.chairs)):
                continue
            l.longs += t.longs; l.chairs += t.chairs
    l.presenter(); return l

def stations_entry(room, name):
    if name == 'Maple':   # face the TV wall; teacher table under the TV; fill the floor
        l = stations_custom(dict(room, usezone=None, zone=(6, 6, 55.5, 33), front='E'), name, pu=11, v0=11.0, check=True)
        x = stations_custom(dict(room, usezone=None, zone=(30.3, 30.5, 50.3, 42.3), front='E'), name, pu=11, v0=10.5, check=True)
        l.longs += x.longs[:-1]; l.chairs += x.chairs[:-1]   # one more island in the entry area (skip its extra teacher table)
        return l
    if name == 'Double Meeting Room':   # face south; teacher table at the south end; 3 islands
        return stations_custom(dict(room, usezone=None, zone=(-25.5, 0.6, -1.2, 26.3), front='S'), name, rows=[2, 1], check=True)
    return stations(room, name)

# 6. Fishbowl: small inner circle talks, outer circles listen
def fishbowl(room, name):
    l = L(room); W, D = l.W, l.D; cap = room['caps']['seats']
    Rmax = min(W, D) / 2 - 1.0
    if Rmax < 5.6: return None
    radii = [(2.6, 5), (min(7.5, Rmax), None)]
    if Rmax >= 10.5: radii.append((10.5, None))
    cx0, cy0 = l._w(W / 2, D / 2)
    for r, n in radii:
        n = n or int(2 * math.pi * r / 2.2)
        for k in range(n):
            t = 360 * k / n + (36 if r < 4 else 0)
            if r > 4 and min(abs(((t - a + 180) % 360) - 180) for a in (45, 135, 225, 315)) < math.degrees(1.5 / r): continue
            if len(l.chairs) >= cap: break
            x, y = l._w(W / 2 + r * math.sin(math.radians(t)), D / 2 + r * math.cos(math.radians(t)))
            l.chairs.append((x, y, facing(x, y, cx0, cy0)))
    return l

# 7. Mixer: standing round tables, food along one wall, a few chairs along the other
def mixer(room, name):
    l = L(room); W, D = l.W, l.D; cap = room['caps']['rounds']
    if W < 16 or D < 14: return None
    u0, u1 = (4.0 if name == 'Maple' else 8.5), W - 6.5
    pitch = 9.0
    while True:   # widen the spacing until the count is within the limit
        v = 4.0; r = 0; ptsl = []; rp = pitch * 0.87; nrow = int((D - 8) / rp + 1e-6) + 1
        v = D / 2 - rp * (nrow - 1) / 2
        for r in range(nrow):
            n = int((u1 - u0) / pitch + 1e-6) + 1 - (r % 2)
            ptsl += [((u0 + u1) / 2 + pitch * (i - (n - 1) / 2), v + rp * r) for i in range(max(n, 0))]
        if len(ptsl) <= cap or pitch > 30: break
        pitch += 0.5
    for u, vv in ptsl[:cap]: add_round(l, u, vv, chairs=False)
    if name == 'Maple': maple_food(l)
    elif name == 'Double Meeting Room':   # food along the north wall, chairs on the west wall between the two doors
        l.food = [(-22.5, 1.05, 0), (-16.5, 1.05, 0), (-10.5, 1.05, 0)]
        for yy in (10.85, 12.85, 14.85, 16.85): l.chairs.append((-25.5, yy, 90))
        l.roundword = 'standing round table'; return l
    else:
        nf = min(3, int((D - 4) / 6))
        for i in range(nf): food(l, 0.7, D / 2 + 6 * (i - (nf - 1) / 2), 90)
    nc = min(8, int(D * 0.6 / 2)); vc = D / 2
    if name in ('Full Oak', 'Double Meeting Room'):   # keep the chairs between the two west doors
        nc = 4; vc = (room.get('usezone') or room['zone'])[3] - 13.85
    if name == 'Willow':   # keep the storage doors on the far wall clear: chairs go along the windows
        for j in range(6): l.chair(W / 2 + 2 * (j - 2.5), D - 1.0, 0)
    else:
        for j in range(nc): l.chair(W - 1, vc + 2 * (j - (nc - 1) / 2), -90)
    l.roundword = 'standing round table'
    return l

IDEAS = [('Center Floor', centerfloor), ('Long Table Dinner', ltd), ('Talk and Tables', talktables), ('Runway', runway),
         ('Workshop Stations', stations_entry), ('Fishbowl', fishbowl), ('Mixer', mixer)]

def extra_check(l):
    bad = 0
    tabs = [(x, y, 2.5) for x, y in l.rounds]
    for x, y, a in l.chairs:
        for tx, ty, tr in tabs:
            if math.hypot(x - tx, y - ty) < tr + 0.6: bad += 1
    for i in range(len(l.rounds)):
        for j in range(i + 1, len(l.rounds)):
            if math.hypot(l.rounds[i][0] - l.rounds[j][0], l.rounds[i][1] - l.rounds[j][1]) < 6.5: bad += 1
    room = l.room
    for x, y, a in getattr(l, 'food', []):
        for p in corners(x, y, a):
            if not clear(room, p, 0.2): bad += 1
        for rx, ry in l.rounds:
            if math.hypot(rx - x, ry - y) < 2.5 + 3: bad += 1
    return bad

if __name__ == '__main__':
    out, _, report = build(IDEAS)
    for r in report: print(r)
    # extra checks
    for sname, fn in IDEAS:
        for name in ORDER:
            ROOMS[name]['usezone'] = ROOMS[name].get('zone2') if sname == 'Mixer' else None
            if ROOMS[name].get('only') and sname not in ROOMS[name]['only']: continue
            l = fn(ROOMS[name], name)
            if l and ROOMS[name].get('filt'): l = gen.filt(ROOMS[name], l)
            if l: 
                b = extra_check(l)
                if b: print('EXTRA BAD', sname, name, b)
    json.dump(out, open('ideas.json', 'w'))
