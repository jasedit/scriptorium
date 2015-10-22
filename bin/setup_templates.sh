#!/bin/bash
# Sets up the template submodule for the paper framework.
# Author: Jason Ziglar <jpz@vt.edu>

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
abs_dir="${dir}/.."

if [ ! -d "${abs_dir}/common" ]; then
  read -p "Please provide a git repository to store templates within:" repo
  if [ -z "$repo" ]; then
    repo="https://github.com/fletcher/peg-multimarkdown-latex-support.git"
  fi
  cur_dir=`pwd`
  cd $abs_dir
  git submodule add --force $repo common
  cd $cur_dir
fi

case `uname` in
  Darwin) latex_dir="${HOME}/Library/texmf";;
  Linux) latex_dir="${HOME}/texmf";;
  CYGWIN_NT*) latex_dir="${HOME}/.config/texmf";;
  *) echo "This platform not yet supported."; exit 1;;
esac

mkdir -p "${latex_dir}"/tex/latex
mkdir -p "${latex_dir}"/bibtex

mmd_dir="${latex_dir}/tex/latex/mmd"
bst_dir="${latex_dir}/bibtex/bst"
bib_dir="${latex_dir}/bibtex/bib"

if [ -d "${latex_dir}"/tex/latex/mmd ]; then
  echo "Directories for LaTeX already exist, which is problematic. Please determine if the following directories are correct, or remove them and run again."
  echo $mmd_dir
  echo $bst_dir
  echo $bib_dir
else
  ln -s ${abs_dir}/common $mmd_dir
  ln -s ${abs_dir}/common $bst_dir
  ln -s ${abs_dir}/common $bib_dir
fi

echo "Looking for dir ${abs_dir}"
mmdl_dir=`grep "${abs_dir}/templates" ~/.bashrc`
echo "Done"
#Environment variable not defined, inject one for this repository
if [ -z "$mmdl_dir" ]; then
  echo "Configuring .bashrc"
  echo "export TEXINPUTS=${abs_dir}/templates/.//:$TEXINPUTS:" >> ~/.bashrc
fi