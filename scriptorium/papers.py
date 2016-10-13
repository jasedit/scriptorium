#!/usr/bin/env python
"""Paper oriented operations."""

import glob
import subprocess
import re
import os
import shutil
import platform

import pymmd

import scriptorium

def paper_root(dname):
    """Given a directory, finds the root document for the paper."""
    root_doc = None
    for fname in glob.glob(os.path.join(dname, '*.mmd')):
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
    with open(fname, 'Ur', encoding='utf8') as mmd_fp:
        return _get_template(mmd_fp.read())

def to_pdf(paper_dir, template_dir=None, use_shell_escape=False):
    """Build paper in the given directory, returning the PDF filename if successful."""
    template_dir = template_dir or scriptorium.TEMPLATE_DIR
    paper_dir = os.path.abspath(paper_dir)
    if not os.path.isdir(paper_dir):
        raise IOError("{0} is not a valid directory".format(paper_dir))
    old_cwd = os.getcwd()
    if old_cwd != paper_dir:
        os.chdir(paper_dir)

    fname = paper_root('.')

    if not fname:
        raise IOError("{0} has no obvious root.".format(paper_dir))

    #Convert all auxillary MMD files to LaTeX
    for mmd in glob.glob('*.mmd'):
        bname = os.path.basename(mmd).split('.')[0]
        tname = '{0}.tex'.format(bname)
        with open(mmd, 'Ur') as mmd_fp, open(tname, 'w') as tex_fp:
            txt = pymmd.convert(mmd_fp.read(), fmt=pymmd.LATEX, dname=mmd)
            tex_fp.write(txt)

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

    pdf_cmd = ['pdflatex', '-halt-on-error', '-interaction=nonstopmode', tname]

    if platform.system() == 'Windows':
        pdf_cmd.insert(-2, '-include-directory={0}'.format(template_loc))

    if use_shell_escape:
        pdf_cmd.insert(1, '-shell-escape')
    try:
        subprocess.check_output(pdf_cmd, env=new_env, universal_newlines=True).encode('utf-8')
    except subprocess.CalledProcessError as exc:
        raise IOError(exc.output)

    try:
        auxname = '{0}.aux'.format(bname)
        #Check if bibtex is defined in the frontmatter
        bibtex_re = re.compile(r'^bibtex:', re.MULTILINE)
        with open(fname, 'Ur') as paper_fp:
            if bibtex_re.search(paper_fp.read()):
                biber_re = re.compile(r'\\bibdata', re.MULTILINE)
                full = open('paper.aux', 'Ur').read()
                if biber_re.search(full):
                    subprocess.check_output(['bibtex', auxname], universal_newlines=True)
                else:
                    subprocess.check_output(['biber', bname], universal_newlines=True)

                subprocess.check_output(pdf_cmd, env=new_env, universal_newlines=True)
                subprocess.check_output(pdf_cmd, env=new_env, universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        raise IOError(exc.output)

    # Revert working directory
    if os.getcwd() != old_cwd:
        os.chdir(old_cwd)

    return os.path.join(paper_dir, '{0}.pdf'.format(bname))

def create(paper_dir, template, force=False, use_git=True, config=None):
    """Create folder with paper skeleton.
    Returns a list of unpopulated variables if successfully created.
    """
    if os.path.exists(paper_dir) and not force:
        raise IOError('{0} exists'.format(paper_dir))

    template_dir = scriptorium.find_template(template, scriptorium.TEMPLATE_DIR)

    os.makedirs(paper_dir)
    if use_git and not os.path.exists(os.path.join(paper_dir, '.gitignore')):
        shutil.copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data',
                                     'gitignore'),
                        os.path.join(paper_dir, '.gitignore'))

    files = {'paper.mmd': 'frontmatter.mmd',
             'metadata.tex': 'metadata.tex'}
    texts = {}
    for ofile, ifile in files.items():
        ifile = os.path.join(template_dir, ifile)
        try:
            with open(ifile, 'Ur') as ifp:
                texts[ofile] = ifp.read()
        except IOError:
            texts[ofile] = ''

    #Inject template as macro argument
    config['TEMPLATE'] = template
    #One line regex thanks to http://stackoverflow.com/a/6117124/59184
    for ofile, text in texts.items():
        texts[ofile] = re.sub("|".join([r'\${0}'.format(ii) for ii in config]),
                              lambda m: config[m.group(0)[1:]], text)

    #Regex to find variable names
    var_re = re.compile(r'\$[A-Z0-9_\.\-]+')
    unset_vars = set()
    for ofile, text in texts.items():
        unset_vars |= set([ii.group(0) for ii in var_re.finditer(text)])
        with open(os.path.join(paper_dir, ofile), 'w') as ofp:
            ofp.write(text)

    return unset_vars
