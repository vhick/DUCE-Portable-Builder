#!/usr/bin/env python3
"""Conservative source checks: stop when new direct host-state writes appear."""
from pathlib import Path
import ast
import re
import sys

base = Path(sys.argv[1] if len(sys.argv)>1 else 'upstream')
checks = ['base.py', 'gui.py', 'cli.py']
for fn in checks:
    p = base / fn
    if not p.exists(): raise SystemExit('Missing upstream file: ' + str(p))
    data = p.read_text(encoding='utf-8')
    ast.parse(data)
    if fn == 'base.py':
        for expected in ('DUCE_PORTABLE_DATA_DIR', 'get_user_data_path("duce.log")',
                         'get_user_data_path(f"duce-{self.interface}-settings.json")'):
            if expected not in data:
                raise SystemExit('Required patch/data access missing: ' + expected)
    # Direct host AppData writes need review. Cookie-reading via rookiepy is intentionally allowed.
    suspicious = re.compile(r'(?i)(?:os\.environ\[(?:\"|\')(?:(?:local)?appdata|programdata)|os\.getenv\((?:\"|\')(?:(?:local)?appdata|programdata)|expanduser\(|Path\.home\()')
    if suspicious.search(data):
        raise SystemExit(f'Unexpected host-specific path usage in {fn}; inspect source before releasing')
print('[PASS] Portable patch, syntax, known output paths and host-state scan')
