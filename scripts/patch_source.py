#!/usr/bin/env python3
"""Apply a guarded, reversible-in-source portable data-directory patch to DUCE.

All user-facing settings and log files that call get_user_data_path()
are redirected to the portable Data folder. Other relative paths are contained
by the launcher setting the program's working directory to Data.
"""
import argparse
import ast
import pathlib
import re
import sys

REPLACEMENT = '''def get_user_data_path(filename):
    """Keep DUCE state in the portable Data folder, not beside App binaries."""
    portable_dir = os.environ.get("DUCE_PORTABLE_DATA_DIR")
    if portable_dir:
        data_dir = os.path.abspath(portable_dir)
    elif getattr(sys, "frozen", False):
        # Safe fallback when the inner EXE is launched instead of the wrapper.
        data_dir = os.path.join(os.path.dirname(sys.executable), "Data")
    else:
        data_dir = os.path.join(os.path.abspath("."), "Data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, filename)
'''


def patch(path: pathlib.Path):
    src = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(src)
    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "get_user_data_path"]
    if len(funcs) != 1:
        raise ValueError("Expected exactly one get_user_data_path function; upstream layout changed.")
    node = funcs[0]
    lines = src.splitlines(keepends=True)
    old = "".join(lines[node.lineno-1:node.end_lineno])
    if 'DUCE_PORTABLE_DATA_DIR' in old:
        raise ValueError("Source is already patched or has unexpected upstream changes.")
    if 'sys.executable' not in old or 'filename' not in old or 'os.path.join' not in old:
        raise ValueError("Upstream get_user_data_path implementation changed; review it before patching.")
    if src.count('get_user_data_path(') < 3:
        raise ValueError("Too few state-file callers found; inspect the changed upstream source.")
    lines[node.lineno-1:node.end_lineno] = [REPLACEMENT + "\n"]
    patched = "".join(lines)
    ast.parse(patched)
    if patched.count('DUCE_PORTABLE_DATA_DIR') != 1:
        raise AssertionError("Unexpected patch content.")
    path.write_text(patched, encoding="utf-8", newline="\n")
    print(f"[PASS] Patched state paths: {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", type=pathlib.Path)
    ns = ap.parse_args()
    patch(ns.file)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f"[FAIL] Refusing to package a potentially nonportable build: {exc}", file=sys.stderr)
        sys.exit(1)
