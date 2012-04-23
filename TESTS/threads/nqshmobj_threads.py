#!/usr/bin/env python

import sys, os, time, threading

global nsolutions, solution_sem, work_sem, wpool, nqueens, nprocs, quiet

nsolutions = 0
solution_sem = threading.Semaphore()
work_sem = threading.Semaphore()
nqueens = 4
nprocs = 1
quiet = 0

def getwork():
    global nsolutions, solution_sem, work_sem, wpool, nqueens, nprocs, quiet
    work_sem.acquire()
    if len(wpool) == 0:
        work_sem.release()
        return None
    temp = wpool.pop()
    work_sem.release()
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
    global nsolutions, solution_sem, work_sem, wpool, nqueens, nprocs, quiet
    if (col+1) == nqueens:
        # print "FOUND", os.getpid(), rows
        if not quiet:
            for i in range(nqueens):
                print rows[i],
            print
        solution_sem.acquire()
        nsolutions = nsolutions+1
        solution_sem.release()
    else:
        for i in range(nqueens):
            if not test_position(col+1, i, rows):
                rows[col+1] = i
                nqbranch(col+1, rows)
                rows[col+1] = 0

def worker():
    node = getwork()
    while node:
        col = node['col']
        rows = node['rows']
        nqbranch(col,rows)
        node = getwork()

colstr = 'col'
rowsstr = 'rows'
wpool = []

if __name__ == '__main__':
    for i in range(len(sys.argv)):
        if sys.argv[i] == '-q':
            quiet = 1
        elif sys.argv[i] == '-n':
            nqueens = int(sys.argv[i+1])
        elif sys.argv[i] == '-p':
            nprocs = int(sys.argv[i+1])

    for i in range(nqueens):
        # make a new zerolist and rowsval each time
        zerolist = []
        for j in range(nqueens):
            zeroval = 0
            zerolist.append(zeroval)
        rowsval = zerolist
        node = { colstr : zeroval, rowsstr : rowsval }
        node['rows'][0] = i
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

    threads = []
    for i in range(nprocs-1):
        threads.append(threading.Thread(target=worker))
        threads[i].start()

    worker()

    for i in range(nprocs-1):
        threads[i].join()

    etime = time.time()

    print "found %d solutions" % nsolutions
    print 'time = %f' % (etime-stime)
