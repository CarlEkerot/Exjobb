texfile=report
bibfile=thesis
slidesfile=slides
articlefile=article
notesfile=slides_notes

all: pdf

pdf: compile
	pdflatex ${texfile}

compile:
	pdflatex ${texfile}
	bibtex ${texfile}
	pdflatex ${texfile}

slides:
	xelatex ${slidesfile}

notes:
	xelatex ${notesfile}

article:
	pdflatex ${articlefile}

clean:
	rm ${texfile}.aux ${texfile}.out ${texfile}.bbl ${texfile}.blg \
	${texfile}.log ${texfile}.toc \
	${slidesfile}.aux ${slidesfile}.log ${slidesfile}.pdf ${slidesfile}.toc \
	${slidesfile}.snm ${slidesfile}.nav ${slidesfile}.out \
	${articlefile}.aux ${articlefile}.log ${articlefile}.pdf
