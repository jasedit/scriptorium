#!/bin/bash
# Sets up the actual paper repository for papers_base.
# Author: Jason Ziglar <jpz@vt.edu>

#get current working directory, then go down one level for base
dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
abs_dir="${dir}/.."

if [ ! -d "${abs_dir}/papers" ]; then
  cur_dir=`pwd`
  read -p "Please provide a git repository to point at to store papers:" repo
  cd $abs_dir
  git submodule add --force $repo papers
  cd $cur_dir
else
  exit 0
fi