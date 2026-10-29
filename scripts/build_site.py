"""Rebuild the whole site: redraw every floor plan, then write ../index.html and ../checklist.html.

Run it from anywhere with Python 3 (nothing else to install):

    python3 scripts/build_site.py

It takes a minute or two, because every layout is checked against the walls, doors and columns.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def run(script):
    print('running', script)
    subprocess.run([sys.executable, script], cwd=HERE, check=True, stdout=subprocess.DEVNULL)

run('gen.py')         # standard setups  -> plans.json
run('gen_ideas.py')   # new idea setups  -> ideas.json
run('assemble.py')    # page body        -> index.html (in this folder)

# Turn the page body into a full web page at the top of the repo.
s = open(os.path.join(HERE, 'index.html'), encoding='utf-8').read()
i = s.index('<svg width="0" height="0"'); head, body = s[:i], s[i:]
reset = '<style>:root{color-scheme:light}html{-webkit-text-size-adjust:100%}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       + reset + head.strip() + '\n</head>\n<body>\n' + body.strip() + '\n</body>\n</html>\n')
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(doc)
print('wrote index.html')

run('checklist.py')   # printable checklist -> ../checklist.html
print('wrote checklist.html')

# Remove the in-between files.
for f in ('plans.json', 'ideas.json', 'index.html', 'preview.html', 'sheet.html'):
    p = os.path.join(HERE, f)
    if os.path.exists(p): os.remove(p)
print('done')
