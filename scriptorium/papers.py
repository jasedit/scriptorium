#!/usr/bin/env python
"""Paper oriented operations."""

import glob
import subprocess
import re
import os
import shutil

import scriptorium

def paper_root(dname):
    """Given a directory, finds the root document for the paper."""

    root_doc = None
    for fname in glob.glob(os.path.join(dname, '*.mmd')):
        #Metadata only exists in the root document
        output = subprocess.check_output(['multimarkdown', '-m', fname])
        if output:
            root_doc = fname
            break

    return os.path.basename(root_doc) if root_doc else None

def get_template(fname):
    """Attempts to find the template of a paper in a given file."""

    output = subprocess.check_output(['multimarkdown', '-e', 'latexfooter', fname])
    template_re = re.compile(r'(?P<template>[a-zA-Z0-9._]*)\/footer.tex')

    match = template_re.search(output)

    return match.group('template') if match else None

def to_pdf(paper_dir, template_dir=None, use_shell_escape=False):
    """Build paper in the given directory, returning the PDF filename if successful."""

    template_dir = template_dir if template_dir else scriptorium.TEMPLATE_DIR
    paper = os.path.abspath(paper_dir)
    if not os.path.isdir(paper):
        raise IOError("{0} is not a valid directory".format(paper))
    old_cwd = os.getcwd()
    if not os.path.samefile(old_cwd, paper):
        os.chdir(paper)

    fname = paper_root('.')

    if not fname:
        raise IOError("{0} does not contain a file that appears to be the root of the paper.".format(paper))

    all_mmd = glob.glob('*.mmd')
    default_mmd = subprocess.check_output(['multimarkdown', '-x', fname], universal_newlines=True)
    default_mmd = default_mmd.splitlines()
    for mmd in set(all_mmd) - set(default_mmd):
        bname = os.path.basename(mmd).split('.')[0]
        tname = '{0}.tex'.format(bname)
        subprocess.check_call(['multimarkdown', '-t', 'latex', '-o', tname, mmd])

    bname = os.path.basename(fname).split('.')[0]
    tname = '{0}.tex'.format(bname)

    #Need to set up environment here
    new_env = dict(os.environ)
    texinputs = './:{0}'.format(template_dir + '/.//')
    if 'TEXINPUTS' in new_env:
      texinputs = '{0}:{1}'.format(texinputs, new_env['TEXINPUTS'])
    texinputs = texinputs + ':'
    new_env['TEXINPUTS'] = texinputs
    pdf_cmd = ['pdflatex', '-halt-on-error', tname]

    if use_shell_escape:
      pdf_cmd.append('-shell-escape')
    try:
        output = subprocess.check_output(pdf_cmd, env=new_env)
    except subprocess.CalledProcessError:
        print('LaTeX conversion failed with the following output:\n', output)
        return None

    auxname = '{0}.aux'.format(bname)
    #Check if bibtex is defined in the frontmatter
    bibtex_re = re.compile(r'^bibtex:')
    if bibtex_re.search(open(fname).read()):
        biber_re = re.compile(r'\\bibdata')
        full = open('paper.aux').read()
        with open(os.devnull, 'w') as null:
            if biber_re.search(full):
                subprocess.check_call(['bibtex', auxname], stdout=null, stderr=null)
            else:
                subprocess.check_call(['biber', bname], stdout=null, stderr=null)

            subprocess.check_call(pdf_cmd, env=new_env, stdout=null, stderr=null)
            subprocess.check_call(pdf_cmd, env=new_env, stdout=null, stderr=null)

    # Revert working directory
    if not os.path.samefile(os.getcwd(), old_cwd):
        os.chdir(old_cwd)

    return os.path.join(paper, '{0}.pdf'.format(bname))

def create(paper_dir, template, force=False, use_git=True, config=None):
    """Create folder with paper skeleton."""

    config = config if config else []
    if os.path.exists(paper_dir) and not force:
        print('{0} exists, will not overwrite. Use -f to force creation.'.format(output))
        return False
    template_dir = scriptorium.find_template(template, scriptorium.TEMPLATES_DIR)

    if not template_dir:
        print('{0} is not an installed template.'.format(template))
        return False

    os.makedirs(paper_dir)
    if use_git:
        here = os.path.dirname(os.path.realpath(__file__))
        giname = os.path.join(here, 'data', 'gitignore')
        shutil.copyfile(giname, os.path.join(paper_dir))

    #Create frontmatter section for paper
    front_file = os.path.join(scriptorium.TEMPLATE_DIR, 'frontmatter.mmd')
    if os.path.exists(front_file):
        with open(front_file, 'r') as fp:
            paper = fp.read()
    else:
        paper = ''

    #Create metadata section
    metaex_file = os.path.join(scriptorium.TEMPLATE_DIR, 'metadata.tex')
    if os.path.exists(metaex_file):
        with open(metaex_file, 'r') as fp:
            metadata = fp.read()
    else:
        metadata = ''

    for opt in config:
        repl = re.compile('${0}'.format(opt[0].upper()))
        repl.sub(opt[1], paper)
        repl.sub(opt[1], metadata)

    #Regex to find variable names
    var_re = re.compile(r'\$[A-Z0-9]+')
    paper_file = os.path.join(paper_dir, 'paper.mmd')
    with open(paper_file, 'w') as fp:
        fp.write(paper)
        fp.write('\n')
        fp.write('latex input: {0}/setup.tex\n'.format(template))
        fp.write('latex footer: {0}/footer.tex\n\n'.format(template))

    for ii in var_re.finditer(paper):
        print('{0} contains unpopulated variable {1}'.format(paper_file, ii.group(0)))

    if metadata:
        metadata_file = os.path.join(paper_dir, 'metadata.tex')
        with open(metadata_file, 'w') as fp:
            fp.write(metadata)
        for mtch in var_re.finditer(metadata):
            print('{0} contains unpopulated variable {1}'.format(metadata_file, mtch.group(0)))

    return True
