CC	 = gcc
CFLAGS	 = -fPIC -O3

SRC	 = align.c

all: align

align.o: $(SRC)
	$(CC) -c $(CFLAGS) $(SRC)

align: align.o
	gcc -shared -o libalign.so align.o

install: align
	cp libalign.so /usr/lib/
	cp align.h /usr/include/

uninstall:
	rm /usr/lib/libalign.so
	rm /usr/include/align.h

clean:
	rm libalign.so align.o

