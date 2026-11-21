#!/usr/bin/env python3
"""Entry point for the-passport-page-of-a-countr-2-20261121-0318 (Python 3.13,
stdlib only).

The passport spread is rendered at build time by generate.py and stored in
the repository as assets/entry.png. This program just copies that file to
the grader's output directory, so it needs no network, no clock and no
randomness, and two runs write byte-identical output.

Run locally with:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "assets" / "entry.png"
DEST_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

DEST_DIR.mkdir(parents=True, exist_ok=True)
shutil.copyfile(SRC, DEST_DIR / "entry.png")
print(f"wrote {DEST_DIR / 'entry.png'}")
