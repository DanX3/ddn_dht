TARGET=client.svg server.svg
CC=dot
CFLAGS=-Tsvg 

all:$(TARGET)
run: all show

%.svg: %.gv
	$(CC) $(CFLAGS) -o $@ $<
	
show:
	xviewer server.svg
