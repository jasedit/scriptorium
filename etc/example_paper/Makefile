all:
	multimarkdown -t latex -o paper.tex paper.mmd
	pdflatex paper.tex
	#bibtex paper.aux
	pdflatex paper.tex

clean:
	rm -rf $(document) *.lof *.lot *.glg *.gls *.glo *.idx *.log *.out *.toc *.ist *.aux *.dvi *.bbl *.blg *.ps *.pdf

.PHONY: all clean
