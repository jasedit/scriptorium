#!/usr/bin/env python
"""Tools for reasoning over templates."""

import re
import os
import os.path
import yaml
import pygit2

import scriptorium
from .repos import _parse_repo_url

def all_templates(dname=None):
    """Builds list of installed templates."""
    if not dname or not os.path.exists(dname):
        dname = scriptorium.CONFIG['TEMPLATE_DIR']
    templates = []
    for dirpath, _, filenames in os.walk(dname):
        if 'setup.tex' in filenames:
            templates.append(os.path.basename(dirpath))

    return templates

def find_template(tname, template_dir=None):
    """Searches given template directory for the named template."""
    template_dir = template_dir if template_dir else scriptorium.CONFIG['TEMPLATE_DIR']
    for dirpath, _, _ in os.walk(template_dir):
        if os.path.basename(dirpath) == tname:
            return os.path.join(template_dir, dirpath)
    raise IOError('{0} cannot be found in {1}'.format(tname, template_dir))

def install_template(url, template_dir=None, rev=None):
    """Installs a template in the template_dir, optionally selecting a revision."""
    template_dir = template_dir if template_dir else scriptorium.CONFIG['TEMPLATE_DIR']
    scriptorium.clone_repo(url, template_dir, rev)

def update_template(template, template_dir=None, rev=None, force=False):
    """Updates the given template repository."""
    template_loc = find_template(template, template_dir)

    scriptorium.update_repo(template_loc, rev=rev, force=force)

def list_variables(template, template_dir=None):
    """List variables a template offers for paper creation."""
    template_dir = template_dir if template_dir else scriptorium.CONFIG['TEMPLATE_DIR']

    template_loc = find_template(template, template_dir)

    var_re = re.compile(r'\$(?P<var>[A-Z0-9]+)')

    files = [os.path.join(template_loc, 'frontmatter.mmd'),
             os.path.join(template_loc, 'metadata.tex')
            ]
    variables = []
    for test_file in files:
        try:
            with open(test_file, 'r') as fp:
                for match in re.finditer(var_re, fp.read()):
                    if match.group('var') != 'TEMPLATE':
                        variables.append(match.group('var'))
        except EnvironmentError:
            pass
    return list(set(variables))

def get_manifest(template, template_dir=None):
    """
    Get manifest for a given template with keys as output names, and values as input names.

    This list of files defines which files should be used when creating a new paper using this document.
    """
    template_dir = template_dir if template_dir else scriptorium.CONFIG['TEMPLATE_DIR']
    template_loc = find_template(template, template_dir)
    manifest_path = os.path.join(template_loc, 'manifest.yml')
    manifest = {
        'paper.mmd': 'frontmatter.mmd',
        'metadata.tex': 'metadata.tex'
        }

    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as mfp:
            manifest = yaml.load(mfp)

    #Remove non-existent files from manifest list
    manifest = {kk:vv for kk, vv in manifest.items() if os.path.exists(os.path.join(template_loc, vv))}
    return manifest

def get_default_config(template, template_dir=None):
    """Get default configuration options if available."""
    template_dir = template_dir if template_dir else scriptorium.CONFIG['TEMPLATE_DIR']
    template_loc = find_template(template, template_dir)
    config_path = os.path.join(template_loc, 'default_config.yml')
    config = {}

    if os.path.exists(config_path):
        with open(config_path, 'r') as cfp:
            raw_config = yaml.load(cfp)
        config = {kk.upper(): vv for kk, vv in raw_config.items()}
    return config
