#!/usr/bin/env python
"""Configuration related functionality for scriptorium."""

import os
import os.path
import atexit
import shutil
import yaml

import scriptorium

_DEFAULT_DIR = os.path.join(os.path.expanduser("~"), '.scriptorium')
_DEFAULT_CFG = os.path.join(_DEFAULT_DIR, 'config')

def read_config():
    """Read configuration values for scriptorium."""
    if not os.path.exists(_DEFAULT_CFG):
        tdir = os.path.join(_DEFAULT_DIR, 'templates')
        #For old users, copy templates to new default directory
        here = os.path.dirname(os.path.realpath(__file__))
        old_templates = os.path.join(here, '..', 'templates')
        if os.path.exists(old_templates):
            print('Migrating templates to new directory structure.')
            shutil.copytree(old_templates, tdir)
            print('Templates now in {0}. You should review and remove them from {1}'.format(old_templates, tdir))
        else:
            os.makedirs(tdir)
        scriptorium.TEMPLATE_DIR = tdir
    else:
        with open(_DEFAULT_CFG, 'r') as cfg_fp:
            cfg = yaml.load(cfg_fp)
            scriptorium.TEMPLATE_DIR = cfg['TEMPLATE_DIR']

def save_config():
    """Save configuration values for scriptorium."""
    with open(_DEFAULT_CFG, 'w') as cfg_fp:
        cfg = {'TEMPLATE_DIR': scriptorium.TEMPLATE_DIR}
        yaml.dump(cfg, cfg_fp)

atexit.register(save_config)
