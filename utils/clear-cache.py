#!/usr/bin/env python
from pathlib import Path
from shutil import rmtree

pj_root = Path(__file__).parent.parent / "auto_flutter"
for path in pj_root.glob("**/__pycache__"):
    rmtree(path)
