#!/usr/bin/env python
#Script to build a scriptorium paper in a cross-platform friendly fashion

import scriptorium
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

def make(args):
    """Creates PDF from paper in the requested location."""
    pdf = scriptorium.to_pdf(args.paper, TEMPLATES_DIR, args.shell_escape)

    if args.output and pdf != args.output:
        shutil.move(pdf, args.output)

def info(args):
    """Function to attempt to extract useful information from a specified paper."""
    fname = scriptorium.paper_root(args.paper)

    if not fname:
        raise IOError('{0} does not contain a valid root document.'.format(args.paper))

    if not fname:
        print('Could not find the root of the paper.')
        sys.exit(1)

    if args.template:
        template = scriptorium.get_template(os.path.join(args.paper, fname))
        if not template:
            print('Could not find footer indicating template name.')
            sys.exit(2)
        print(template)

def list_cmd(args):
    """Prints out all installed templates."""
    templates = scriptorium.all_templates(TEMPLATES_DIR)
    for template in templates:
        print('{0}'.format(template))

def create(args):
    """Creates a new paper given flags."""
    if os.path.exists(args.output) and not args.force:
        print('{0} exists, will not overwrite. Use -f to force creation.'.format(args.output))
        sys.exit(3)

    template_dir = scriptorium.find_template(args.template, TEMPLATES_DIR)

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

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers()

make_parser = subparsers.add_parser("make")

make_parser.add_argument("paper", default=".", help="Directory containing paper to make")
make_parser.add_argument('-o', '--output', help='Filename to store resulting PDF as.')
make_parser.add_argument('-s', '--shell-escape', action='store_true', help='Flag to indicate shell-escape should be used')
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