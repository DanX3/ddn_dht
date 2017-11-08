CC=python3.5
SRCS=$(shell find . -name "[A-Z]*.py")
PROFILEOUT=profile_data
PROFILELINES=profile_lines
FLAME=profile.flame
FLAMEIMG=profile.svg
FLAMEOPTS= --title "IME Simulation" --colors blue

all: $(SRCS) accelerated.so
	cd src/ && time $(CC) Simulator.py --request ../request
	gnuplot plot.plt

accelerated.so: accelerated.c
	gcc -shared -o accelerated.so -fPIC -Wall -O2 $<

print:
	@echo $(SRCS)

doc: $(SRCS) Doxyfile
	doxygen Doxyfile

lineprofile: $(SRCS)
	cd src/ && $(CC) -m vmprof --lines -o $(PROFILEOUT) Simulator.py && mv $(PROFILEOUT) ../
	vmprofshow --lines $(PROFILEOUT) > $(PROFILELINES)
	less $(PROFILELINES)

profile: $(SRCS)
	$(CC) -m vmprof -o $(PROFILEOUT) src/Simulator.py
	vmprofshow $(PROFILEOUT) | head -30

flame: $(SRCS)
	cd src/ && python3.5 -m vmprof --lines -o $(PROFILEOUT) Simulator.py && mv $(PROFILEOUT) ../
	vmprof-flamegraph.py $(PROFILEOUT) > $(FLAME)
	flamegraph.pl $(FLAMEOPTS) $(FLAME) > $(FLAMEIMG)
	firefox $(FLAMEIMG)

graph: map.gv
	dot -Tsvg $< > map.svg

plot:
	gnuplot plot.plt
	mv *.svg svgs/

plotclient: client.log
	gnuplot plot.plt

clean:
	rm -f $(FLAME) $(FLAMEIMG) $(PROFILEOUT) $(PROFILELINES) *.log *.svg *.pyc *.dat
	rm -f logs/*

show:
	firefox svgs/* & 
