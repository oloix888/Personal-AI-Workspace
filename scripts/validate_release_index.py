#!/usr/bin/env python3
import glob,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'release-index.json').read_text())
assert data['releases'], 'No releases'
parts=sorted(glob.glob(str(root/data['source_parts_glob'])))
assert parts, 'Missing creator source parts'
for p in data['patches']:
    assert (root/p['path']).is_file(), f"Missing patch {p['path']}"
versions=[r['version'] for r in data['releases']]
assert len(versions)==len(set(versions)), 'Duplicate versions'
assert data['latest']==versions[-1], 'Latest must be final release entry'
for r in data['releases']:
    assert (root/r['notes_file']).is_file(), f"Missing notes {r['notes_file']}"
    if (root/'build').exists(): assert (root/r['asset']).is_file(), f"Missing generated asset {r['asset']}"
print(f'Validated {len(versions)} releases and {len(parts)} source parts; latest v{data["latest"]}')
