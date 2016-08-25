#!/bin/bash
# Installs the required tools for this repository for Ubuntu 14.04
# Author: Jason Ziglar <jpz@vt.edu>

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
abs_dir=`readlink -f "${dir}/.."`

installMMD5Linux()
{
  cpack -G DEB
  sudo dpkg -i *.deb
}

installMMD5Mac()
{
  sudo make install
}

installMMD5Cygwin()
{
  sudo make install
}

installMMD5()
{
  mkdir ~/src
  old_wd=$(pwd)
  cd ~/src
  git clone https://github.com/fletcher/MultiMarkdown-5.git
  cd MultiMarkdown-5
  ./link_git_modules
  ./update_git_modules
  make shared
  cd build
  make

  case $(uname) in
    Linux) installMMD5Linux;;
    Darwin) installMMD5Mac;;
    Cygwin_NT) installMMD5Cygwin;;
  esac

  cd $old_wd
}

#Install packages for Ubuntu
installLinux()
{
  codename=$(lsb_release -c | cut -d':' -f2 | tr -d [:space:])
  case $codename in
    trusty);;
    xenial);;
    *) echo "${codename} not yet supported."; exit 1;;
  esac
  sudo apt-get install texlive latexmk texlive-latex-extra texlive-publishers cmake
  installMMD5

}

installCygwin()
{
  installMMD5
}

installMac()
{
  installMMD5
}

os=$(uname)

case $os in
  Linux) installLinux;;
  Darwin) installMac;;
  CYGWIN_NT*) installCygwin;;
  *) echo "$os is not currently supported. Please add support and submit a pull request, or file an issue."; exit 2;;
esac

$dir/setup_templates.sh
