#!/bin/bash
# Sets up the template repositories for the paper framework.
# Author: Jason Ziglar <jpz@vt.edu>

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
abs_dir=`readlink -f "${dir}/.."`

if [ ! -d "${abs_dir}/papers" ]; then
  read -p "Please provide a git repository to store templates within:" repo
  if [ -z "$repo" ]; then
    repo="https://github.com/TRECVT/peg-multimarkdown-latex-support.git"
  fi
  cur_dir=`pwd`
  cd $abs_dir
  git submodule add --force $repo common
  cd $cur_dir
fi

case `uname` in
  Darwin) latex_dir="~/Library/texmf/";;
  Linux) latex_dir="~/texmf";;
  *) echo "This platform not yet supported."; exit 1;;
  #Todo: Add Windows support
esac

mkdir -p "${latex_dir}"/tex/latex
mkdir -p "${latex_dir}"/bibtex

ln -s ${abs_dir}/common "${latex_dir}"/tex/latex/mmd
ln -s ${abs_dir}/common "${latex_dir}"/bibtex/bst
ln -s ${abs_dir}/common "${latex_dir}"/bibtex/bib