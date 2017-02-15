"""Setuptools file for a MultiMarkdown Python wrapper."""
import os
import re
from distutils.core import setup
from setuptools import find_packages
import pypandoc

with open(os.path.join('scriptorium', '_version.py'), 'r') as vfp:
    vtext = vfp.read()
    v_re = r"__version__ = \"(?P<ver>.*)\""
    mo = re.search(v_re, vtext)
    VER = mo.group("ver")

LONG_DESC = pypandoc.convert_file('README.md', 'rst')

setup(
    name='scriptorium',
    version=VER,
    description='Multimarkdown and LaTeX framework for academic papers.',
    long_description=LONG_DESC,
    license='MIT',
    author='Jason Ziglar',
    author_email='jasedit@gmail.com',
    url="https://github.com/jasedit/scriptorium",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Filters',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': ['scriptorium = scriptorium:main'],
    },
    package_data={'scriptorium': ['data/gitignore']},
    install_requires=[
        'pyyaml',
        'argcomplete',
        'pymmd>=0.3'
    ]
    )
