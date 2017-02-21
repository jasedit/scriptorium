#!/usr/bin/env python
"""Configuration related functionality for scriptorium."""

import os
import yaml

import scriptorium

_DEFAULT_DIR = os.path.join(os.path.expanduser("~"), '.scriptorium')
_CFG_FILE = os.path.join(_DEFAULT_DIR, 'config')

_DEFAULT_CFG = {
    'TEMPLATE_DIR': os.path.join(_DEFAULT_DIR, 'templates'),
    'LATEX_CMD': 'xelatex'
}

def _sanitize_paths(cfg):
    """Ensure that paths in configuration options have ~ symbols expanded."""
    cfg['TEMPLATE_DIR'] = os.path.expanduser(cfg['TEMPLATE_DIR'])

def read_config():
    """Read configuration values for scriptorium."""
    try:
        with open(_CFG_FILE, 'Ur') as cfg_fp:
            cfg = yaml.load(cfg_fp)
            scriptorium.CONFIG.update(cfg)
            _sanitize_paths(scriptorium.CONFIG)
    except EnvironmentError:
        if not os.path.exists(scriptorium.CONFIG['TEMPLATE_DIR']):
            os.makedirs(scriptorium.CONFIG['TEMPLATE_DIR'])
        #Save configuration from first time
        save_config()

    if not os.path.exists(scriptorium.CONFIG['TEMPLATE_DIR']):
        err_msg = '{0} is a non-existent template directory'.format(scriptorium.CONFIG['TEMPLATE_DIR'])
        raise ValueError(err_msg)

def save_config():
    """Save configuration values for scriptorium."""
    _sanitize_paths(scriptorium.CONFIG)
    with open(_CFG_FILE, 'w') as cfg_fp:
        yaml.dump(scriptorium.CONFIG, cfg_fp)
