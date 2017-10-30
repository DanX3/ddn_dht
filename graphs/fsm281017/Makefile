TARGET=client.svg server.svg

all: $(TARGET)

%.svg: %.dot
	dot -Tsvg $< > $@
