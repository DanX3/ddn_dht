all: propagate

propagate: clean
	@for case_num in `seq 1 5`; do mkdir $$case_num; cp config $$case_num; done
	@./set_values.sh

clean:
	@rm -rf [0-9]

run: 
	find . -type d -name "[0-9]" | xargs -n 1 -P 4 -I{} python3.5 ~/bin/Simulator.py --config {}/config --logpath {} -r request
	gnuplot plot.plt
	mkdir -p plots/
	mv *.svg plots/
