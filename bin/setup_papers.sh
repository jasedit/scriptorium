#!/bin/bash
# Sets up the actual paper repository for papers_base.
# Author: Jason Ziglar <jpz@vt.edu>

#get current working directory, then go down one level for base
dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
abs_dir="${dir}/.."

if [ ! -d "${abs_dir}/papers" ]; then
  read -p "Please provide a git repository to point at to store papers:" repo
  git submodule add --force $repo "${abs_dir}"/papers
else
  exit 0
fi