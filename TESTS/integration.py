#!/usr/bin/env python
# Written by David Ells
#
# This program was written as a test for the shmobj python package.
# The code approximates the integral of function func. The parent
# process spawns a new child to calculate each set of intervals in parallel.
# Each child then adds its calculated area to the shared sum. When
# all children are done executing, the parent prints the approximation.

import os, shmobj, time
from sys import argv, exit
from math import pow, sin, sqrt

global approxes

def func(x):
    return sqrt(3.0 * pow( sin(x/2.0), 3.0 ))

def calc(i,numintervals):
    start = i*numintervals
    end = start + numintervals
 
    area = 0
    for j in range(start, end):
        height = (func(j*width) + func((j+1)*width)) / 2.0
        area += (width * height)
 
    print os.getpid(), ": child adding area of", area
    approxes[i].set(area)

if __name__=='__main__':
    PI = shmobj.SHMDBL(3.1415926535)
    approx = shmobj.SHMDBL(0.0)

    if(len(argv) != 3):
        print "Usage: %s [number of children] [number of intervals]" % argv[0]
        exit(-1)

    numchildren = int(argv[1])
    n = int(argv[2])
    width = PI / (n*1.0)
    numintervals = n / numchildren
    remintervals = n % numchildren

    approxes = shmobj.SHMLST([shmobj.SHMDBL(0.0) for i in range(numchildren)])

    stime = time.time()

    for i in range(0, numchildren): 
        rc = os.fork()
        if rc == 0:
            calc(i, numintervals)
            exit(0)

    area = 0
    start = numintervals*numchildren
    end = start + remintervals
    for j in range(start, end):
        height = (func(j*width) + func((j+1)*width)) / 2.0
        area += (width * height)

    for i in range(0, numchildren):
        (pid,stat) = os.wait()

    final_approx = sum(approxes) + area

    etime = time.time()

    print os.getpid(), ": parent adding area of", area

    print ""
    print "Approximation is", final_approx
    print "Pi used:", PI
    print "Time = %f" % (etime - stime)
    print ""

