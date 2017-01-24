#!/usr/bin/env python
"""Initialization of scriptorium package."""

TEMPLATE_DIR = None
LATEX_CMD = None

from .config import read_config, save_config

read_config()

from .papers import paper_root, get_template, to_pdf, create
from .templates import all_templates, find_template, install_template, update_template
from .templates import list_variables, get_manifest, get_default_config
from .install import find_missing_binaries, find_missing_packages
from .__main__ import main