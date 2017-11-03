CC=pypy3
SRCS=$(shell find . -name "[A-Z]*.py")
PROFILEOUT=profile_data
PROFILELINES=profile_lines
FLAME=profile.flame
FLAMEIMG=profile.svg
FLAMEOPTS= --title "IME Simulation" --colors blue

all: $(SRCS)
	cd src/ && time $(CC) Simulator.py --request ../request
	gnuplot plot.plt

print:
	@echo $(SRCS)

doc: $(SRCS) Doxyfile
	doxygen Doxyfile

lineprofile: $(SRCS)
	$(CC) -m vmprof --lines -o $(PROFILEOUT) src/Simulator.py 
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

plotclient: client.log
	gnuplot plot.plt

clean:
	rm -f $(FLAME) $(FLAMEIMG) $(PROFILEOUT) $(PROFILELINES) *.log *.svg *.pyc *.dat
	rm -f logs/*

show:
	firefox svgs/* & 
