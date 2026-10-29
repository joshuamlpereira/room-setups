import json,re
d=json.load(open('plans.json')); P=d['setups']; E=d['empties']; I=json.load(open('ideas.json'))
# 2026-10-13: no banquet setup in the Double Meeting Room, Hickory or Sycamore
NO_BANQUET=('Double Meeting Room','Hickory','Sycamore')
P['Banquet']=[f for f in P['Banquet'] if not any(f'">{n}</span>' in f for n in NO_BANQUET)]
# 2026-10-13: no Full Oak lecture
P['Lecture']=[f for f in P['Lecture'] if '">Full Oak</span>' not in f]
P['Panel']=[f for f in P['Panel'] if '">Full Oak</span>' not in f]
for k in ('Classroom','Classroom V'): P[k]=[f for f in P[k] if '">Full Oak</span>' not in f]
P['U-Shape']=[f for f in P['U-Shape'] if '">Full Oak</span>' not in f and '">Sycamore</span>' not in f]
P['Horseshoe']=[f for f in P['Horseshoe'] if '">Full Oak</span>' not in f]
P['Pod']=[f for f in P['Pod'] if not any(f'">{n}</span>' in f for n in ('Full Oak','Hickory','Sycamore'))]
P['Boardroom']=[f for f in P['Boardroom'] if '">Full Oak</span>' not in f]
P['Cabaret']=[f for f in P['Cabaret'] if not any(f'">{n}</span>' in f for n in ('Full Oak','Hickory','Sycamore'))]
P['Exam']=[f for f in P['Exam'] if not any(f'">{n}</span>' in f for n in ('Hickory','Sycamore'))]
I['Center Floor']=[f for f in I['Center Floor'] if not any(f'">{n}</span>' in f for n in ('Maple','Oak'))]
I['Workshop Stations']=[f for f in I['Workshop Stations'] if '">Full Oak</span>' not in f]
s=open('index_base.html').read()
s,nph=re.subn(r'<figure data-room="[^"]*"><button type="button" class="shot".*?</figure>','',s,flags=re.S); print('photos removed',nph)
assert 'class="shot"' not in s and '<img src' not in s
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a[:60],s.count(a)); s=s.replace(a,b)
css='''
:root{--floor:#eef0f4;--wall:#0f1d3a;--glass:#1f9fd4;--table:#dcbb78;--table-edge:#9a7a3a;--chair:#5a6885;--chair-back:#1f2a44;--seatbank:#3d5486;--food:#f3e6c4;--mark:#dde6f7;--tv:#7b3fb3;--screen:#e0662f;--board:#18a07a}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){--floor:#1c2945;--wall:#dfe6f5;--glass:#5cc8f0;--table:#c9a55c;--table-edge:#7d6226;--chair:#93a2c4;--chair-back:#e8edf8;--seatbank:#5873ad;--food:#8a7a52;--mark:#283a61;--tv:#c8a2ee;--screen:#f39a6b;--board:#5fd3ad} }
:root[data-theme="dark"]{--floor:#1c2945;--wall:#dfe6f5;--glass:#5cc8f0;--table:#c9a55c;--table-edge:#7d6226;--chair:#93a2c4;--chair-back:#e8edf8;--seatbank:#5873ad;--food:#8a7a52;--mark:#283a61;--tv:#c8a2ee;--screen:#f39a6b;--board:#5fd3ad}
h4{font:600 .78rem var(--display);text-transform:uppercase;letter-spacing:.09em;color:var(--muted);margin:6px 0 0}
.plans{grid-template-columns:repeat(auto-fill,minmax(250px,1fr))}
.plan{display:block;position:relative;width:100%;padding:0;border:1px solid var(--line);background:var(--surface);border-radius:6px;cursor:zoom-in;aspect-ratio:4/3}
.plan:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
svg .fl{fill:var(--floor)} svg .wl{fill:none;stroke:var(--wall);stroke-width:calc(var(--sw)*1.5);stroke-linejoin:round;stroke-linecap:round}
.plan svg{position:absolute;left:8px;top:8px;width:calc(100% - 16px);height:calc(100% - 16px)}
#lb-svg svg{width:100%;height:100%;display:block}
svg .gl{fill:none;stroke:var(--glass);stroke-width:calc(var(--sw)*2.4)} svg .dr{stroke:var(--gold);stroke-width:calc(var(--sw)*2.8)}
svg .dv{stroke:var(--muted);stroke-width:calc(var(--sw)*1.8)} svg .dv.open{stroke-dasharray:1.2 1.2;opacity:.55}
svg .tb{fill:var(--table);stroke:var(--table-edge);stroke-width:.14px} svg .bl{fill:var(--seatbank)} svg .bll{stroke:var(--floor);stroke-width:.18px}
svg .scl{stroke:var(--screen);stroke-width:calc(var(--sw)*3.4)} svg .tvl{stroke:var(--tv);stroke-width:calc(var(--sw)*3.4)} svg .wbl{stroke:var(--board);stroke-width:calc(var(--sw)*3.4)} svg .mk{fill:var(--mark);stroke:var(--muted);stroke-width:.2px;stroke-dasharray:1 .8} svg .ct{fill:var(--line)} svg .st{fill:var(--line);opacity:.8} svg .fd{fill:var(--food);stroke:var(--table-edge)} svg .col{fill:var(--wall)} svg .sb{fill:none;stroke:var(--muted);stroke-width:.22px}
svg .lb{font:500 var(--fs) var(--body);fill:var(--muted)} svg .lb.big{font:700 calc(var(--fs)*1.6) var(--display);fill:var(--ink)}
.cs{fill:var(--chair)} .cb{fill:var(--chair-back)}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.88rem;color:var(--muted);padding:0;margin:0;list-style:none}
.legend li{display:flex;align-items:center;gap:7px}
.legend i{display:inline-block;width:22px;height:0;border-top:4px solid var(--wall)}
.legend i.g{border-color:var(--glass)} .legend i.d{border-color:var(--gold)} .legend i.m{border-color:var(--muted)}
.legend i.t{height:10px;border:1px solid var(--table-edge);background:var(--table);border-radius:2px} .legend i.sc{border-color:var(--screen)} .legend i.tv{border-color:var(--tv)} .legend i.wb{border-color:var(--board)} .legend i.t.f{background:var(--food)} .legend i.t.o{background:var(--mark);border:1px dashed var(--muted)} .legend i.c{width:10px;height:10px;border:0;background:var(--chair);border-radius:3px}
#lb-svg{background:var(--surface);border-radius:6px;padding:10px;width:min(92vw,1100px);height:min(78vh,820px)}
</style>'''
rep('</style>',css)
rep('<div class="wrap">','<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><g id="chr"><rect class="cs" x="-.7" y="-.7" width="1.4" height="1.4" rx=".35"/><rect class="cb" x="-.7" y=".42" width="1.4" height=".4" rx=".2"/></g></defs></svg>\n<div class="wrap">')
rep('Photos of each way we can arrange Maple, Oak and Willow.','Floor plans of each way we can arrange Maple, Oak and Willow, drawn to scale.')
rep('Tap any photo to see it larger.','Tap any floor plan to see it larger.')
# rooms
def into_grid(roomcard,figs):
    global s
    i=s.index(f'data-roomcard="{roomcard}"'); g=s.index('<div class="grid">',i)
    assert s[g:g+len('<div class="grid"></div>')]=='<div class="grid"></div>'
    s=s[:g]+'<div class="grid plans">'+figs+'</div>'+s[g+len('<div class="grid"></div>'):]
