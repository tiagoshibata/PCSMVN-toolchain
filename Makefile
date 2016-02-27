.PHONY: all clean

all: pcsmvn-dumpview

clean:
	rm -f *.o pcsmvn-dumpview

pcsmvn-dumpview: dumpview.o
	gcc -o $@ $^

dumpview.o: dumpview.c
