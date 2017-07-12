CC=g++
TARGET=efficiency.svg
BINARY=model.x
OBJECTS=build/connection.o build/networkLayout.o build/utils.o
FLAGS=-Iinclude/ -std=c++11

all: $(BINARY)

#run: twrite tsend jumbo
run: $(BINARY)
	./$(BINARY) 2

markdown:
	markdown-to-slides slides.md -o slides.html

$(BINARY): $(OBJECTS) main.cpp
	$(CC) $(FLAGS) $(OBJECTS) main.cpp -o $(BINARY)

networkLayout.o: connection.o

build/%.o: src/%.cpp
	$(CC) $(FLAGS) -c $< -o $@

show: $(TARGET)
	xviewer $(TARGET)

clean:
	rm -f *.o $(TARGET) $(OBJECTS) $(BINARY)
	rm -f build/*.o
	rm -rf twrite tsend jumbo

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

