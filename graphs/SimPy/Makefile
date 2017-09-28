SRCS=$(shell find . -name "[A-Z]*.py")

all: $(SRCS)
	python3.5 Simulator.py

print:
	@echo $(SRCS)

doc: $(SRCS) Doxyfile
	doxygen Doxyfile

profile: $(SRCS)
	pypy3 -m vmprof --lines -o profile_data Simulator.py 
	grep -e "/SimPy/" profile_data
