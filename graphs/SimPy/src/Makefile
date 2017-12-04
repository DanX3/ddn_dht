CC=python3.5
SRCS=$(shell find . -name "[A-Z]*.py")
PROFILEOUT=profile_data
PROFILELINES=profile_lines
FLAME=profile.flame
FLAMEIMG=profile.svg
FLAMEOPTS= --title "IME Simulation" --colors yellow --width 1500

all: $(SRCS)
	time $(CC) Simulator.py --logpath log
	cd log && gnuplot plot.plt

print:
	@echo $(SRCS)

doc: $(SRCS) Doxyfile
	doxygen Doxyfile

lineprofile: $(SRCS)
	$(CC) -m vmprof --lines -o $(PROFILEOUT) Simulator.py 
	vmprofshow --lines $(PROFILEOUT) > $(PROFILELINES)
	less $(PROFILELINES)

profile: $(SRCS)
	$(CC) -m vmprof -o $(PROFILEOUT) Simulator.py
	vmprofshow $(PROFILEOUT) | head -30

flame: $(SRCS)
	python3.5 -m vmprof -o $(PROFILEOUT) Simulator.py
	vmprof-flamegraph.py $(PROFILEOUT) > $(FLAME)
	flamegraph.pl $(FLAMEOPTS) $(FLAME) > $(FLAMEIMG)
	firefox $(FLAMEIMG)

graph: map.gv
	dot -Tsvg $< > map.svg

plot: client.log server.log
	cd ../ && gnuplot plot.plt

plotclient: client.log
	cd ../ && gnuplot plot.plt

clean:
	rm -f $(FLAME) $(FLAMEIMG) $(PROFILEOUT) $(PROFILELINES) *.log *.svg *.pyc 
