texfile=report
bibfile=thesis

pdf: compile
	pdflatex ${texfile}

compile:
	latex ${texfile}
	bibtex ${texfile}
	latex ${texfile}

clean:
	rm ${texfile}.aux ${texfile}.bbl ${texfile}.blg ${texfile}.dvi ${texfile}.log ${texfile}.toc ${texfile}.pdf
