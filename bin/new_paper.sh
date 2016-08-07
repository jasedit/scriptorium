#!/bin/bash
# Create a new paper based on the example version.
# Author: Jason Ziglar <jpz@vt.edu>

function printUsage() {
  echo "new_paper.sh [-a author] [-g] [-f] [-o dir] [-t template] [-c config]"
  echo "-a author  : Sets the author name to insert in the new paper."
  echo "-g         : Use git to extract author information."
  echo "-f         : Forcibly create paper, overwriting files if necessary."
  echo "-o dir     : name of folder to store new paper in, under papers/"
  echo "-t template: name of template to use for this paper"
  echo "-c config  : file containing key-value pairs to attempt variable substitution."
  echo "             Config variable of NAME will replace $NAME in frontmatter."
}

function replaceValue() {
#Replaces the second argument with the third argument, in the file given as the first argument.
  if [ -z "$1" -o ! -f "$1" ]; then
    return
  fi
  if [ $(uname) = "Darwin" ]; then
    sed -i '' -e "s/\$${2}/${3}/g" "$1"
  else
    sed -i -e "s/\$${2}/${3}/g" "$1"
  fi
}

function enforceFinalNewline() {
  if [ -z "$1" -o ! -f "$1" ]; then
    return
  fi
  if [ $(uname) = "Darwin" ]; then
    sed -i '' -e '$a\' "$1"
  else
    sed -i -e '$a\' "$1"
  fi
}

#Use git to extract author info
use_git=0
#Forcibly create the paper
force=0
#Sets author name
author=""
#Output folder
folder=""
#Template name
template=""
#Configuration file for replacement values
config=""

while getopts "a:gfo:t:c:" flag; do
  case "$flag" in
    a) author=$OPTARG;;
    g) use_git=1;;
    f) force=1;;
    o) folder=$OPTARG;;
    t) template=$OPTARG;;
    c) config=$OPTARG;;
    *) printUsage; exit 1;;
  esac
done

#Test if arguments are set
if [ -z "$folder" -o -z "$template" ]; then
  printUsage
  exit 1
fi

#get current working directory, then go down one level for base
cur_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
abs_dir="${cur_dir}/.."

#Set up paper directory structure
if [ ! -d "${abs_dir}/papers" ]; then
  mkdir -p "${abs_dir}/papers"
fi

paper_dir="${abs_dir}/papers/$folder"

if [ -d "${paper_dir}" -a "$force" -eq "0" ]; then
  echo "Paper directory already exists, refusing to blow it away."
  exit 3
fi

mkdir $paper_dir

template_dir=$(find ${abs_dir}/templates -name ${template} -type d -print -quit)

if [ -z "$template_dir" ]; then
  echo "Could not find the ${template} template."
  exit 4
fi

ls $paper_dir
#Set up initial structure
cp -r "${abs_dir}/etc/example_paper/"* "$paper_dir"
mv "${paper_dir}/gitignore" "${paper_dir}/.gitignore"

if [ -z "$author" ]; then
  if [ "$use_git" -eq "1" ]; then
    author=$(git config user.name)
  else
    author="Replace Me"
  fi
fi

paper="${paper_dir}/paper.mmd"
metadata=""

#If the template comes with a frontmatter template, start with that file.
if [ -f "$template_dir/frontmatter.mmd" ]; then
  cp $template_dir/frontmatter.mmd "$paper"
fi

#Also grab the metadata.tex for a template, if it exists
if [ -f "${template_dir}/metadata.tex" ]; then
  cp "${template_dir}/metadata.tex" "${paper_dir}/metadata.tex"
  metadata="${paper_dir}/metadata.tex"
fi

enforceFinalNewline "$paper"

echo "latex input: $template/setup.tex" >> "$paper"
echo "latex footer: $template/footer.tex" >> "$paper"

#Sets the Author flag, wherever the template places it.
replaceValue "$paper.mmd" "AUTHOR" "${author}"
replaceValue "$metadata" "AUTHOR" "${author}"

#If a configuration file is given, replace all key/value pairs.
if [ -f "$config" ]; then
  OLDIFS=$IFS
  IFS='='
  while read line; do
      set -- $line
      if [ -n "$1" -a -n "$2" ]; then
        replaceValue "$paper" "$1" "$2"
        replaceValue "$metadata" "$1" "$2"
      fi
  done < "$config"
  IFS=$OLDIFS
fi

for ii in "$paper $metadata"; do
  if [ -n "$(grep -E '[$][[:alnum:]]+' $ii)" ]; then
    echo "WARNING: Substitution variables still undefined, please replace them or the paper will not build."
    break
  fi
done
