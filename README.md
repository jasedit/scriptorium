# papers_base

Repository creating a framework for providing a MultiMarkdown and LaTeX based system for easily writing academic papers.

This repository provides a framework for a research group to develop a common setup for writing academic papers. This aims to be easy to use, scalable, and re-usable between labs. The system breaks down into three main areas:

1. [MultiMarkdown](http://fletcherpenney.net/multimarkdown/) templating - A framework extending the MultiMarkdown [Latex support](https://github.com/fletcher/peg-multimarkdown-latex-support) to provide a method for pulling in LaTeX templates for various academic conferences/journals.
2. Papers as a submodule. Since papers in development are generally not open-source, this framework pushes papers as a user-definable submodule. This way, any lab can keep their actual academic text in a private repository, while the templates and framework can be left open-source.
3. This repository - the glue logic which makes this system as easy to use as possible.

# Installation

Installation is broken down into two separate phases, depending on which part of the system is being built: first time setup for a group, or first time setup for an end user.

## Group Setup Instructions

1. Fork this repository. This repository will be modified during your group's usage of it, so you want to create your own fork for general use. The only proprietary information which should be directly stored in this repository is where your two submodules exist.
2. Select a template repository. An bare-bones repository is available [here](https://github.com/TRECVT/peg-multimarkdown-latex-support), which contains the barebones latex support. It is likely that your group will want to fork this repository and begin building up the set of templates which correspond to common papers being written in the lab.
3. Create a papers repository. This should be a git repository that has the appropriate level of protection for your papers.
4. Clone your forked version of this repository to a machine.
5. Run `./bin/setup_templates.sh` in the cloned repository, and specify the desired template repository location.
6. Run `./bin/setup_papers.sh` in the cloned repository, and specify the desired papers repository location.
7. Commit and push the new submodule configuration to your base repository for others to share.

## End User Setup

1. Clone the base reposotiry corresponding to the group you want to use. It is best if you include use the `--recursive` flag, so all submodules are checked out as part of the initial clone.

### Ubuntu 14.04 Setup

1. Run `bin/install.sh` to install multimarkdown and latex packages necessary for this system to build.
2. Run `./bin/setup_templates.sh` to symlink the templates for multimarkdown.

### Windows Setup

1. Install Cygwin from http://cygwin.com/
2. Make sure the following Cygwin packages are installed: texlive, texlive-collection-latexextra, texlive-collection-publishers, git, openssh, make, libglib2.0-devel, gcc-core, gcc-g++
3. Once cygwin is installed, open up the Cygwin terminal for the following steps.
4. Set up an SSH key. The easiest way is to execute "ssh-keygen" and follow the prompts.
5. Add the public key to GitHub.
6. Clone Multimarkdown with the following command: `git clone --recursive git@github.com:fletcher/peg-multimarkdown-latex-support.git $MMD_DIR`, where `$MMD_DIR` is a location to download the MultiMarkdown source code.
7. `cd $MMD_DIR; make; make install`
8. `git clone --recursive $PAPER_REPO $PAPER_DIR` where `$PAPER_REPO` is your paper repository, and `$PAPER_DIR` is the location to save the papers.
9. `cd $PAPER_REPO/bin; ./steup_templates.sh`

## Creating a new paper

This repository provides a base example paper for creating new papers using this framework. To create a new paper, you can execute `./bin/new_paper.sh paper_name template_name`, where `paper_name` and `template_name` are the name of the subfolder in papers to save the paper in, and the name of the folder inside common containing the template to use for this paper, respectively. As an example, a new paper named `my_conference_paper` using the IEEE conference template can be created by invoking:
```
./bin/new_paper.sh my_conference_paper ieee
```

## Creating a new template

A template defines the latex setup defining how a paper is going to be laid out, which packages it will use, etc. A template is made in three steps:

1. A folder inside the common directory. The name of this folder is what is used to reference the template in a MultiMarkdown paper by the `latex template` metadata.
2. A LaTeX file named `setup.tex` inside this folder, which contains the template preamble. The preamble should include everything at the start of the document before the content, through the `\begin{document}` statement. More may be included in this preamble, such as seen in the IEEE example.
3. a LaTeX file named `footer.tex` inside this folder, which contains any LaTeX which should be appended to the end of the file. This often includes the biliography commands. The IEEE `footer.tex` file is a good example of such a footer.