into_grid('Maple',E['Maple']); into_grid('Willow',E['Willow']); into_grid('Oak',''.join(E[n] for n in ['Full Oak','Oak','Double Meeting Room','Hickory','Sycamore']))
s=re.sub(r'<div class="split".*?</span></div></div>','',s,count=1,flags=re.S); assert 'class="split"' not in s
rep('<p>2,027 sq ft. Windows on two sides, checkered floor, TV.</p>','<p>2,027 sq ft. Curved wall of windows, TV, and a storage area past the TV wall that is not used for seating.</p>')
rep('Each round seats up to 8.</p>','Each round seats up to 8. Food goes on 6 ft tables along the left wall in Maple, under the whiteboard in Oak, along the west wall in Full Oak, and on the counter in Willow.</p>')
# setups
lead='<p class="lead">Each photo is tagged with the room it was taken in. Most setups can be built in any room as long as the group fits.</p>'
rep(lead,'''<p class="lead">The floor plans are drawn to scale from the building floor plan, with 6 ft long tables and 5 ft round tables. Table and chair counts stay within our capacity sheet. Treat them as a starting point and confirm the final count with us.</p>
<ul class="legend"><li><i></i>Wall</li><li><i class="g"></i>Windows</li><li><i class="d"></i>Door</li><li><i class="m"></i>Moving wall</li><li><i class="t"></i>Table</li><li><i class="t f"></i>Food table</li><li><i class="c"></i>Chair</li></ul>''')
def plans_html(name):
    h='<div class="grid plans">'+''.join(P[name])+'</div>'
    # 2026-10-13: V shape classroom dropped
    return h
