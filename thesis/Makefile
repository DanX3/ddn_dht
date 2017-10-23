TARGET=00_main.pdf
SRCS=$(shell find -type f -name "*.tex")
BIBFILE=references.bib

all: $(TARGET)

test:$(SRCS)
	pdflatex 00_main.tex

$(TARGET): $(SRCS) $(BIBFILE)
	@pdflatex 00_main.tex > /dev/null
	@rm -f *.bbl *.blg && bibtex 00_main
	@pdflatex 00_main.tex > /dev/null
	@pdflatex 00_main.tex > /dev/null

bib: $(BIBFILE)
	rm -f *.bbl *.blg && bibtex 00_main

print:
	@echo $(SRCS)

clean: softclean
	rm -f *.pdf

softclean:
	rm -f *.toc *.aux *.log *.dvi *.bbl *.blg
