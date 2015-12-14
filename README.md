# papers_base

Repository creating a framework for providing a MultiMarkdown and LaTeX based system for easily writing academic papers.

This repository provides a framework for a research group to develop a common setup for writing academic papers. This aims to be easy to use, scalable, and re-usable between labs. The system breaks down into three main areas:

1. [MultiMarkdown](http://fletcherpenney.net/multimarkdown/) templating - A framework extending the MultiMarkdown [Latex support](https://github.com/fletcher/peg-multimarkdown-latex-support) to provide a method for pulling in LaTeX templates for various academic conferences/journals.
2. Papers as a submodule. Since papers in development are generally not open-source, this framework pushes papers as a user-definable submodule. This way, any lab can keep their actual academic text in a private repository, while the templates and framework can be left open-source.
3. This repository - the glue logic which makes this system as easy to use as possible.

# Installation

1. Clone this repository to your local machine.
2. Follow the installation instructions for your platform of choice below.
3. Clone some number of template repositories under the templates folder. This repository does not track those repositories, so the base repository can be shared publicly, and templates can be distributed in whatever organization makes sense for individual groups/projects.

### Ubuntu 14.04 Setup

1. Run `bin/install.sh` to install MultiMarkdown and latex packages necessary for this system to build.
2. From inside the repository, run `./bin/setup_templates.sh` in the cloned repository, and specify the desired MultiMarkdown LaTeX support repository. The default is set to the official [repository](https://github.com/fletcher/peg-multimarkdown-latex-support). **NOTE:** This script injects an environment variable, `TEXINPUTS`, into your .bashrc file to enable building files appropriately.

### Windows Setup

1. Install Cygwin from http://cygwin.com/
2. Make sure the following Cygwin packages are installed: texlive, texlive-collection-latexextra, texlive-collection-publishers, git, openssh, make, libglib2.0-devel, gcc-core, gcc-g++, and texlive-fonts-recommended
3. Once cygwin is installed, open up the Cygwin terminal for the following steps.
4. Set up an SSH key. The easiest way is to execute `ssh-keygen` and follow the prompts.
5. Add the public key to GitHub.
6. Clone MultiMarkdown with the following command: `git clone --recursive git@github.com:fletcher/MultiMarkdown-4.git $MMD_DIR`, where `$MMD_DIR` is a location to download the MultiMarkdown source code.
7. `cd $MMD_DIR; make; make install`
8. `git clone --recursive $PAPER_REPO $PAPER_DIR` where `$PAPER_REPO` is your paper repository, and `$PAPER_DIR` is the location to save the papers.
9. From inside the repository, run `./bin/setup_templates.sh` in the cloned repository, and specify the desired MultiMarkdown LaTeX support repository. The default is set to the official [repository](https://github.com/fletcher/peg-multimarkdown-latex-support). **NOTE:** This script injects an environment variable, `TEXINPUTS`, into your .bashrc file to enable building files appropriately.

## Creating a new paper

This repository provides a base example paper for creating new papers using this framework. To create a new paper, you can execute `./bin/new_paper.sh paper_name template_name`, where `paper_name` and `template_name` are the name of the subfolder in papers to save the paper in, and the name of the folder inside common containing the template to use for this paper, respectively. Note that the paper location should include the path into the paper repository, and the path will be created as specified. As an example, a new paper named `my_conference_paper` inside the `my_papers` subdirectory of papers using the IEEE conference template can be created by invoking:
```
./bin/new_paper.sh my_papers/my_conference_paper ieee
```
which will create a skeleton paper in `papers/my_papers/my_conference_paper`.

## Creating a new template

A template defines the latex setup defining how a paper is going to be laid out, which packages it will use, etc. A template is made in a few steps:

1. A folder inside the templates directory. The name of this folder is what is used to reference the template in a MultiMarkdown paper, by LaTeX's recursive subdirectory search.
2. A LaTeX file named `setup.tex` inside this folder, which contains the template preamble. The preamble should include everything at the start of the document before the content, through the `\begin{document}` statement. More may be included in this preamble, such as seen in the IEEE example.
3. A LaTeX file named `footer.tex` inside this folder, which contains any LaTeX which should be appended to the end of the file. This often includes the bibliography commands. The IEEE `footer.tex` file is a good example of such a footer.