#!/usr/bin/env python

import importlib
from pathlib import Path

root = Path(__file__).absolute().parent

for fpath in root.rglob("**/*"):
    if fpath.name.startswith("_"):
        continue
    if fpath.name.startswith("."):
        continue
    if not fpath.name.endswith(".py"):
        continue
    relpath = list(fpath.relative_to(root).parts)[:-1] + [fpath.stem]
    module_name = ".".join(["bots", "backends"] + relpath)
    importlib.import_module(module_name)
