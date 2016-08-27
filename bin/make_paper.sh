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

#The root document for this is the one which contains frontmatter, or metadata
for file in $(ls *.mmd); do
  if [ -n "$(multimarkdown -m $file)" ]; then
    paper=$file
    break
  fi
done

if [ -z "$paper" ]; then
  echo "No .mmd file contains metadata, which is required for interfacing with scriptorium. Cannot continue."
  exit 1
fi

tex_file="./$(basename $paper).tex"

/usr/local/bin/multimarkdown -t latex -o "$tex_file" "$paper"

if [ $? != 0 ]; then
  exit 1
fi

pdflatex -shell-escape "$tex_file"

if [ $? != 0 ]; then
  exit 1
fi

#Test if paper is using a bibliography or not
full_paper=$(latexpand "$tex_file")
if [ -n "$(echo $paper | grep bibtex:)" ]; then
  if [ -n "$(echo $full_paper | grep backend=biber)" ]; then
    biber paper
  else
    bibtex paper.aux
  fi
fi

pdflatex -shell-escape "$tex_file"
pdflatex -shell-escape "$tex_file"

# Revert to old directory
if [ "$old_cwd" != "$(pwd)" ]; then
  cd "$old_cwd"
fi
