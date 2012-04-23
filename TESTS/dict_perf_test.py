#!/usr/bin/python

import shmobj, time, random

LENGTH = 10000

if __name__=='__main__':

    shmobj.add_shmem_pages(1000)
    print "Using %d bytes of memory" % shmobj.freecount()


    shmdict = shmobj.SHMDCT({})
    locdict = {}

    #We first allocate all the SHMINT objects ahead of time
    #to minimize overhead from that allocation
    otherdict1 = {}
    otherdict2 = {}
    shmkeylist = [shmobj.SHMSTR(str(i)) for i in range(LENGTH)]
    lockeylist = [str(i) for i in range(LENGTH)]
    for i in range(LENGTH):
        otherdict1[shmkeylist[i]] = shmobj.SHMINT(i)
        otherdict2[lockeylist[i]] = i


    stime = time.time()
    for i in range(LENGTH):
        shmdict[shmkeylist[i]] = otherdict1[shmkeylist[i]]
    etime = time.time()
    print "shmdict create time (set):", (etime - stime)

    stime = time.time()
    for i in range(LENGTH):
        locdict[lockeylist[i]] = otherdict2[lockeylist[i]]
    etime = time.time()
    print "locdict create time (set):", (etime - stime)

    print

    shmdict.delete(shallow=True)

    stime = time.time()
    shmdict = shmobj.SHMDCT(otherdict1)
    etime = time.time()
    print "shmdict create time (from previous dict):", (etime - stime)

    stime = time.time()
    locdict = dict(otherdict2)
    etime = time.time()
    print "locdict create time (from previous dict):", (etime - stime)

    print

    a = 0

    stime = time.time()
    for i in range(LENGTH):
        a = shmdict[str(i)]
    etime = time.time()
    print "shmdict \"linear\" access time:", (etime - stime)

    stime = time.time()
    for i in range(LENGTH):
        a = locdict[str(i)]
    etime = time.time()
    print "locdict \"linear\" access time:", (etime - stime)

    print

    r = random.Random()

    stime = time.time()
    for i in range(LENGTH):
        a = shmdict[r.choice(shmkeylist)]
    etime = time.time()
    print "shmdict random access time:", (etime - stime)

    stime = time.time()
    for i in range(LENGTH):
        a = locdict[r.choice(lockeylist)]
    etime = time.time()
    print "locdict random access time:", (etime - stime)
