#!/usr/bin/env python
"""Installation and doctor oriented commands."""

import subprocess
import os
import platform
from collections import defaultdict

REQUIRED_PACKAGES = {
  'git': ['git'],
  'latex': ['pdflatex', 'biber'],
  'multimarkdown': ['multimarkdown']
}

SPLIT_TOKENS = {
    'Windows' : ';',
    'Darwin': ':',
    'linux': ':'
}

BINARY_EXT = defaultdict(str, [('Windows', '.exe')])

def required_binaries():
    """Return flat list of all binaries"""
    all_binaries = []
    for binaries in REQUIRED_BINARIES.values():
        all_binaries += binaries

    return all_binaries

def find_binaries(binaries):
    """Checks that all the required tools are installed."""
    found_binaries = set()

    system = platform.system()
    for binary in binaries:
        for path in os.environ['PATH'].split(SPLIT_TOKENS[system]):
            binary_path = os.path.join(path, binary + BINARY_EXT[system])
            #Test if path is an executable file
            if os.path.isfile(binary_path) and os.access(binary_path, os.X_OK):
                found_binaries.add(binary)
                break

    return found_binaries

def find_missing_packages():
    missing_packages = {}
    for package, binaries in REQUIRED_PACKAGES.items():
        if not find_binaries(binaries):
          if package not in missing_packages:
              missing_packages[package] = []
          missing_packages[package].append(package)
          continue
    return missing_packages

def find_missing_binaries():
    """Return list of missing binaries."""
    missing_binaries = []
    missing_packages = find_missing_packages()
    for package, binaries in missing_packages:
        missing_binaries += binaries
    return missing_binaries