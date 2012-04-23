#!/usr/bin/python

import os, sys, time, threading

MAX_PROC = 20
DIM = 200

a = []
b = []
c = []

def mm(rank, numprocs):
    i = rank
    while i < DIM:
        for j in range(DIM):
            sum = 0.0
            for k in range(DIM):
                sum = sum + (a[i][k] * b[k][j])
            c[i][j] = sum
        i = i + numprocs

def checkmatrix():
    errs = 0
    for i in range(DIM):
        for j in range(DIM):
            e = 0.0
            for k in range(DIM):
                e = e + (a[i][k] * b[k][j])
            if e != c[i][j]:
                print "(%d,%d) error\n" % (i, j)
                print 'e = %s, c[%d][%d] = %s' % (e, i, j, c[i][j])
                errs += 1
    if errs == 0:
        print 'Success'
    

if __name__=='__main__':
    
    if (len(sys.argv) != 3):
        print 'Usage: %s n dim\n where n is the number of threads and dim is the dimension of the matrix' % sys.argv[0]
        sys.exit(1)
            
    n = int(sys.argv[1])
    DIM = int(sys.argv[2])

    for i in range(DIM):
        a.append([])
        b.append([])
        c.append([])
        for j in range(DIM):
            a[i].append(i+j)
            b[i].append(i+j)
            c[i].append(0)
    
    stime = time.time()

    threads = []
    for i in range(n):
        threads.append(threading.Thread(target=mm, args=(i,n)))
        threads[i].start()
        #thread.start_new_thread(mm, (i, n))
        #rc = os.fork()
        #if rc == 0:
            #print 'mm(%s,%s)' % (i, n)
        #    mm(i,n)
        #    sys.exit(0)

    for i in range(n):
        #(pid,stat) = os.wait()
        threads[i].join()

    etime = time.time()
    print 'time = %f' % (etime - stime)

    #checkmatrix()
