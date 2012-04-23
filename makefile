
all:
	python setup.py build
	cp build/l*/py2shmobj.so .

clean:
	rm -rf build *pyc *.o *.so