for name in ['Banquet','Lecture','Panel','Job Fair','Classroom','Conference','Square','U-Shape','Horseshoe','Pod','Theatre Seating']:
    i=s.index(f'<h3>{name}</h3>'); j=s.index('</article>',i)
    assert s[j-len('<div class="grid"></div>'):j]=='<div class="grid"></div>'
    s=s[:j-len('<div class="grid"></div>')]+plans_html(name)+s[j:]
    a=s.rfind('<article class="setup" data-rooms="',0,i); b=s.index('"',a+len('<article class="setup" data-rooms="'))
    s=s[:a]+'<article class="setup" data-rooms="'+('Oak' if name=='Theatre Seating' else 'Maple Oak Willow')+s[b:]
new=[('Boardroom','Long tables pushed together into one big table with chairs on all sides.','Board meetings and small group discussions.'),
     ('Cabaret','Round tables with chairs on the side away from the speaker, all turned toward one focal point: the speaker table. Food tables go along a side wall.','Dinners with a speaker, trivia nights, award shows.'),
     ('Exam','Single tables in rows with one chair each, spaced apart.','Tests and quiet individual work.')]
arts=''.join(f'<article class="setup" data-rooms="Maple Oak Willow"><header><h3>{n}</h3><p>{d}</p><p class="use"><b>Good for</b> {u}</p></header>{plans_html(n)}</article>' for n,d,u in new)
k=s.index('<p class="none" id="willow-note"'); k2=s.rfind('</section>',0,k); s=s[:k2]+arts+s[k2:]
s=re.sub(r'<p class="none" id="willow-note".*?</p>\n','',s,count=1,flags=re.S)
s=re.sub(r'<section id="more">.*?</section>\n','',s,count=1,flags=re.S); assert 'id="more"' not in s
rep('805 sq ft. Carpet floor, counter with sink, whiteboard.','805 sq ft. Carpet floor, counter with sink, and a TV on the long wall that people face. There is no whiteboard on the wall; a small rolling whiteboard is kept in storage.')
rep('<h3>Classroom</h3><p>Rows of long tables with chairs on one side, all facing the front. In a V shape the rows are angled toward the middle so everyone can see the front.','<h3>Classroom</h3><p>Rows of long tables with chairs on one side, all facing the front, plus a table and chair for the teacher.')
# new ideas
ideas=[('Center Floor','Round tables set around an open floor in the middle, so every table has a view of it.','Dances, performances, award nights, cultural shows.'),
 ('Long Table Dinner','Long tables pushed end to end in long rows, with chairs on both sides.','Family style meals, team dinners, potlucks, speed networking.'),
 ('Workshop Stations','Islands made of two long tables, six chairs each, with a presenter table at the front. Groups can rotate from island to island.','Hands on workshops, craft nights, training with breakout tasks.'),
]
# archived 2026-10-13: restore by adding this line back
#('Mixer','Round tables with no chairs for standing and talking, food tables along one wall, and a short row of chairs along the other.','Receptions, networking events, socials, meet and greets.')]
def rooms_of(figs):
    r=[]
    for m in re.findall(r'<figure data-room="([^"]+)"',''.join(figs)):
        if m not in r: r.append(m)
    return ' '.join(r)
