papers_base
===========

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


## Creating a new paper

This repository provides a base example paper for creating new papers using this framework. To create a new paper, you can execute `./bin/new_paper.sh paper_name template_name`, where `paper_name` and `template_name` are the name of the subfolder in papers to save the paper in, and the template to set the paper to use, respectively.