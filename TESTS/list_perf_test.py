#!/usr/bin/python

import shmobj, time, random

LENGTH = 10000

if __name__=='__main__':

    shmobj.add_shmem_pages(1000)
    print "Using %d bytes of memory" % shmobj.freecount()


    shmlist = shmobj.SHMLST([])
    loclist = []

    #We first allocate all the SHMINT objects ahead of time
    #to minimize overhead from that allocation
    otherlist1 = [shmobj.SHMINT(i) for i in range(LENGTH)]
    otherlist2 = [i for i in range(LENGTH)]


    stime = time.time()
    for i in range(LENGTH):
        shmlist.append(otherlist1[i])
    etime = time.time()
    print "shmlist create time (append):", (etime - stime)

    stime = time.time()
    for i in range(LENGTH):
        loclist.append(otherlist2[i])
    etime = time.time()
    print "loclist create time (append):", (etime - stime)

    print

    shmlist.delete(shallow=True)

    stime = time.time()
    shmlist = shmobj.SHMLST([x for x in otherlist1])
    etime = time.time()
    print "shmlist create time (list comprehension):", (etime - stime)

    stime = time.time()
    loclist = [x for x in otherlist2]
    etime = time.time()
    print "loclist create time (list comprehension):", (etime - stime)

    print

    a = 0

    stime = time.time()
    for i in range(LENGTH):
        a = shmlist[i]
    etime = time.time()
    print "shmlist linear access time (index lookup):", (etime - stime)

    stime = time.time()
    for i in range(LENGTH):
        a = loclist[i]
    etime = time.time()
    print "loclist linear access time (index lookup):", (etime - stime)

    print

    stime = time.time()
    for x in shmlist:
        pass
        #a = x
    etime = time.time()
    print "shmlist linear access time (for loop):", (etime - stime)

    stime = time.time()
    for x in loclist:
        pass
        #a = x
    etime = time.time()
    print "loclist linear access time (for loop):", (etime - stime)

    print

    r = random.Random()

    stime = time.time()
    for i in range(LENGTH):
        a = r.choice(shmlist)
    etime = time.time()
    print "shmlist random access time:", (etime - stime)

    stime = time.time()
    for i in range(LENGTH):
        a = r.choice(loclist)
    etime = time.time()
    print "loclist random access time:", (etime - stime)

