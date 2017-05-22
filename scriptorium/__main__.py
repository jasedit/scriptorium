#!/usr/bin/env python
#Script to build a scriptorium paper in a cross-platform friendly fashion

import argparse
import argcomplete
import shutil
import sys
import os
import os.path
import yaml

import scriptorium

def build_cmd(args):
    """Creates PDF from paper in the requested location."""
    pdf = scriptorium.to_pdf(args.paper, use_shell_escape=args.shell_escape, flatten=args.flatten,
                                            keep_comments=args.keep_comments)

    if args.output and pdf != args.output:
        shutil.move(pdf, args.output)

def info(args):
    """Function to attempt to extract useful information from a specified paper."""
    fname = scriptorium.paper_root(args.paper)

    if not fname:
        print('{0} does not contain a valid root document.'.format(args.paper))
        sys.exit(1)

    if args.template:
        template = scriptorium.get_template(os.path.join(args.paper, fname))
        if not template:
            print('Could not find footer indicating template name.')
            sys.exit(2)
        print(template)

def template_cmd(args):
    """Prints out all installed templates."""
    if args.update:
        rev = args.update[1] if len(args.update) > 1 else None
        scriptorium.update_template(args.update[0], args.template_dir, rev)

    if args.list:
        templates = scriptorium.all_templates(args.template_dir)
        print('\n'.join(templates))

    if args.readme:
        template = scriptorium.find_template(args.readme, args.template_dir)
        template_readme = os.path.join(template, 'README.md')
        if template and os.path.exists(template_readme):
            with open(template_readme, 'r') as readme:
                print(readme.read())

    if args.install:
        scriptorium.install_template(args.install, args.template_dir)

    if args.variables:
        variables = scriptorium.list_variables(args.variables, args.template_dir)
        print('\n'.join(variables))

    if args.manifest:
        manifest = scriptorium.get_manifest(args.manifest, args.template_dir)

        for kk, vv in manifest.items():
            print("{0} -> {1}".format(vv, kk))

def create_cmd(args):
    """Creates a new paper given flags."""
    config = {kk:vv for kk, vv in args.config}
    unset_vars = scriptorium.create(args.output, args.template, force=args.force, config=config)
    if unset_vars:
        if not args.quiet:
            print('WARNING: Variables are unset! Build will fail until they are defined')
            for vname in unset_vars:
                print('${0}'.format(vname.upper()))
        sys.exit(3)

def doctor_cmd(_):
    """Command for checking the health of scriptorium."""
    missing_packages = scriptorium.find_missing_packages()
    if missing_packages:
        for package in missing_packages:
            print('Missing package {0}\n'.format(package))

def config_cmd(args):
    """Command to access configuration values."""
    if args.list:
        print(yaml.dump(scriptorium.CONFIG, default_flow_style=False))
    elif len(args.value) == 1:
        print(yaml.dump({args.value[0] : scriptorium.CONFIG[args.value[0]]}))
    elif len(args.value) == 2:
        scriptorium.CONFIG[args.value[0].upper()] = args.value[1]
        scriptorium.save_config()

def clean_cmd(args):
    """Command to clean cruft from current directory."""
    scriptorium.clean(args.paper)

def main():
    """Main function for executing scriptorium as a standalone script."""
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--version', action="store_true")

    subparsers = parser.add_subparsers()

    # Build Command
    build_parser = subparsers.add_parser('build')
    build_parser.add_argument('paper', default='.', nargs='?',
                              help='Directory containing paper to build')
    build_parser.add_argument('-o', '--output', help='Destination of PDF')
    build_parser.add_argument('-s', '--shell-escape', action='store_true', default=False,
                              help='Flag indicating shell-escape should be used')
    build_parser.add_argument('-f', '--flatten', action='store_true', default=False,
                              help='Flatten root LaTeX file output')
    build_parser.add_argument('-k', '--keep-comments', action='store_true', default=False,
                              help='Keep comments when flattening the resulting LaTeX file')
    build_parser.set_defaults(func=build_cmd)

    # Info Command
    info_parser = subparsers.add_parser('info')
    info_parser.add_argument('paper', default='.', nargs='?',
                             help='Directory containing paper to make')
    info_parser.add_argument('-t', '--template', action='store_true',
                             help='Flag to extract template')
    info_parser.set_defaults(func=info)

    # New Command
    new_parser = subparsers.add_parser("new")
    new_parser.add_argument("output", help="Directory to create paper in.")
    new_parser.add_argument("-f", "--force", action="store_true",
                            help="Overwrite files in paper creation.")
    new_parser.add_argument("-t", "--template", help="Template to use in paper.")
    new_parser.add_argument("-c", "--config", nargs=2, action='append', default=[],
                            help='Provide "key" "value" to replace in default paper.')
    new_parser.add_argument('-q', '--quiet', action='store_true', default=False,
                            help='Squelch warnings about unset variables')
    new_parser.set_defaults(func=create_cmd)

    # Template Command
    template_parser = subparsers.add_parser("template")
    template_parser.add_argument('-l', '--list', action='store_true', default=False,
                                 help='List available templates')
    template_parser.add_argument('-u', '--update', nargs='+',
                                 help='Update the given template to the latest version')
    template_parser.add_argument('-r', '--readme', help='Print README for the specified template')
    template_parser.add_argument('-d', '--template_dir', default=None,
                                 help='Overrides template directory used for listing templates')
    template_parser.add_argument('-i', '--install',
                                 help='Install repository at given URL in template directory')
    template_parser.add_argument('-v', '--variables',
                                 help='List variables available when using the new command')
    template_parser.add_argument('-m', '--manifest',
                                help='List the manifest of files this template provides for new documents')
    template_parser.set_defaults(func=template_cmd)

    # Doctor Command
    doctor_parser = subparsers.add_parser('doctor')
    doctor_parser.set_defaults(func=doctor_cmd)

    # Config Command
    config_parser = subparsers.add_parser('config')
    config_parser.add_argument('-l', '--list', action='store_true',
                               help='List available configuration options and current vaules')
    config_parser.add_argument('value', nargs='*', help='Access configuration value')
    config_parser.set_defaults(func=config_cmd)

    #Clean Command
    clean_parser = subparsers.add_parser('clean')
    clean_parser.add_argument('paper', default='.', nargs='?', help='Directory containing paper to clean')
    clean_parser.set_defaults(func=clean_cmd)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.version:
        print(scriptorium.__version__)
        return 0

    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    # Only save configuration with main
    main()
