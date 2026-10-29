"""Build the printable setup checklist (../checklist.html) from the captions on the Room Setups page (../index.html).

Order inside each room: round table setups, then rectangle table setups (most chairs first),
then setups that are just chairs. The Oak rooms follow the divider order:
Full Oak, Oak divider, Oak, Double Meeting Room, Hickory/Sycamore divider, Sycamore, Hickory.
"""
import base64, datetime, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGE = os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'checklist.html')

# ---------- data: one entry per setup and room, read from the page captions ----------
data = {}
for cap_attr in re.findall(r'data-cap="([^"]*)"', open(PAGE, encoding='utf-8').read()):
    parts = html.unescape(cap_attr).split(' · ')
    if len(parts) != 3: continue          # empty room outlines, not setups
    setup, room, cap = parts
    def g(pat):
        m = re.search(r'(\d+) ' + pat, cap); return int(m.group(1)) if m else 0
    d = dict(setup=setup, rounds=g(r'round tables?'), longs=g(r'long tables?'), food=g(r'food tables?'),
             checkin=g(r'check-in tables?'), speaker=g(r'speaker tables?'), chairs=g(r'chairs'),
             fixed=g(r'fixed seats'), counter='food on the counter' in cap, cap=cap)
    d['rect'] = d['longs'] + d['food'] + d['checkin'] + d['speaker']
    data.setdefault(room, []).append(d)

CHAIR_SETUPS = {'Lecture', 'Panel', 'Pod', 'Horseshoe', 'Theatre Seating'}
GROUPS = ['round', 'rect', 'chairs']
LABEL = {'round': 'Rounds', 'rect': 'Rectangles', 'chairs': 'Chairs'}

def group(d):
    if d['rounds']: return 'round'
    if d['setup'] in CHAIR_SETUPS: return 'chairs'
    return 'rect'

def ordered(room):
    out = []
    for gname in GROUPS:
        its = [d for d in data[room] if group(d) == gname]
        # most chairs first; ties go to the setup with more tables
        its.sort(key=lambda d: (-d['chairs'], -(d['rect'] + d['rounds']), d['setup']))
        if its: out.append((gname, its))
    return out

def nsetups(room): return len(data[room])

