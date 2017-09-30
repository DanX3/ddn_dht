SRCS=$(shell find . -name "[A-Z]*.py")
PROFILEOUT=profile_data
PROFILELINES=profile_lines
FLAME=profile.flame
FLAMEIMG=profile.svg
FLAMEOPTS= --title "IME Simulation" --width 3000 --colors red --fontsize 10

all: $(SRCS)
	pypy3 Simulator.py

print:
	@echo $(SRCS)

doc: $(SRCS) Doxyfile
	doxygen Doxyfile

lineprofile: $(SRCS)
	python3 -m vmprof --lines -o $(PROFILEOUT) Simulator.py 
	vmprofshow --lines $(PROFILEOUT) > $(PROFILELINES)
	less $(PROFILELINES)

profile: $(SRCS)
	pypy3 -m vmprof -o $(PROFILEOUT) Simulator.py
	vmprofshow $(PROFILEOUT) | head -30

flame: $(SRCS)
	python3 -m vmprof --lines -o $(PROFILEOUT) Simulator.py
	vmprof-flamegraph.py $(PROFILEOUT) > $(FLAME)
	flamegraph.pl $(FLAMEOPTS) $(FLAME) > $(FLAMEIMG)
	eog $(FLAMEIMG)
