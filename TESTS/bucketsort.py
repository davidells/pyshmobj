#!/usr/bin/env python
# Written by David Ells
#
# This program was written as a test for the shmobj python package.
# The code does a simple bucketsort on a uniformly distributed list
# of numbers.

import os, sys, shmobj, time
from sys import argv

def get_random_num_list(listsize):
    import random
    l = []
    for i in range(listsize):
        l.append(random.randint(0, listsize))
    return l

if __name__=='__main__':
    #if(len(argv) != 3):
    #    print "Usage: %s [number of children (buckets)] [file]" % argv[0]
    #    exit(-1)
    debug = 0
    shmobj.add_shmem_pages(40)

    for i in range(0, len(argv)):
        if argv[i] == '-d':
            debug = 1

    if(len(argv) < 2):
        print "Usage: %s [-d] [number of children (buckets)]" % argv[0]
        sys.exit(-1)

    numchildren = int(argv[-1])

    #f = open(argv[2])
    #nums = []
    #for line in f:
    #    linenums = line.split(' ')
    #    nums.extend(linenums)
    #nums = map(int, nums)

    #nums = get_1k_nums()
    nums = get_random_num_list(4000)
    print 'Initial mem: ', shmobj.freecount()

    n = len(nums)
    interval_size = n / numchildren
    remintervals = n % numchildren

    b = shmobj.barrier(numchildren)
    buckets = shmobj.SHMLST([])
    buckets_sem = shmobj.semaphore(val=1)

    for i in range(0, numchildren): 
        rc = os.fork()
        if rc == 0:
            buckets_sem.wait()
            buckets.append(shmobj.SHMLST([]))
            buckets_sem.post()
            start = i*interval_size
            end = start + interval_size
            if i == (numchildren-1):
                end = end + remintervals

            b.join()

            #print '%d: got interval [%d, %d)' % (os.getpid(), start, end)
            for j in range(start,end):
                k = nums[j] / interval_size
                if k >= numchildren: k = numchildren - 1
                buckets_sem.wait()
                (buckets[k]).append(shmobj.SHMINT(nums[j]))
                buckets_sem.post()

            b.join()

            buckets[i].sort()
            sys.exit(0)

    for i in range(0, numchildren):
        (pid,stat) = os.wait()

    if debug:
        print "All done"
        print buckets

    print 'Final mem before del: ', shmobj.freecount()
    buckets.delete()
    b.delete()
    print 'Final mem: ', shmobj.freecount()