# ---------- pieces ----------
ICON = {
    'round': '<svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="5.8" fill="currentColor"/></svg>',
    'rect': '<svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><rect x="1" y="5" width="14" height="6" rx="1.2" fill="currentColor"/></svg>',
    'chairs': '<svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><path d="M5 1.8V14.2M5 9H11.6V14.2" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}

def box(label):
    return f'<label class="box"><input type="checkbox" aria-label="{html.escape(label)}"><span></span></label>'

def num(v, sub=''):
    cls = 'v zero' if v == 0 else 'v'
    s = f'<td class="{cls}"><span class="big">{v}</span>'
    if sub: s += f'<small>{sub}</small>'
    return s + '</td>'

def rect_cell(d):
    note = rect_note(d)
    cls = 'v lv zero' if d['rect'] == 0 else 'v lv'
    return (f'<td class="{cls}"><div class="lvw"><span class="big">{d["rect"]}</span>'
            + (f'<small>{note}</small>' if note else '') + '</div></td>')

def rect_note(d):
    parts = []
    if d['food']: parts.append(f"{d['food']} food")
    if d['checkin']: parts.append(f"{d['checkin']} check-in")
    if d['speaker']: parts.append(f"{d['speaker']} speaker")
    if d['counter']: parts.append('food on the counter')
    return ', '.join(parts)

COLS = ('<colgroup><col class="c-rail"><col class="c-ck"><col class="c-n"><col class="c-name">'
        '<col class="c-r"><col class="c-l"><col class="c-ch"><col class="c-notes"></colgroup>')
THEAD = ('<thead><tr><th class="c-rail"></th><th>Done</th><th>#</th><th class="l">Setup</th>'
         '<th>Round<br>tables</th><th class="lv">Rectangle<br>tables</th><th>Chairs</th><th class="l">Notes</th></tr></thead>')

def table(room, rh, head=True):
    rows = []; i = 0
    for gname, its in ordered(room):
        body = []
        for k, d in enumerate(its):
            i += 1
            tds = ''
            if k == 0:
                fits = len(its) * rh >= 26 + 7.4 * len(LABEL[gname])   # room for the sideways label
                lab = f'<span class="rl">{LABEL[gname]}</span>' if fits else ''
                tds += f'<td class="rail" rowspan="{len(its)}" title="{LABEL[gname]}">{ICON[gname]}{lab}</td>'
            name = html.escape(d['setup'])
            sub = '<small>Pull out the bleachers</small>' if d['fixed'] else ''
            tds += f'<td class="ck">{box(room + " " + d["setup"])}</td><td class="n">{i}</td><td class="nm">{name}{sub}</td>'
            tds += num(d['rounds']) + rect_cell(d) + num(d['chairs'])
            tds += '<td class="notes"></td>'
            body.append(f'<tr>{tds}</tr>')
        rows.append(f'<tbody class="g-{gname}">' + ''.join(body) + '</tbody>')
    return f'<table class="list">{COLS}{THEAD if head else ""}{"".join(rows)}</table>'

KEY = ('<div class="key"><span class="lbl">Order</span>'
       f'<span class="chip k-round">{ICON["round"]}Rounds</span><span class="arr">&rarr;</span>'
       f'<span class="chip k-rect">{ICON["rect"]}Rectangles, most chairs first</span><span class="arr">&rarr;</span>'
       f'<span class="chip k-chairs">{ICON["chairs"]}Just chairs</span></div>')

FLOW = [('Full Oak', ''), ('Oak divider', 'wall'), ('Oak', ''), ('Double Meeting Room', ''),
        ('Hickory / Sycamore divider', 'wall'), ('Sycamore', ''), ('Hickory', '')]

def flow(on):
    lis = []
    for k, (t, c) in enumerate(FLOW, 1):
        cls = ' '.join(x for x in (c, 'on' if k in on else '') if x)
        lis.append(f'<li class="{cls}"><b>{k}</b>{html.escape(t)}</li>')
    return '<ol class="flow">' + ''.join(lis) + '</ol>'

def step(n, room, note):
    k = nsetups(room)
    return (f'<div class="step"><span class="sn">Step {n}</span><h2>{html.escape(room)}</h2>'
            f'<span class="sub">{note}{" · " if note else ""}{k} setups</span></div>')

def divider(n, text, sub):
    return (f'<div class="divider">{box("Step " + str(n))}<span class="sn">Step {n}</span>'
            f'<div><b>{text}</b><span>{sub}</span></div></div>')

MONTH = datetime.date.today().strftime('%b %Y')

def foot(p, total):
    return (f'<footer class="foot"><span>UToledo Student Recreation Center &middot; Reservations and Events</span>'
            f'<span>Counts match the Room Setups page, {MONTH}</span><span>Page {p} of {total}</span></footer>')

TOTAL = 4

def room_sheet(room, color, p, rh):
    return (f'<section class="sheet" style="--room:var(--{color});--rh:{rh}px">'
            f'<header class="head"><div><div class="kicker">Room setup checklist</div><h1>{room}</h1></div>'
            f'<div class="count"><b>{nsetups(room)}</b>setups</div></header>'
            '<p class="intro">Work from the top down and check off each setup when it is done. '
            'The layout for each one is on the Room Setups page.</p>'
            + KEY + table(room, rh) +
            '<div class="notebox"><span>Notes</span></div>' + foot(p, TOTAL) + '</section>')

RH3, RH4 = 26, 24   # row heights for the two Oak pages, so each fits on one sheet
oak_rooms = ['Full Oak', 'Oak', 'Double Meeting Room', 'Sycamore', 'Hickory']
oak_total = sum(nsetups(r) for r in oak_rooms)

oak1 = (f'<section class="sheet oak" style="--room:var(--oak);--rh:{RH3}px">'
        f'<header class="head"><div><div class="kicker">Room setup checklist</div><h1>Full Oak and its rooms</h1></div>'
        f'<div class="count"><b>{oak_total}</b>setups</div></header>'
        '<p class="intro">Start with Full Oak. Then set up the dividers and work through each smaller room in this order.</p>'
        + flow({1, 2, 3}) + KEY
        + step(1, 'Full Oak', 'All dividers open') + table('Full Oak', RH3)
        + divider(2, 'Set up the divider between Oak and the Double Meeting Room', 'Full Oak is now two rooms: Oak and the Double Meeting Room.')
        + step(3, 'Oak', 'Oak divider up') + table('Oak', RH3, head=False)
        + foot(3, TOTAL) + '</section>')

oak2 = (f'<section class="sheet oak" style="--room:var(--oak);--rh:{RH4}px">'
        '<header class="head slim"><div><div class="kicker">Room setup checklist</div><h1>Full Oak and its rooms, continued</h1></div>'
        '<div class="count">Steps 4 to 7</div></header>'
        + flow({4, 5, 6, 7})
        + step(4, 'Double Meeting Room', 'Oak divider up, Hickory and Sycamore divider still open') + table('Double Meeting Room', RH4)
        + divider(5, 'Set up the divider between Hickory and Sycamore', 'The Double Meeting Room is now two rooms: Sycamore and Hickory.')
        + step(6, 'Sycamore', '') + table('Sycamore', RH4, head=False)
        + step(7, 'Hickory', '') + table('Hickory', RH4, head=False)
        + foot(4, TOTAL) + '</section>')

sheets = room_sheet('Maple', 'maple', 1, 38) + room_sheet('Willow', 'willow', 2, 38) + oak1 + oak2

def face(fam, fname, extra):
    b = base64.b64encode(open(os.path.join(HERE, fname), 'rb').read()).decode()
    return (f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:100 900;{extra}font-display:block;"
            f"src:url(data:font/woff2;base64,{b}) format('woff2')}}")

FONTS = face('Archivo', 'archivo.woff2', 'font-stretch:62% 125%;') + '\n' + face('Public Sans', 'public-sans.woff2', '')
CSS = open(os.path.join(HERE, 'checklist.css'), encoding='utf-8').read()
JS = open(os.path.join(HERE, 'checklist.js'), encoding='utf-8').read()

doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>Room Setup Checklist</title>
<style>
{FONTS}
{CSS}
</style>
</head>
<body>
<div class="toolbar">
  <span class="tb-title">Room setup checklist</span>
  <span class="tb-hint">Prints on {TOTAL} letter pages. Turn off headers and footers in the print settings.</span>
  <button type="button" id="print">Print</button>
  <button type="button" id="clear" class="ghost">Clear checks</button>
</div>
<main>
{sheets}
</main>
<script>
{JS}
</script>
</body>
</html>
'''

if __name__ == '__main__':
    open(OUT, 'w', encoding='utf-8').write(doc)
    print(f'checklist.html: {sum(len(v) for v in data.values())} setups in {len(data)} rooms')
