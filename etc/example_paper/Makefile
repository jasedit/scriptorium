all:
	multimarkdown -t latex -o paper.tex paper.mmd
	pdflatex paper.tex
	#biber paper.aux
	pdflatex paper.tex

clean:
	rm -rf $(document) *.lof *.lot *.glg *.gls *.glo *.idx *.log *.out *.toc *.ist *.aux *.dvi *.bbl *.blg *.ps *.pdf paper.tex

.PHONY: all clean
