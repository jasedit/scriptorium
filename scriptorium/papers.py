#!/usr/bin/env python
"""Paper oriented operations."""

import glob
import subprocess
import re
import os

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

def to_pdf(paper_dir, template_dir, use_shell_escape=False):
    """Build paper in the given directory, returning the PDF filename if successful."""
    paper = os.path.abspath(paper_dir)
    if not os.path.isdir(paper):
        raise IOError("{0} is not a valid directory".format(paper))
    old_cwd = os.getcwd()
    if not os.path.samefile(old_cwd, paper):
        os.chdir(paper)

    fname = paper_root('.')

    if not fname:
        raise IOError("{0} does not contain a file that appears to be the root of the paper.".format(paper))

    bname = os.path.basename(fname).split('.')[0]
    tname = '{0}.tex'.format(bname)
    subprocess.check_call(['multimarkdown', '-t', 'latex', '-o', tname, fname])

    #Need to set up environment here
    new_env = dict(os.environ)
    new_env['TEXINPUTS'] = './:{0}:{1}'.format(template_dir + '/.//', new_env['TEXINPUTS'])
    pdf_cmd = ['pdflatex', '-halt-on-error', tname]

    if use_shell_escape:
      pdf_cmd.append('-shell-escape')
    try:
        output = subprocess.check_output(pdf_cmd, env=new_env)
    except subprocess.CalledProcessError:
        print('LaTeX conversion failed with the following output:')
        print(output)
        return None

    auxname = '{0}.aux'.format(bname)
    #Check if bibtex is defined in the frontmatter
    bibtex_re = re.compile(r'^bibtex:')
    if bibtex_re.search(open(fname).read()):
        biber_re = re.compile(r'\\bibdata')
        full = open('paper.aux').read()
        with open(os.devnull, 'w') as fp:
            if biber_re.search(full):
                subprocess.check_call(['bibtex', auxname], stdout=fp, stderr=fp)
            else:
                subprocess.check_call(['biber', bname], stdout=fp, stderr=fp)

            subprocess.check_call(pdf_cmd, env=new_env, stdout=fp, stderr=fp)
            subprocess.check_call(pdf_cmd, env=new_env, stdout=fp, stderr=fp)

    # Revert working directory
    if not os.path.samefile(os.getcwd(), old_cwd):
        os.chdir(old_cwd)

    return os.path.join(paper, '{0}.pdf'.format(bname))