#!/usr/bin/env python
from os import scandir
from pathlib import Path
from shutil import rmtree

pj_root = Path(__file__).parent.parent / "src"
for path in pj_root.glob("**/__pycache__"):
    rmtree(path)

for path in pj_root.glob("**/"):
    if any(scandir(path)):
        continue
    rmtree(path)
