#!/usr/bin/env python
"""Paper oriented operations."""

import glob
import subprocess
import re
import os
import shutil
import platform
import tempfile
import mmap

import sys

import pymmd

import scriptorium

_BLANK_LINK = bytearray('\n\n', 'utf-8') if sys.version_info >= (3,0) else '\n\n'

def _list_files(dname):
    """Builds list of all files which could be converted via MultiMarkdown."""
    fexts = ['mmd', 'md', 'txt']
    return [ii for jj in fexts for ii in glob.glob(os.path.join(dname, '*.' + jj))]

def paper_root(dname):
    """Given a directory, finds the root document for the paper."""
    root_doc = None

    for fname in _list_files(dname):
        #Template metadata only exists in root
        if get_template(fname):
            root_doc = fname
            break

    return os.path.basename(root_doc) if root_doc else None

def _get_template(txt):
    """Extract template name from string containing document text"""
    template = pymmd.value(txt, 'latexfooter', pymmd.COMPLETE)
    template_re = re.compile(r'(?P<template>[a-zA-Z0-9._]*)\/footer.tex')

    match = template_re.search(template)

    return match.group('template') if match else None

def get_template(fname):
    """Attempts to find the template of a paper in a given file."""
    if os.stat(fname).st_size == 0:
        return None
    with open(fname, 'r') as mmd_fp:
        mmf = mmap.mmap(mmd_fp.fileno(), 0, access=mmap.ACCESS_READ)
        idx = mmf.find(_BLANK_LINK)
        if idx == -1:
            idx = mmf.size()
        mmf.seek(0)
        frontmatter = mmf.read(idx).decode('utf-8')
        return _get_template(frontmatter)

def _build_latex_cmd(fname, template_dir, use_shell_escape=False):
    """Builds LaTeX command and environment to process a given paper."""
    bname = os.path.basename(fname).split('.')[0]
    tname = '{0}.tex'.format(bname)

    template = get_template(fname)
    if not template:
        raise IOError('{0} does not appear to have lines necessary to load a template.'.format(fname))

    template_loc = scriptorium.find_template(template, template_dir)

    if not template_loc:
        raise IOError('{0} template not installed in {1}'.format(template, template_dir))

    template_loc = os.path.abspath(os.path.join(template_loc, '..'))

    #Need to set up environment here
    new_env = dict(os.environ)
    old_inputs = new_env.get('TEXINPUTS')
    texinputs = './:{0}:{1}'.format(template_loc + '/.//', old_inputs + ':' if old_inputs else '')
    new_env['TEXINPUTS'] = texinputs

    pdf_cmd = [scriptorium.CONFIG['LATEX_CMD'], '-halt-on-error', '-interaction=nonstopmode', tname]

    if platform.system() == 'Windows':
        pdf_cmd.insert(-2, '-include-directory={0}'.format(template_loc))

    if use_shell_escape:
        pdf_cmd.insert(1, '-shell-escape')
    return pdf_cmd, new_env

