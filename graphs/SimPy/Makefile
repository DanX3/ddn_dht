SRCS=$(shell find . -name "[A-Z]*.py")

all: $(SRCS)
	python3.5 Simulator.py

print:
	@echo $(SRCS)

doc: $(SRCS) Doxyfile
	doxygen Doxyfile
