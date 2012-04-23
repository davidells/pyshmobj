#!/usr/bin/env python

import sys, os, time, math, random, threading

nrands = 10000
nprocs = 1

for i in xrange(len(sys.argv)):
    if sys.argv[i] == '-n':
        nrands = int(sys.argv[i+1])
    elif sys.argv[i] == '-p':
        nprocs = int(sys.argv[i+1])

nrandsPerProc = nrands / nprocs
if nrandsPerProc * nprocs != nrands:
    nrandsPerProc += 1

insides = [0 for i in range(nprocs)]

def calc(myrank):
    inside = 0
    for i in range(0,nrandsPerProc):
        d = math.hypot( random.random(), random.random() )
        if d < 1:
            inside += 1
    insides[myrank] = inside


stime = time.time()

threads = []
for i in range(nprocs-1):
    threads.append(threading.Thread(target=calc, args=(i+1,)))
    threads[i].start()

calc(0)

for i in range(nprocs-1):
    threads[i].join()

etime = time.time()

inside = 0
for i in range(nprocs):
    inside += insides[i]
print 4.0 * inside / nrands
print 'time = %f' % (etime-stime)
