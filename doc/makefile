texfile=report
bibfile=thesis

all: pdf

pdf: compile
	pdflatex ${texfile}

compile:
	pdflatex ${texfile}
	bibtex ${texfile}
	pdflatex ${texfile}

clean:
	rm ${texfile}.aux ${texfile}.out ${texfile}.bbl ${texfile}.blg \
	${texfile}.log ${texfile}.toc ${texfile}.pdf
