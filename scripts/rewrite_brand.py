"""Rewrite rendered publication branding without touching the current GitHub Pages base path."""
import json,re
from pathlib import Path
from site_config import ROOT

brand=json.loads((ROOT/'data/brand.json').read_text(encoding='utf-8'))
new=brand['name']
old=brand.get('previousName') or 'Folvella'
# Replace the visible/editorial brand name while preserving /Folvella/ in the temporary GitHub Pages URL.
pattern=re.compile(r'(?<!/)'+re.escape(old)+r'(?!/)')
extensions={'.html','.xml','.txt'}
changed=0
for path in ROOT.rglob('*'):
    if not path.is_file() or path.suffix.lower() not in extensions:
        continue
    try:
        text=path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        continue
    updated=pattern.sub(new,text)
    if updated!=text:
        path.write_text(updated,encoding='utf-8')
        changed+=1
print(f'Rebranded {changed} rendered files: {old} -> {new}')
