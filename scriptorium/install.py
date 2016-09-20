#!/usr/bin/env python
"""Installation and doctor oriented commands."""

import subprocess
import os
import platform
from collections import defaultdict

REQUIRED_BINARIES = ['git', 'pdflatex', 'multimarkdown', 'biber']

SPLIT_TOKENS = {
    'Windows' : ';',
    'Darwin': ':',
    'linux': ':'
}

BINARY_EXT = defaultdict(str, [('Windows', '.exe')])

def find_binaries():
    """Checks that all the required tools are installed."""
    open_binaries = set(REQUIRED_BINARIES)
    found_binaries = set()

    system = platform.system()
    for path in os.environ['PATH'].split(SPLIT_TOKENS[system]):
        new_binaries = set()
        for binary in open_binaries:
            binary_path = os.path.join(path, binary + BINARY_EXT[system])
            #Test if path is an executable file
            if os.path.isfile(binary_path) and os.access(binary_path, os.X_OK):
                new_binaries.add(binary)
        open_binaries -= new_binaries
        found_binaries |= new_binaries

    return found_binaries

def missing_binaries():
    """Return list of missing binaries."""
    return set(REQUIRED_BINARIES) - find_binaries()