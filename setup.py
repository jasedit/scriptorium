"""Setuptools file for a MultiMarkdown Python wrapper."""
from codecs import open
from os import path
from distutils.core import setup
from setuptools import find_packages
import pypandoc

here = path.abspath(path.dirname(__file__))

long_description = pypandoc.convert_file('README.md', 'rst')

setup(
    name='scriptorium',
    version='2.2.2',
    description='Multimarkdown and LaTeX framework for academic papers.',
    long_description=long_description,
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
    entry_points = {
        'console_scripts': ['scriptorium = scriptorium:main'],
    },
    package_data={'scriptorium': ['data/gitignore']},
    install_requires=['pyyaml', 'argcomplete', 'pymmd']
    )
