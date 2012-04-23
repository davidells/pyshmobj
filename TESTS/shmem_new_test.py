#!/usr/bin/env python

import shmobj, os, sys, time

def printCurrentMemUse():
    print ''
    print '========================='
    print "Current free mem :", shmobj.freecount()
    print '========================='
    print ''

def runtest(testnum):
    if testnum == 1:
        l = []
        printCurrentMemUse()

        for i in range(2046):
            l.append(shmobj.SHMINT(i))
        print 'Allocated 2046 SHMINTs'
            
        printCurrentMemUse()

        shmobj.add_shmem_pages(8)
        print 'Added 8 more pages of shared mem'

        printCurrentMemUse()

        for i in range(2047):
            l.append(shmobj.SHMDBL(i))
        print 'Allocated 2047 SHMDBLs'

        printCurrentMemUse()

        for x in l:
            x.delete()
        print 'Deleted all shmobjs...'

        printCurrentMemUse()
        #print l

if __name__=='__main__':
    if len(sys.argv) < 2:
        print 'usage %s [test number]' % sys.argv[0]
        sys.exit(-1)

    runtest(int(sys.argv[1]))
