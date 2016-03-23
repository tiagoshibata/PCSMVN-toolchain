.PHONY: all clean

CFLAGS=-std=c99
BINARIES=pcsmvn-bin2dump pcsmvn-dumpview
all: $(BINARIES)

clean:
	rm -f *.o $(BINARIES)

pcsmvn-bin2dump: bin2dump.o
	gcc -o $@ $^

pcsmvn-dumpview: dumpview.o
	gcc -o $@ $^

bin2dump.o: bin2dump.c
dumpview.o: dumpview.c
