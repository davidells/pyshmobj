#!/usr/bin/env python

import sys, os, time, math, shmobj

if len(sys.argv) != 3:
    print 'usage: %s num_procs num_iterations' % (sys.argv[0])
    sys.exit(0)
nprocs = int(sys.argv[1])
niters = int(sys.argv[2])

myid = 0

subvals = shmobj.SHMLST( [ shmobj.SHMDBL(0.0) for i in range(nprocs) ] )

childPids = []
for i in range(nprocs-1):
    pid = os.fork()
    if pid == 0:
        myid = i + 1
        break
    else:
        childPids.append(pid)

startTime = time.time()
h = 1.0 / float(niters)
sum = 0.0
# A slightly better approach starts from large i and works back
for i in range(myid+1,niters+1,nprocs):
    x = h * (float(i) - 0.5)
    sum += (4.0 / (1.0 + x * x))
subvals[myid].set(h * sum)
# print "MYID=%d MYVAL=%f" % (myid,subvals[myid])

if myid == 0:
    for pid in childPids:
        (pid,status) = os.waitpid(pid,0)
    pi = 0.0
    for i in range(nprocs):
        pi += subvals[i]
    endTime = time.time();
    print 'pi is approximately %.16f, err is %.16f' % (pi,abs(math.pi-pi))
    print 'time = %f' % (endTime-startTime)
