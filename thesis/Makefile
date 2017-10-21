TARGET=thesis.pdf
SRCS=$(shell find -type f -name "*.tex")

all: $(TARGET)

$(TARGET): $(SRCS)
	@# As it seems, some changes need 2 runs to be effective, so then...
	pdflatex 00_main.tex
	pdflatex 00_main.tex

bib:
	rm -f *.bbl *.blg
	bibtex 00_main

print:
	@echo $(SRCS)

clean: softclean
	rm -f *.pdf

softclean:
	rm -f *.toc *.aux *.log *.dvi *.bbl *.blg
