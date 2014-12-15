#!/bin/bash
# Installs the required tools for this repository for Ubuntu 14.04
# Author: Jason Ziglar <jpz@vt.edu>

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
abs_dir=`readlink -f "${dir}/.."`

sudo apt-add-repository ppa:trecvt/ppa
sudo apt-get update
sudo apt-get install multimarkdown texlive latexmk texlive-latex-extra

$dir/setup_templates.sh
