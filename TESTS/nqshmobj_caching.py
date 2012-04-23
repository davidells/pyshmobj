#!/usr/bin/env python

# RMB: this version is almost the same as nqshmobj.py but caches some of the vaues
#  into local mem for significant sppedup.  I have tested it with multiple procs
#  and get the correct number of solutions in each case.  However, I have not really
#  printed the solutions.  Yu can do a diff to see the chgs.

import sys, os, time, shmobj

global nsolutions, solution_sem, work_sem, wpool, nqueens, nprocs, quiet

nsolutions = shmobj.SHMINT(0)
solution_sem = shmobj.semaphore()
work_sem = shmobj.semaphore()
nqueens = 4
nprocs = 1
quiet = 0

def getwork():
    work_sem.wait()
    if len(wpool) == 0:
        work_sem.post()
        return None
    temp = wpool.pop()
    work_sem.post()
    return temp

def test_position(col, row, rows):
    for i in range(col):
        tempval = int(rows[i])
        if tempval+i == col+row  \
        or i-tempval == col-row  \
        or tempval == row:
            return 1
    return 0

def nqbranch(col, rows):
    if (col+1) == nqueens:
        # print "FOUND", os.getpid(), rows
        if not quiet:
            for i in range(nqueens):
                print rows[i],
            print
        solution_sem.wait()
        nsolutions.set(nsolutions+1)
        solution_sem.post()
    else:
        for i in range(nqueens):
            if not test_position(col+1, i, rows):
                rows[col+1] = i  # shmobj.SHMINT(i)
                nqbranch(col+1, rows)
                rows[col+1] = 0  # shmobj.SHMINT(0)

def worker():
    node = getwork()
    while node:
        col = node['col']
        rows = [ x.val() for x in node['rows'] ]
        nqbranch(col,rows)
        node = getwork()

if __name__ == '__main__':
    for i in range(len(sys.argv)):
        if sys.argv[i] == '-q':
            quiet = 1
        elif sys.argv[i] == '-n':
            nqueens = int(sys.argv[i+1])
        elif sys.argv[i] == '-p':
            nprocs = int(sys.argv[i+1])

    # Add more pages of available shmem
    shmobj.add_shmem_pages(36)

    colstr = shmobj.SHMSTR('col')
    rowsstr = shmobj.SHMSTR('rows')
    wpool = shmobj.SHMLST([])
    for i in range(nqueens):
        # make a new zerolist and rowsval each time
        zerolist = []
        for j in range(nqueens):
            zeroval = shmobj.SHMINT(0)
            zerolist.append(zeroval)
        rowsval = shmobj.SHMLST( zerolist )
        node = shmobj.SHMDCT( { colstr : zeroval, rowsstr : rowsval } )
        node['rows'][0] = shmobj.SHMINT(i)
        wpool.append(node)

    childPids = []
    for i in range(nprocs-1):
        pid = os.fork()
        if pid == 0:
            worker()
            sys.exit(0)
        else:
            childPids.append(pid)

    stime = time.time()
    worker()

    for pid in childPids:
        (pid,status) = os.waitpid(pid,0)

    print "found %d solutions" % nsolutions
    print 'time = %f' % (time.time()-stime)
