#!/usr/bin/env python3
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
required=['README.md','LICENSE','NOTICE','AUTHORS.md','ATTRIBUTION.md','CHANGELOG.md','CONTRIBUTING.md','CODE_OF_CONDUCT.md','SECURITY.md','docs/index.html','docs/styles.css','docs/app.js','release-index.json']
for f in required: assert (root/f).is_file(), f'Missing {f}'
text=(root/'docs/index.html').read_text()
for token in ['Personal AI Workspace','v1.5.1','Michał Poliński','Emma ✨','Apache-2.0']: assert token in text, token
assert 'lang="en"' in text
assert '#fff' in (root/'docs/styles.css').read_text().lower()
print('Repository structure and public site validated')
