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

def make(args):
    """Creates PDF from paper in the requested location."""
    pdf = scriptorium.to_pdf(args.paper, use_shell_escape=args.shell_escape)

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
    if not scriptorium.create(args.output, args.template, force=args.force, config=args.config):
        sys.exit(3)

def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    # Make command
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
    list_parser.add_argument("-t", "--template_dir", default=scriptorium.TEMPLATES_DIR, help="Overrides template directory used for listing templates")
    list_parser.set_defaults(func=list_cmd)

    args = parser.parse_args()

    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()