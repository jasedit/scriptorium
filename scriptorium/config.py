#!/usr/bin/env python
"""Configuration related functionality for scriptorium."""

import os
import yaml

import scriptorium

_DEFAULT_DIR = os.path.join(os.path.expanduser("~"), '.scriptorium')
_DEFAULT_CFG = os.path.join(_DEFAULT_DIR, 'config')

def read_config():
    """Read configuration values for scriptorium."""
    try:
        with open(_DEFAULT_CFG, 'Ur') as cfg_fp:
            cfg = yaml.load(cfg_fp)
            scriptorium.TEMPLATE_DIR = cfg['TEMPLATE_DIR']
    except EnvironmentError:
        tdir = os.path.join(_DEFAULT_DIR, 'templates')
        if not os.path.exists(tdir):
            os.makedirs(tdir)
        scriptorium.TEMPLATE_DIR = tdir
        #Save configuration from first time
        save_config()

def save_config():
    """Save configuration values for scriptorium."""
    with open(_DEFAULT_CFG, 'w') as cfg_fp:
        cfg = {'TEMPLATE_DIR': scriptorium.TEMPLATE_DIR}
        yaml.dump(cfg, cfg_fp)
