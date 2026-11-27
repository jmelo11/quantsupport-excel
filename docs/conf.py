"""Excel guides and API reference generated from this add-in's metadata."""

import sys
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs/_ext"))
project = "QuantSupport Excel"
author = "QuantSupport contributors"
release = tomllib.loads((ROOT / "Cargo.toml").read_text())["workspace"]["package"][
    "version"
]
extensions = ["excel_api", "myst_parser"]
html_theme = "furo"
html_title = f"QuantSupport Excel {release}"
html_baseurl = "https://jmelo11.github.io/quantsupport-excel/"
html_show_sourcelink = False
exclude_patterns = ["_build", "README.md", "requirements.txt"]
myst_enable_extensions = ["dollarmath", "amsmath"]

core_revision = tomllib.loads((ROOT / "Cargo.toml").read_text())["dependencies"][
    "quantsupport"
]["rev"]
rst_epilog = f".. |core_revision| replace:: {core_revision}"
