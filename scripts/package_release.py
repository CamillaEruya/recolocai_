#!/usr/bin/env python3
"""Gera um ZIP release do projeto, ignorando artefatos locais.

Uso: python scripts/package_release.py
"""
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'releases'
OUT_DIR.mkdir(exist_ok=True)
OUT_FILE = OUT_DIR / 'recoloca-ia-release.zip'

EXCLUDE = {
    '.git', '.venv', 'venv', '__pycache__', '.pytest_cache', 'database.db', 'releases'
}

def should_include(path: Path):
    for part in path.parts:
        if part in EXCLUDE:
            return False
    return True

with zipfile.ZipFile(OUT_FILE, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(ROOT):
        root_path = Path(root)
        # skip excluded dirs in-place
        dirs[:] = [d for d in dirs if should_include(root_path / d)]
        for f in files:
            fp = root_path / f
            if not should_include(fp):
                continue
            # write with relative path
            arcname = fp.relative_to(ROOT)
            zf.write(fp, arcname)

print(f'Release gerada em: {OUT_FILE}')
