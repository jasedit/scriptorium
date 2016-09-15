#!/usr/bin/env python

TEMPLATE_DIR = None

from .papers import paper_root, get_template, to_pdf, create
from .templates import all_templates, find_template
from .config import read_config, save_config
from .__main__ import main

read_config()