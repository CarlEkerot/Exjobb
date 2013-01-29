CC	 = gcc
CFLAGS	 = -fPIC -I/usr/include/python2.7 -fno-strict-aliasing -DNDEBUG
CFLAGS	+= -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector
CFLAGS	+= --param=ssp-buffer-size=4 -Wformat -Wformat-security -Werror=format-security

SRC	 = align.c

all: align

align.o: $(SRC)
	$(CC) -c $(CFLAGS) $(SRC)

align: align.o
	gcc -shared -o libalign.so align.o

install: align
	mv libalign.so /usr/lib/
	cp align.h /usr/include/

uninstall:
	rm /usr/lib/libalign.so
	rm /usr/include/align.h

clean:
	rm libalign.so align.o

