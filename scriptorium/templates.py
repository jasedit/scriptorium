#!/usr/bin/env python
"""Tools for reasoning over templates."""

import os

import scriptorium

def all_templates(dname):
    """Builds list of installed templates."""

    templates = []
    for dirpath, _, filenames in os.walk(dname):
        if 'setup.tex' in filenames:
            templates.append(os.path.basename(dirpath))

    return templates

def find_template(tname, tdir=scriptorium.TEMPLATES_DIR):
    """Searches given template directory for the named template."""
    for dirpath, _, _ in os.walk(tdir):
        if os.path.basename(dirpath) == tname:
            return os.path.join(tdir, dirpath)
    return None