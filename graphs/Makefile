TARGET=client.svg server.svg
CC=dot
CFLAGS=-Tsvg 

all:$(TARGET)
run: all show

%.svg: %.gv
	$(CC) $(CFLAGS) -o $@ $<

runpng:client.png server.png

%.png: %.gv
	$(CC) -Tpng -o $@ $<
	
show:
	eog server.svg
