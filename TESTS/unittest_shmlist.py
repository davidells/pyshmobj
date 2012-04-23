#!/usr/bin/env python

import shmobj
import sys, os, unittest

class ShmLstTestCase(unittest.TestCase):
    def setUp(self):
        length = 20
        self.start_mem = shmobj.freecount()
        self.locallist = []
        for i in range(0, length):
            val = shmobj.SHMINT(i)
            self.locallist.append(val)
        self.shmlist = shmobj.SHMLST(self.locallist)
        self.last = length - 1
    
    def tearDown(self):
        self.shmlist.delete()

    def testLength(self):
        shmlen = len(self.shmlist)
        lcllen = len(self.locallist)
        self.assertEqual(shmlen, lcllen)

    def testGetEntry(self):
        self.assertEqual(self.locallist[5], self.shmlist[5])
        self.assertEqual(self.locallist[0], self.shmlist[0])
        self.assertEqual(self.locallist[self.last], self.shmlist[self.last])
        self.assertEqual(self.shmlist[-1], self.shmlist[self.last])
        self.assertEqual( self.shmlist[0], self.shmlist[0 - (self.last + 1)] )
        self.assertRaises(IndexError, self.shmlist.__getitem__, self.last + 1)
        self.assertRaises(IndexError, self.shmlist.__getitem__, 0 - (self.last + 2))

    def testSplice(self):
        self.assertEqual(self.locallist[0:], self.shmlist[0:])
        self.assertEqual(self.locallist[:len(self.locallist)], \
                         self.shmlist[:len(self.shmlist)])
        self.assertEqual(self.shmlist[-4:-2], self.locallist[-4:-2])

    def testSetEntry(self):
        newval = shmobj.SHMINT(999)
        self.shmlist[0] = newval
        self.assertEqual(self.shmlist[0], newval)
        self.shmlist[5] = newval
        self.assertEqual(self.shmlist[5], newval)
        self.shmlist[self.last] = newval
        self.assertEqual(self.shmlist[self.last], newval)

    def testString(self):
        self.assertEqual(str(self.shmlist), str(self.locallist))

    def testEqual(self):
        d = self.shmlist
        self.assertEqual(d, self.shmlist)

    def testCount(self):
        local_item = self.locallist[0]
        shm_item = self.shmlist[0]
        for i in range(1,5):
            self.locallist[i] = local_item
            self.shmlist[i] = shm_item
        self.shmlist[self.last] = shm_item
        self.locallist[self.last] = local_item
        self.assertEqual(self.locallist.count(local_item), \
                         self.shmlist.count(shm_item))
        self.assertEqual(self.shmlist.count(shm_item), 6)
        self.assertEqual(self.shmlist.count(0), 6)
        self.assertEqual(self.shmlist.count(1), 0)
        self.assertEqual(self.shmlist.count(7), 1)

    def testDelete(self):
        self.shmlist.delete()
        self.assertEqual(shmobj.freecount(), self.start_mem)
        #Make sure we don't throw an error when we call tearDown
        self.setUp()


if __name__=='__main__':
    unittest.main()