ih='<section id="ideas"><h2>New ideas</h2><p class="lead">Extra arrangements we came up with using the same round tables, long tables and chairs. They are drawn to the same scale and stay within the same capacity limits.</p>'
ih+=''.join(f'<article class="setup" data-rooms="{rooms_of(I[n])}"><header><h3>{n}</h3><p>{d_}</p><p class="use"><b>Good for</b> {u}</p></header><div class="grid plans">{"".join(I[n])}</div></article>' for n,d_,u in ideas)+'</section>\n'
rep_s='<section id="sizes">'; assert s.count(rep_s)==1; s=s.replace(rep_s,ih+rep_s)
assert s.count("document.querySelectorAll('#setups figure')")==1; s=s.replace("document.querySelectorAll('#setups figure')","document.querySelectorAll('.setup figure')")
rep('<li><i class="t f"></i>Food table</li>','<li><i class="t f"></i>Food table</li><li><i class="t o"></i>Open floor</li><li><i class="tv"></i>TV</li><li><i class="sc"></i>Projector screen</li><li><i class="wb"></i>Whiteboard or chalkboard</li>')
# 2026-10-13: Square setup dropped
s,nsq=re.subn(r'<article class="setup"[^>]*><header><h3>Square</h3>.*?</article>','',s,count=1,flags=re.S); assert nsq==1
# js
rep("var note=document.getElementById('willow-note');",'')
rep("note.hidden=f!=='Willow';","document.querySelectorAll('#rooms figure').forEach(function(g){g.hidden=false});")
rep('<img id="lb-img" alt="">','<img id="lb-img" alt="" hidden><div id="lb-svg" hidden></div>')
rep("var lb=document.getElementById('lb'),im=document.getElementById('lb-img'),cap=document.getElementById('lb-cap');","var lb=document.getElementById('lb'),im=document.getElementById('lb-img'),sv=document.getElementById('lb-svg'),cap=document.getElementById('lb-cap');")
rep("var b=e.target.closest('.shot'); if(!b)return;","var p=e.target.closest('.plan'); if(p){sv.innerHTML=p.innerHTML;sv.hidden=false;im.hidden=true;cap.textContent=p.dataset.cap;if(lb.showModal)lb.showModal();return}\n    var b=e.target.closest('.shot'); if(!b)return; sv.hidden=true;im.hidden=false;")
open('index.html','w').write(s)
skel='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
open('preview.html','w').write(skel+s+'</body></html>')
# plans-only sheet for checking
m=re.search(r'<style>.*?</style>',s,re.S).group(0)
sheet=skel+m+'<svg width="0" height="0" style="position:absolute"><defs><g id="chr"><rect class="cs" x="-.7" y="-.7" width="1.4" height="1.4" rx=".35"/><rect class="cb" x="-.7" y=".42" width="1.4" height=".4" rx=".2"/></g></defs></svg>'
for n,figs in I.items(): sheet+=f'<h3 style="margin:10px">{n}</h3><div class="grid" style="grid-template-columns:repeat(4,1fr);padding:0 10px">'+''.join(figs)+'</div>'
sheet+='<h3>Rooms</h3><div class="grid" style="grid-template-columns:repeat(4,1fr);padding:0 10px">'+''.join(E.values())+'</div>'
open('sheet.html','w').write(sheet+'</body></html>')
print(len(s))
s=open('index.html').read()
for x,y in [('one block per setup with its photos','one block per setup with its floor plans'),('aria-label="Show photos by room"','aria-label="Show floor plans by room"'),('aria-label="Larger photo"','aria-label="Larger floor plan"')]:
    assert s.count(x)==1; s=s.replace(x,y)
open('index.html','w').write(s)
s=open('index.html').read()
x='<tr><th>Willow</th><td>Ask</td>'; assert s.count(x)==1; s=s.replace(x,'<tr><th>Willow</th><td>5</td>')
open('index.html','w').write(s)
