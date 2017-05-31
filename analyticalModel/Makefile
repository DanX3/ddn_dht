TARGET=plot.svg
BINARY=model.x
OBJECTS=model.o

all: plot
plot: $(TARGET)

markdown:
	markdown-to-slides slides.md -o slides.html

$(TARGET): $(BINARY) plot.p
	./$(BINARY)
	gnuplot plot.p

$(BINARY): $(OBJECTS) main.cpp
	g++ -std=c++11 -g $(OBJECTS) main.cpp -o $(BINARY)

%.o: %.cpp
	g++ -std=c++11 -g -c $< -o $@

show: $(TARGET)
	xviewer $(TARGET)

clean:
	rm -f *.o $(TARGET) $(OBJECTS) $(BINARY)

