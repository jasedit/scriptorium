#!/usr/bin/env python
#Script to build a scriptorium paper in a cross-platform friendly fashion

import argparse
import subprocess
import os
import os.path
import glob
import re
import shutil
import sys

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.abspath(os.path.join(BIN_DIR, '..'))
TEMPLATES_DIR = os.path.abspath(os.path.join(BASE_DIR, 'templates'))

def find_paper_root(dname):
  """Given a directory, finds the root document for the paper."""

  root_doc = None
  for fname in glob.glob(os.path.join(dname, '*.mmd')):
      #Metadata only exists in the root document
      output = subprocess.check_output(['multimarkdown', '-m', fname])
      if output:
          root_doc = fname
          break

  return os.path.basename(root_doc) if root_doc else None

def make(args):
    """Build paper in the given directory."""
    paper = os.path.abspath(args.paper)
    if not os.path.isdir(paper):
        raise IOError("{0} is not a valid directory".format(paper))
    old_cwd = os.getcwd()
    if not os.path.samefile(old_cwd, paper):
        os.chdir(paper)

    fname = find_paper_root('.')

    if not fname:
        raise IOError("{0} does not contain a file that appears to be the root of the paper.".format(paper))

    bname = os.path.basename(fname).split('.')[0]
    tname = '{0}.tex'.format(bname)
    subprocess.check_call(['multimarkdown', '-t', 'latex', '-o', tname, fname])

    #Need to set up environment here
    new_env = dict(os.environ)
    new_env['TEXINPUTS'] = './:{0}:{1}'.format(TEMPLATES_DIR + '/.//', new_env['TEXINPUTS'])
    pdf_cmd = ['pdflatex', '-shell-escape', '-halt-on-error', tname]
    output = subprocess.check_output(pdf_cmd, env=new_env)

    auxname = '{0}.aux'.format(bname)
    bibtex_re = re.compile(r'bibtex:')
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

    # Move file from default location to specified location
    if args.output:
        shutil.move('{0}.pdf'.format(bname), os.path.join(old_cwd, args.output))
    # Revert working directory
    if not os.path.samefile(os.getcwd(), old_cwd):
        os.chdir(old_cwd)

def find_theme(fname):
    """Attempts to find the theme of a paper in a given file."""

    output = subprocess.check_output(['multimarkdown', '-e', 'latexfooter', fname])
    theme_re = re.compile(r'(?P<theme>[a-zA-Z0-9._]*)\/footer.tex')

    match = theme_re.search(output)

    return match.group('theme') if match else None

def info(args):
    """Function to attempt to extract useful information from a specified paper."""

    fname = find_paper_root(args.paper)

    if not fname:
        raise IOError('{0} does not contain a valid root document.'.format(args.paper))

    if not fname:
        print('Could not find the root of the paper.')
        sys.exit(1)

    if args.template:
        theme = find_theme(os.path.join(args.paper, fname))
        if not theme:
            print('Could not find footer indicating theme name.')
            sys.exit(2)
        print(theme)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    make_parser = subparsers.add_parser("make")

    make_parser.add_argument("paper", default=".", help="Directory containing paper to make")
    make_parser.add_argument('-o', '--output', help='Filename to store resulting PDF as.')
    make_parser.set_defaults(func=make)

    info_parser = subparsers.add_parser("info")
    info_parser.add_argument("paper", default=".", help="Directory containing paper to make")
    info_parser.add_argument('-t', '--template', action="store_true", help="Flag to extract template")
    info_parser.set_defaults(func=info)

    args = parser.parse_args()

    args.func(args)