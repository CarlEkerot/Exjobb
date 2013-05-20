texfile=report
bibfile=thesis
slidesfile=slides

all: pdf

pdf: compile
	pdflatex ${texfile}

compile:
	pdflatex ${texfile}
	bibtex ${texfile}
	pdflatex ${texfile}

slides:
	xelatex ${slidesfile}

clean:
	rm ${texfile}.aux ${texfile}.bbl ${texfile}.blg ${texfile}.log ${texfile}.toc \
	rm ${slidesfile}.aux ${slidesfile}.log ${slidesfile}.pdf ${slidesfile}.toc ${slidesfile}.snm ${slidesfile}.nav ${slidesfile}.out
