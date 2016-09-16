#!/usr/bin/env python
"""Tools for reasoning over templates."""

import subprocess
import re
import os
import os.path

import scriptorium

def all_templates(dname):
    """Builds list of installed templates."""

    if not dname:
        dname = scriptorium.TEMPLATE_DIR
    templates = []
    for dirpath, _, filenames in os.walk(dname):
        if 'setup.tex' in filenames:
            templates.append(os.path.basename(dirpath))

    return templates

def find_template(tname, template_dir=None):
    """Searches given template directory for the named template."""

    template_dir = template_dir if template_dir else scriptorium.TEMPLATE_DIR
    for dirpath, _, _ in os.walk(template_dir):
        if os.path.basename(dirpath) == tname:
            return os.path.join(template_dir, dirpath)
    return None

def repo_checkout(repo, rev):
    """Checks out a specific revision of the repository."""
    old_cwd = os.getcwd()
    os.chdir(repo)
    subprocess.check_call(['git', 'checkout', rev])
    os.chdir(old_cwd)

def install_template(url, template_dir=None, rev=None):
    """Installs a template in the template_dir, optionally selecting a revision."""
    url_re = re.compile(r'((git|ssh|http(s)?)(:(//)?)|([\w\d]*@))?(?P<url>[\w\.]+).*\/(?P<dir>[\w\-]+)(\.git)(/)?')
    match = url_re.search(url)
    if not match:
        print('{0} is not a valid git URL'.format(url))
        return False
    template = match.group('dir')
    template_dir = template_dir if template_dir else scriptorium.TEMPLATE_DIR
    template_dest = os.path.join(template_dir, template)

    if os.path.exists(template_dest):
        print('{0} already exists, cannot install on top'.format(template))
        return False

    try:
        subprocess.check_output(['git', 'clone', url, template_dest], universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        print('\n'.join(['Could not clone template:', exc.output]))

    treeish_re = re.compile(r'[A-Za-z0-9_\-\.]+')
    if rev and treeish_re.match(rev):
        repo_checkout(template_dest, rev)

    return True

def update_template(template, template_dir=None, rev=None, max_depth=100):
    """Updates the given template repository."""
    template_loc = find_template(template, template_dir)
    if not template_loc:
        print('Cannot find template {0}'.format(template))
        return False

    old_cwd = os.getcwd()
    os.chdir(template_loc)
    try:
        if not rev:
            rev = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD'], universal_newlines=True)
            rev = rev.rstrip()
        treeish_re = re.compile(r'[A-Za-z0-9_\-\.]+')
        if treeish_re.match(rev):
            subprocess.check_call(['git', 'pull', 'origin', rev])
    except subprocess.CalledProcessError as e:
        print('Update failed on {0}'.format(template))
        return False
    os.chdir(old_cwd)
    return True
