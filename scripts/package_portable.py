#!/usr/bin/env python3
"""Stage the actual DUCE Windows PortableApps-style distribution."""
import argparse
import configparser
import os
from pathlib import Path
import re
import shutil
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def package(source: Path, dist: Path, stage: Path):
    gui = dist / 'DUCE-GUI'
    cli = dist / 'DUCE-CLI'
    for folder, filename in [(gui, 'DUCE-GUI.exe'), (cli, 'DUCE-CLI.exe')]:
        if not (folder / filename).is_file():
            raise FileNotFoundError(f'Missing PyInstaller output: {folder / filename}')
        if not (folder / '_internal').is_dir():
            raise FileNotFoundError(f'Incomplete onedir output (no _internal): {folder}')
    src = (source / 'base.py').read_text(encoding='utf-8')
    if 'DUCE_PORTABLE_DATA_DIR' not in src:
        raise ValueError('Portable-path source patch not found')
    m = re.search(r'^VERSION\s*=\s*[\'"]v?(\d+(?:\.\d+){1,3})[\'"]', src, re.M)
    if not m:
        raise ValueError('Unknown upstream VERSION; cannot label package accurately')
    version = m.group(1)
    parts = version.split('.')
    package_version = '.'.join((parts + ['0'] * (4-len(parts)))[:4])
    target = stage / 'DUCEPortable'
    if target.exists():
        shutil.rmtree(target)
    (target / 'App' / 'DUCE').mkdir(parents=True)
    shutil.copytree(gui, target / 'App' / 'DUCE' / 'GUI')
    shutil.copytree(cli, target / 'App' / 'DUCE' / 'CLI')
    (target / 'App' / 'AppInfo').mkdir(parents=True)
    (target / 'Data').mkdir()
    (target / 'Data' / 'README - your settings live here.txt').write_text(
        'DUCE Portable settings, logs, exported courses, cache and scratch files stay here.\n'
        'When updating, NEVER delete or overwrite this Data folder.\n'
        'Warning: GUI settings can contain saved Udemy credentials. Protect this drive.\n', encoding='utf-8'
    )
    (target / 'Other' / 'Source').mkdir(parents=True)
    (target / 'Other' / 'Help').mkdir(parents=True)
    (target / 'Other' / 'Help' / 'USER-GUIDE.txt').write_text(
        'DUCE PORTABLE\n\n'
        'Start: DUCEPortable.exe (at the top of this folder).\n'
        'Command-line: DUCEPortable-CLI.cmd or DUCEPortable.exe --cli.\n'
        'All settings and exports should live in Data.\n'
        'Auto-login reads cookies from the browser installed on this PC; this is an intentional exception.\n'
        'If you move the program, you may need to sign in to Udemy again.\n'
        'Upgrade by replacing App, AppInfo, Other and the launchers only. Preserve Data.\n'
        'Do not store the folder on a shared or untrusted drive if you save Udemy credentials.\n', encoding='utf-8'
    )
    (target / 'Other' / 'Source' / 'PORTABLE-PATCH-README.txt').write_text(
        'Source: https://github.com/techtanic/Discounted-Udemy-Course-Enroller\n'
        'License: AGPL-3.0; see the upstream LICENSE in the adjacent patched source.\n'
        'Modification: get_user_data_path() in base.py redirects settings/duce.log to Data.\n'
        'Launcher sets working directory to Data for relative output (Courses, debug, logs).\n'
        'Build scripts and the launcher source are in this builder repository.\n'
        'Package includes the patched upstream source snapshot.\n', encoding='utf-8'
    )
    shutil.copytree(
        source,
        target / 'Other' / 'Source' / 'Discounted-Udemy-Course-Enroller',
        ignore=shutil.ignore_patterns('.git', '.github', '__pycache__', '*.pyc', 'dist', 'build', '*.spec', '.venv')
    )
    shutil.copy(ROOT / 'launcher' / 'DUCEPortable.cs', target / 'Other' / 'Source' / 'DUCEPortable.cs')
    shutil.copy(ROOT / 'scripts' / 'patch_source.py', target / 'Other' / 'Source' / 'patch_source.py')
    logo = source / 'extra' / 'DUCE-LOGO.ico'
    if not logo.is_file() or logo.read_bytes()[:4] != b'\x00\x00\x01\x00':
        raise ValueError('Missing/invalid original upstream DUCE-LOGO.ico: no generic icon substitution')
    icon_folder = target / 'App' / 'AppInfo'
    shutil.copy2(logo, icon_folder / 'appicon.ico')
    with Image.open(logo) as ico:
        srcicon = ico.convert('RGBA')
    for size, filename in [(128, 'appicon.png'), (32, 'appicon_32.png'), (16, 'appicon_16.png')]:
        srcicon.resize((size, size), Image.Resampling.LANCZOS).save(icon_folder / filename)

    appinfo = f'''[Format]
Type=PortableAppsFormat
Version=3.9

[Details]
Name=Discounted Udemy Course Enroller Portable
AppID=DUCEPortable
Publisher=techtanic (upstream); independent portable build
Homepage=https://github.com/techtanic/Discounted-Udemy-Course-Enroller
Category=Education
Description=Automatically find and enroll in eligible fully discounted Udemy courses.
Language=Multilingual

[License]
Shareable=true
OpenSource=true
Freeware=true
CommercialUse=true

[Version]
PackageVersion={package_version}
DisplayVersion={version} Portable

[Control]
Icons=1
Start=DUCEPortable.exe
'''
    (icon_folder / 'appinfo.ini').write_text(appinfo, encoding='utf-8')
    (target / 'DUCEPortable-CLI.cmd').write_text('''@echo off
setlocal
set "DUCE_PORTABLE_DATA_DIR=%~dp0Data"
if not exist "%DUCE_PORTABLE_DATA_DIR%" mkdir "%DUCE_PORTABLE_DATA_DIR%"
if not exist "%DUCE_PORTABLE_DATA_DIR%\\Temp" mkdir "%DUCE_PORTABLE_DATA_DIR%\\Temp"
if not exist "%DUCE_PORTABLE_DATA_DIR%\\Cache" mkdir "%DUCE_PORTABLE_DATA_DIR%\\Cache"
set "TEMP=%DUCE_PORTABLE_DATA_DIR%\\Temp"
set "TMP=%DUCE_PORTABLE_DATA_DIR%\\Temp"
set "XDG_CACHE_HOME=%DUCE_PORTABLE_DATA_DIR%\\Cache"
set "PYTHONNOUSERSITE=1"
cd /d "%DUCE_PORTABLE_DATA_DIR%"
"%~dp0App\\DUCE\\CLI\\DUCE-CLI.exe" %*
endlocal
''', encoding='utf-8', newline='\r\n')
    (stage / 'release-name.txt').write_text(f'DUCEPortable_v{version}_Windows_x64.zip', encoding='utf-8')
    (stage / 'upstream-version.txt').write_text(version, encoding='utf-8')
    print(f'[PASS] Staged original-icon DUCE v{version} at {target}')
    print('[PASS] GUI + CLI onedir, correct AppInfo, full patched source, preservable Data')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('upstream'))
    ap.add_argument('--dist', type=Path, default=Path('dist'))
    ap.add_argument('--stage', type=Path, default=Path('stage'))
    ns = ap.parse_args()
    try:
        package(ns.source, ns.dist, ns.stage)
    except Exception as e:
        print(f'[FAIL] Packaging stopped: {e}', file=sys.stderr)
        sys.exit(1)
