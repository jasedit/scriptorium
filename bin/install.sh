#!/bin/bash
# Installs the required tools for this repository for Ubuntu 14.04
# Author: Jason Ziglar <jpz@vt.edu>

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
abs_dir=`readlink -f "${dir}/.."`

#Install packages for Ubuntu
installLinux()
{
  codename=`lsb_release -c | cut -d':' -f2 | tr -d [:space:]`
  case $codename in
    trusty);;
    *) echo "${codename} not yet supported."; exit 1;;
  esac
  #Install from Debian Packages
  sudo apt-add-repository ppa:trecvt/ppa
  sudo apt-get update
  sudo apt-get install multimarkdown texlive latexmk texlive-latex-extra texlive-publishers
}

installCygwin()
{
  echo "Please install using Cygwin, as referenced in the README.";
}

installMac()
{
  echo "Please install MultiMarkdown from http://fletcherpenney.net/multimarkdown/download/";
}

os=`uname`

case $os in
  Linux) installLinux;;
  Darwin) installMac;;
  CYGWIN_NT*) installCygwin;;
  *) echo "$os is not currently supported. Please add support and submit a pull request, or file an issue."; exit 2;;
esac

$dir/setup_templates.sh
