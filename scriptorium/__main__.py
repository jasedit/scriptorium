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
    try:
        output = subprocess.check_output(pdf_cmd, env=new_env)
    except CalledProcessError:
        print('LaTeX conversion failed with the following output:')
        print(output)
        sys.exit(5)

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

    # Move file from default location to specified location
    if args.output:
        shutil.move('{0}.pdf'.format(bname), os.path.join(old_cwd, args.output))
    # Revert working directory
    if not os.path.samefile(os.getcwd(), old_cwd):
        os.chdir(old_cwd)

def extract_paper_template(fname):
    """Attempts to find the template of a paper in a given file."""

    output = subprocess.check_output(['multimarkdown', '-e', 'latexfooter', fname])
    template_re = re.compile(r'(?P<template>[a-zA-Z0-9._]*)\/footer.tex')

    match = template_re.search(output)

    return match.group('template') if match else None

def info(args):
    """Function to attempt to extract useful information from a specified paper."""

    fname = find_paper_root(args.paper)

    if not fname:
        raise IOError('{0} does not contain a valid root document.'.format(args.paper))

    if not fname:
        print('Could not find the root of the paper.')
        sys.exit(1)

    if args.template:
        template = extract_paper_template(os.path.join(args.paper, fname))
        if not template:
            print('Could not find footer indicating template name.')
            sys.exit(2)
        print(template)

def list_templates(dname):
    """Builds list of installed templates."""

    templates = []
    for dirpath, _, filenames in os.walk(dname):
        if 'setup.tex' in filenames:
            templates.append(os.path.basename(dirpath))

    return templates

def find_template(tname, tdir=TEMPLATES_DIR):
    """Searches given template directory for the named template."""
    for dirpath, _, _ in os.walk(tdir):
        if os.path.basename(dirpath) == tname:
            return os.path.join(tdir, dirpath)
    return None

def list_cmd(args):
    """Prints out all installed templates."""
    templates = list_templates(TEMPLATES_DIR)
    for template in templates:
        print('{0}'.format(template))

def create(args):
    """Creates a new paper given flags."""
    if os.path.exists(args.output) and not args.force:
        print('{0} exists, will not overwrite. Use -f to force creation.'.format(args.output))
        sys.exit(3)

    template_dir = find_template(args.template)

    if not template_dir:
        print('{0} is not an installed template.'.format(args.template))
        sys.exit(4)

    os.mkdir(args.output)
    giname = os.path.join(BASE_DIR, 'etc', 'example_paper', 'gitignore')
    shutil.copyfile(giname, os.path.join(args.output, '.gitignore'))

    #Create frontmatter section for paper
    front_file = os.path.join(template_dir, 'frontmatter.mmd')
    if os.path.exists(front_file):
        with open(front_file, 'r') as fp:
            paper = fp.read()
    else:
        paper = ''

    #Create metadata section
    metaex_file = os.path.join(template_dir, 'metadata.tex')
    if os.path.exists(metaex_file):
        with open(metaex_file, 'r') as fp:
            metadata = fp.read()
    else:
        metadata = ''

    for opt in args.config:
        repl = re.compile('${0}'.format(opt[0].upper()))
        repl.sub(opt[1], paper)
        repl.sub(opt[1], metadata)

    #Regex to find variable names
    var_re = re.compile(r'\$[A-Z0-9]+')
    paper_file = os.path.join(args.output, 'paper.mmd')
    with open(paper_file, 'w') as fp:
        fp.write(paper)
        fp.write('\n')
        fp.write('latex input: {0}/setup.tex\n'.format(args.template))
        fp.write('latex footer: {0}/footer.tex\n\n'.format(args.template))

    for ii in var_re.finditer(paper):
        print('{0} contains unpopulated variable {1}'.format(paper_file, ii.group(0)))

    if metadata:
        metadata_file = os.path.join(args.output, 'metadata.tex')
        with open(metadata_file, 'w') as fp:
            fp.write(metadata)
        for mtch in var_re.finditer(metadata):
            print('{0} contains unpopulated variable {1}'.format(metadata_file, mtch.group(0)))

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

    new_parser = subparsers.add_parser("new")
    new_parser.add_argument("output", help="Directory to create paper in.")
    new_parser.add_argument("-f", "--force", action="store_true", help="Overwrite files in paper creation.")
    new_parser.add_argument("-t", "--template", help="Template to use in paper.")
    new_parser.add_argument("-c", "--config", nargs=2, action='append', default=[],
                            help='Flag to provide options for filling out variables in new papers, in the form key value')
    new_parser.set_defaults(func=create)

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(func=list_cmd)

    args = parser.parse_args()

    args.func(args)