def _process_bib(fname):
    """Perform processing to generate bibliography data for the given LaTeX file."""
    bname = os.path.basename(fname).split('.')[0]
    try:
        auxname = '{0}.aux'.format(bname)
        #Check if bibtex is defined in the frontmatter
        bibtex_re = re.compile(r'^bibtex:', re.MULTILINE)
        with open(fname, 'r') as paper_fp:
            if bibtex_re.search(paper_fp.read()):
                biber_re = re.compile(r'\\bibdata', re.MULTILINE)
                full = open(auxname, 'r').read()
                if biber_re.search(full):
                    subprocess.check_output(['bibtex', auxname], universal_newlines=True)
                else:
                    subprocess.check_output(['biber', bname], universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        raise IOError(exc.output)

def to_pdf(paper_dir, template_dir=None, use_shell_escape=False, flatten=False):
    """Build paper in the given directory, returning the PDF filename if successful."""
    template_dir = template_dir or scriptorium.CONFIG['TEMPLATE_DIR']

    paper_dir = os.path.abspath(paper_dir)
    if os.path.isdir(paper_dir):
        fname = paper_root(paper_dir)
    elif os.path.isfile(paper_dir):
        fname = paper_dir
        paper_dir = os.path.dirname(paper_dir)
    else:
        raise IOError("{0} is not a valid directory".format(paper_dir))

    old_cwd = os.getcwd()
    if old_cwd != paper_dir:
        os.chdir(paper_dir)

    if not fname:
        raise IOError("{0} has no obvious root.".format(paper_dir))

    #Convert all auxillary MMD files to LaTeX
    for mmd in _list_files(paper_dir):
        bname = os.path.basename(mmd).split('.')[0]
        with open(mmd, 'r') as mmd_fp, open('{0}.tex'.format(bname), 'w') as tex_fp:
            tex_fp.write(pymmd.convert(mmd_fp.read(), fmt=pymmd.LATEX, dname=mmd, ext=pymmd.SMART))

    pdf_cmd, new_env = _build_latex_cmd(fname, template_dir, use_shell_escape)

    bname = os.path.basename(fname).split('.')[0]
    if flatten:
        tname = '{0}.tex'.format(bname)
        with tempfile.NamedTemporaryFile() as tmp:
            subprocess.check_call(['latexpand', '-o', tmp.name, tname], env=new_env)
            shutil.copyfile(tmp.name, tname)
    try:
        subprocess.check_output(pdf_cmd, env=new_env, universal_newlines=True).encode('utf-8')
    except subprocess.CalledProcessError as exc:
        raise IOError(exc.output)

    _process_bib(fname)

    subprocess.check_output(pdf_cmd, env=new_env, universal_newlines=True)
    subprocess.check_output(pdf_cmd, env=new_env, universal_newlines=True)

    # Revert working directory
    if os.getcwd() != old_cwd:
        os.chdir(old_cwd)

    return os.path.join(paper_dir, '{0}.pdf'.format(bname))

def _expand_variables(template, texts, config):
    # """Given a
    #Inject template as macro argument
    config['TEMPLATE'] = template
    full_config = scriptorium.get_default_config(template)
    full_config.update(config)

    #One line regex thanks to http://stackoverflow.com/a/6117124/59184
    for ofile, text in texts.items():
        texts[ofile] = re.sub("|".join([r'\${0}'.format(ii) for ii in full_config]),
                              lambda m: full_config[m.group(0)[1:]], text)

    #Regex to find variable names
    var_re = re.compile(r'\$[A-Z0-9_\.\-]+')
    unset_vars = set()
    for ofile, text in texts.items():
        unset_vars |= set([ii.group(0) for ii in var_re.finditer(text)])

    unset_vars = set([ii[1:].lower() for ii in unset_vars])
    return unset_vars

def create(paper_dir, template, force=False, use_git=True, config=None):
    """Create folder with paper skeleton.
    Returns a list of unpopulated variables if successfully created.
    """

    try:
        config = {kk.upper():vv for kk, vv in config}
    except ValueError:
        config = {kk.upper():vv for kk, vv in config.items()}

    if os.path.exists(paper_dir) and not force:
        raise IOError('{0} exists'.format(paper_dir))

    template_dir = scriptorium.find_template(template, scriptorium.CONFIG['TEMPLATE_DIR'])

    os.makedirs(paper_dir)
    if use_git and not os.path.exists(os.path.join(paper_dir, '.gitignore')):
        shutil.copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data',
                                     'gitignore'),
                        os.path.join(paper_dir, '.gitignore'))

    files = scriptorium.get_manifest(template)
    texts = {}
    for ofile, ifile in files.items():
        ifile = os.path.join(template_dir, ifile)
        try:
            with open(ifile, 'r') as ifp:
                texts[ofile] = ifp.read()
        except IOError:
            texts[ofile] = ''

    unset_vars = _expand_variables(template, texts, config)
    for ofile, text in texts.items():
        with open(os.path.join(paper_dir, ofile), 'w') as ofp:
            ofp.write(text)

    return unset_vars
