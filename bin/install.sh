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
    xenial);;
    *) echo "${codename} not yet supported."; exit 1;;
  esac
  sudo apt-get install texlive latexmk texlive-latex-extra texlive-publishers cmake
  mkdir ~/src
  old_wd=$(pwd)
  cd ~/src
  git clone https://github.com/jasedit/MultiMarkdown-5.git
  cd MultiMarkdown-5
  ./link_git_modules
  ./update_git_modules
  make
  cd build
  make
  cpack -G DEB
  sudo dpkg -i *.deb
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
