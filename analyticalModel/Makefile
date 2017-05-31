CC=g++
TARGET=efficiency.svg
BINARY=model.x
OBJECTS=model.o

all: twrite 

markdown:
	markdown-to-slides slides.md -o slides.html

twrite: $(BINARY) plot.p
	./$(BINARY) 0
	gnuplot plot.p
	mkdir -p $@
	mv efficiency.svg walltime.svg $@

$(BINARY): $(OBJECTS) main.cpp
	$(CC) -std=c++11 $(OBJECTS) main.cpp -o $(BINARY)

model.o: model.cpp
	$(CC) -std=c++11 -c $< -o $@

show: $(TARGET)
	xviewer $(TARGET)

clean:
	rm -f *.o $(TARGET) $(OBJECTS) $(BINARY)
