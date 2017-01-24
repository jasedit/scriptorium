#!/usr/bin/env python
"""Configuration related functionality for scriptorium."""

import os
import yaml

import scriptorium

_DEFAULT_DIR = os.path.join(os.path.expanduser("~"), '.scriptorium')
_DEFAULT_CFG = os.path.join(_DEFAULT_DIR, 'config')

def read_config():
    """Read configuration values for scriptorium."""
    default_template_dir = os.path.join(_DEFAULT_DIR, 'templates')
    default_latex_cmd = 'pdflatex'
    try:
        with open(_DEFAULT_CFG, 'Ur') as cfg_fp:
            cfg = yaml.load(cfg_fp)
            scriptorium.TEMPLATE_DIR = cfg.get('TEMPLATE_DIR', default_template_dir)
            scriptorium.LATEX_CMD = cfg.get('LATEX_CMD', default_latex_cmd)
    except EnvironmentError:
        if not os.path.exists(default_template_dir):
            os.makedirs(default_template_dir)
        scriptorium.TEMPLATE_DIR = default_template_dir
        scriptorium.LATEX_CMD = default_latex_cmd
        #Save configuration from first time
        save_config()

def save_config():
    """Save configuration values for scriptorium."""
    with open(_DEFAULT_CFG, 'w') as cfg_fp:
        cfg = {
            'TEMPLATE_DIR': scriptorium.TEMPLATE_DIR,
            'LATEX_CMD': scriptorium.LATEX_CMD
        }
        yaml.dump(cfg, cfg_fp)
