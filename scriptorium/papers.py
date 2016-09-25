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
        #Metadata only exists in the root document
        if pymmd.has_metadata_from(fname, pymmd.COMPLETE):
            root_doc = fname
            break

    return os.path.basename(root_doc) if root_doc else None

def get_template(fname):
    """Attempts to find the template of a paper in a given file."""
    template = pymmd.extract_metadata_value_from(fname, 'latexfooter', pymmd.COMPLETE)
    template_re = re.compile(r'(?P<template>[a-zA-Z0-9._]*)\/footer.tex')

    match = template_re.search(template)

    return match.group('template') if match else None

def to_pdf(paper_dir, template_dir=None, use_shell_escape=False):
    """Build paper in the given directory, returning the PDF filename if successful."""
    template_dir = template_dir if template_dir else scriptorium.TEMPLATE_DIR
    paper = os.path.abspath(paper_dir)
    if not os.path.isdir(paper):
        raise IOError("{0} is not a valid directory".format(paper))
    old_cwd = os.getcwd()
    if old_cwd != paper_dir:
        os.chdir(paper)

    fname = paper_root('.')

    if not fname:
        raise IOError("{0} does not contain a file that appears to be the root of the paper.".format(paper))

    for mmd in set(glob.glob('*.mmd')) - set(pymmd.manifest(fname)):
        bname = os.path.basename(mmd).split('.')[0]
        tname = '{0}.tex'.format(bname)
        pymmd.convert_from(mmd, fmt=pymmd.LATEX, oname=tname)

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
        with open(fname, 'r') as paper_fp:
            if bibtex_re.search(paper_fp.read()):
                biber_re = re.compile(r'\\bibdata', re.MULTILINE)
                full = open('paper.aux').read()
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

    return os.path.join(paper, '{0}.pdf'.format(bname))

def create(paper_dir, template, force=False, use_git=True, config=None):
    """Create folder with paper skeleton.
    Returns a list of unpopulated variables if successfully created."""

    config = config if config else []
    if os.path.exists(paper_dir) and not force:
        raise IOError('{0} exists'.format(paper_dir))
    template_dir = scriptorium.find_template(template, scriptorium.TEMPLATE_DIR)

    if not template_dir:
        raise ValueError('{0} is not an installed template.'.format(template))

    os.makedirs(paper_dir)
    if use_git:
        here = os.path.dirname(os.path.realpath(__file__))
        giname = os.path.join(here, 'data', 'gitignore')
        shutil.copyfile(giname, os.path.join(paper_dir, '.gitignore'))

    #Create frontmatter section for paper
    front_file = os.path.join(template_dir, 'frontmatter.mmd')
    if os.path.exists(front_file):
        with open(front_file, 'r') as paper_fp:
            paper = paper_fp.read()
    else:
        paper = ''

    #Create metadata section
    metaex_file = os.path.join(template_dir, 'metadata.tex')
    if os.path.exists(metaex_file):
        with open(metaex_file, 'r') as meta_fp:
            metadata = meta_fp.read()
    else:
        metadata = ''

    for opt in config:
        repl = re.compile(r'\${0}'.format(opt[0].upper()))
        paper = repl.sub(opt[1], paper)
        metadata = repl.sub(opt[1], metadata)

    #Regex to find variable names
    var_re = re.compile(r'\$[A-Z0-9_\.\-]+')
    paper_file = os.path.join(paper_dir, 'paper.mmd')
    with open(paper_file, 'w') as paper_fp:
        paper_fp.write(paper)
        #Only add a newline if previous material exists
        if paper:
            paper_fp.write('\n')
        paper_fp.write('latex input: {0}/setup.tex\n'.format(template))
        paper_fp.write('latex footer: {0}/footer.tex\n\n'.format(template))

    unset_vars = set([ii.group(0) for ii in var_re.finditer(paper)])

    if metadata:
        metadata_file = os.path.join(paper_dir, 'metadata.tex')
        with open(metadata_file, 'w') as meta_fp:
            meta_fp.write(metadata)
        for match in var_re.finditer(metadata):
            unset_vars += match.group(0)

    return unset_vars
