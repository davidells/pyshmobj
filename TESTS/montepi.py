#!/usr/bin/env python

import sys, os, time, math, random, shmobj

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

insides = shmobj.SHMLST( [ shmobj.SHMINT(0) for i in range(nprocs) ] )

def calc(myrank):
    inside = 0
    for i in range(0,nrandsPerProc):
        d = math.hypot( random.random(), random.random() )
        if d < 1:
            inside += 1
    insides[myrank] = shmobj.SHMINT(inside)


stime = time.time()

myrank = 0
childPids = []
for i in range(nprocs-1):
    pid = os.fork()
    if pid == 0:
        calc(i+1)
        sys.exit(0)
    else:
        childPids.append(pid)

if myrank == 0:
    calc(0)

    for pid in childPids:
        (pid,status) = os.waitpid(pid,0)

    etime = time.time()

    inside = 0
    for i in range(nprocs):
        inside += insides[i]
    print 4.0 * inside / nrands
    print 'time = %f' % (etime-stime)
