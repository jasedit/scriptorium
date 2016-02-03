#!/bin/bash
# Create a new paper based on the example version.
# Author: Jason Ziglar <jpz@vt.edu>

function printUsage() {
  echo "new_paper.sh folder_name template_name"
  echo "folder_name : name of folder to store new paper in, under papers/"
  echo "template_name : name of template to use for this paper"
}

#Test if arguments are set
if [ $# -ne 2 ]; then
  printUsage
  exit 1
fi

#get current working directory, then go down one level for base
dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
abs_dir="${dir}/.."

paper_dir="${abs_dir}/papers/$1"

if [ ! -d "${abs_dir}/papers" ]; then
  echo "Papers directory does not exist."
  printUsage
  exit 2
fi

if [ -d "${paper_dir}" ]; then
  echo "Paper directory already exists, refusing to blow it away."
  exit 3
fi

mkdir -p $paper_dir
cp -r "${abs_dir}"/etc/example_paper/* $paper_dir
mv "${paper_dir}"/gitignore "${paper_dir}"/.gitignore

if [ `uname` = "Darwin" ]; then
  sed -i '' -e "s/TEMPLATE/${2}/g" "${paper_dir}"/paper.mmd
else
  sed -i -e "s/TEMPLATE/${2}/g" "${paper_dir}"/paper.mmd
fi
