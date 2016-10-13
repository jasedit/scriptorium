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
    raise IOError('{0} cannot be found in {1}'.format(tname, template_dir))

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
        raise ValueError('{0} is not a valid git URL'.format(url))
    template = match.group('dir')
    template_dir = template_dir if template_dir else scriptorium.TEMPLATE_DIR
    template_dest = os.path.join(template_dir, template)

    if os.path.exists(template_dest):
        raise IOError('{0} already exists, cannot install on top'.format(template))

    try:
        subprocess.check_output(['git', 'clone', url, template_dest], universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        raise IOError('\n'.join(['Could not clone template:', exc.output]))

    treeish_re = re.compile(r'[A-Za-z0-9_\-\.]+')
    if rev and treeish_re.match(rev):
        repo_checkout(template_dest, rev)

def update_template(template, template_dir=None, rev=None):
    """Updates the given template repository."""
    template_loc = find_template(template, template_dir)

    old_cwd = os.getcwd()
    os.chdir(template_loc)
    try:
        subprocess.check_call(['git', 'fetch', 'origin'])
        git_cmd = ['git', 'symbolic-ref', '--short', 'HEAD']
        current_rev = subprocess.check_output(git_cmd, universal_newlines=True)
        current_rev = current_rev.rstrip()
        rev = rev if rev else current_rev
        treeish_re = re.compile(r'[A-Za-z0-9_\-\.]+')
        if treeish_re.match(rev):
            if rev != current_rev:
                subprocess.check_call(['git', 'checkout', rev])
            subprocess.check_call(['git', 'pull', 'origin', rev])
    except subprocess.CalledProcessError as exc:
        raise IOError('Cannot update {0}:\n {1}'.format(template, exc.output))
    os.chdir(old_cwd)

def list_variables(template, template_dir=None):
    """List variables a template offers for paper creation."""
    template_dir = template_dir if template_dir else scriptorium.TEMPLATE_DIR

    template_loc = find_template(template, template_dir)

    var_re = re.compile(r'\$(?P<var>[A-Z0-9]+)')

    files = [os.path.join(template_loc, 'frontmatter.mmd'),
             os.path.join(template_loc, 'metadata.tex')
            ]
    variables = []
    for test_file in files:
        try:
            with open(test_file, 'Ur') as fp:
                for match in re.finditer(var_re, fp.read()):
                    if match.group('var') != 'TEMPLATE':
                        variables.append(match.group('var'))
        except EnvironmentError:
            pass
    return list(set(variables))
