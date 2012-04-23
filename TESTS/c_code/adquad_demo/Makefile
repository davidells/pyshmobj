all: adquad

CFLAGS = -O4

adquad:  adquad.c askfor.o
	cc ${CFLAGS} -o adquad adquad.c askfor.o -lpthread

askfor.o: askfor.c
	cc ${CFLAGS} -c askfor.c

clean:
	rm -f *.o adquad
