#!/usr/bin/env python3
"""Validate staged PortableApps package before uploading; no GUI/network needed."""
import configparser
from pathlib import Path
import sys
import zipfile

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'stage/DUCEPortable')
required = [
    'DUCEPortable.exe', 'DUCEPortable-CLI.cmd',
    'App/DUCE/GUI/DUCE-GUI.exe', 'App/DUCE/CLI/DUCE-CLI.exe',
    'App/DUCE/GUI/_internal/default-duce-gui-settings.json',
    'App/DUCE/CLI/_internal/default-duce-cli-settings.json',
    'App/AppInfo/appinfo.ini', 'App/AppInfo/appicon.ico',
    'App/AppInfo/appicon.png', 'App/AppInfo/appicon_16.png',
    'App/AppInfo/appicon_32.png',
    'Data/README - your settings live here.txt',
    'Other/Source/Discounted-Udemy-Course-Enroller/base.py',
    'Other/Source/Discounted-Udemy-Course-Enroller/LICENSE',
]
missing = [f for f in required if not (root / f).is_file()]
if missing: raise SystemExit('Missing required packaged files:\n- ' + '\n- '.join(missing))
if (root / 'App/AppInfo/appicon.ico').read_bytes()[:4] != b'\x00\x00\x01\x00':
    raise SystemExit('Incorrect original icon')
info = configparser.ConfigParser(interpolation=None)
info.read(root / 'App/AppInfo/appinfo.ini', encoding='utf-8')
if info.get('Details', 'AppID') != 'DUCEPortable': raise SystemExit('Incorrect PortableApps AppID')
if info.get('Control', 'Start') != 'DUCEPortable.exe': raise SystemExit('Incorrect launcher name')
if 'DUCE_PORTABLE_DATA_DIR' not in (root / 'Other/Source/Discounted-Udemy-Course-Enroller/base.py').read_text(encoding='utf-8'):
    raise SystemExit('Wrong/unpatched source bundled')
for f in root.rglob('*'):
    if f.is_file() and f.name.startswith('duce-') and f.name.endswith('-settings.json') and 'Data' in f.parts:
        raise SystemExit('User settings unexpectedly bundled: ' + str(f))
print(f'[PASS] PortableApps metadata, original icons, onedir dependencies, patched source, empty Data at {root}')
