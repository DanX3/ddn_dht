CC=g++
TARGET=efficiency.svg
BINARY=model.x
OBJECTS=model.o

all: twrite tsend jumbo

markdown:
	markdown-to-slides slides.md -o slides.html

jumbo: $(BINARY) plot.p
	@echo Computing $@
	@./$(BINARY) 2
	@gnuplot plot.p
	@mkdir -p $@
	@mv efficiency.svg walltime.svg $@

tsend: $(BINARY) plot.p
	@echo Computing $@
	@./$(BINARY) 1
	@gnuplot plot.p
	@mkdir -p $@
	@mv efficiency.svg walltime.svg $@

twrite: $(BINARY) plot.p
	@echo Computing $@
	@./$(BINARY) 0
	@gnuplot plot.p
	@mkdir -p $@
	@mv efficiency.svg walltime.svg $@

$(BINARY): $(OBJECTS) main.cpp
	$(CC) -std=c++11 $(OBJECTS) main.cpp -o $(BINARY)

model.o: model.cpp
	$(CC) -std=c++11 -c $< -o $@

show: $(TARGET)
	xviewer $(TARGET)

clean:
	rm -f *.o $(TARGET) $(OBJECTS) $(BINARY)
	rm -r twrite tsend jumbo
