#!/bin/bash
#Author: Jason Ziglar <jpz@vt.edu>
#Script to automate making papers using Scriptorium, which is useful for
#automating paper building in a slightly safer fashion.
cur_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
abs_dir="${cur_dir}/.."

export TEXINPUTS=".:${abs_dir}/templates/.//:$TEXINPUTS"

old_cwd=$(pwd)
#change to specified directory, if given
if [ -n "$1" ]; then
  cd $1
fi

/usr/local/bin/multimarkdown -t latex -o ./paper.tex paper.mmd

if [ $? != 0 ]; then
  exit 1
fi

pdflatex -shell-escape paper.tex

if [ $? != 0 ]; then
  exit 1
fi

#Test if paper is using a bibliography or not
full_paper=$(latexpand paper.tex)
if [ -n "$(echo $paper.mmd | grep bibtex:)" ]; then
  if [ -n "$(echo $full_paper | grep backend=biber)" ]; then
    biber paper
  else
    bibtex paper.aux
  fi
fi

pdflatex -shell-escape paper.tex
pdflatex -shell-escape paper.tex

# Revert to old directory
if [ "$old_cwd" != "$(pwd)" ]; then
  cd "$old_cwd"
fi
