#!/usr/bin/env python

import shmobj
import sys, os, unittest

class ShmStrTestCase(unittest.TestCase):
    def setUp(self):
        self.start_mem = shmobj.freecount()
        self.lstr = "Hello World!"
        self.shmstr = shmobj.SHMSTR("Hello World!")
        self.last = len(self.shmstr) - 1
    
    def tearDown(self):
        self.shmstr.delete()

    def testLength(self):
        shmlen = len(self.shmstr)
        lcllen = len(self.lstr)
        self.assertEqual(shmlen, lcllen)

    def testGetEntry(self):
        self.assertEqual(self.lstr[5], self.shmstr[5])
        self.assertEqual(self.lstr[0], self.shmstr[0])
        self.assertEqual(self.lstr[self.last], self.shmstr[self.last])
        self.assertEqual(self.shmstr[-1], self.shmstr[self.last])
        self.assertEqual( self.shmstr[0], self.shmstr[0 - (self.last + 1)] )
        self.assertRaises(IndexError, self.shmstr.__getitem__, self.last + 1)
        self.assertRaises(IndexError, self.shmstr.__getitem__, 0 - (self.last + 2))

    def testSplice(self):
        self.assertEqual(self.lstr[0:], self.shmstr[0:])
        self.assertEqual(self.lstr[:len(self.lstr)], \
                         self.shmstr[:len(self.shmstr)])
        self.assertEqual(self.shmstr[-4:-2], self.lstr[-4:-2])

    def testString(self):
        self.assertEqual(str(self.shmstr), str(self.lstr))

    def testEqual(self):
        d = self.shmstr
        self.assertEqual(d, self.shmstr)

    def testDelete(self):
        self.shmstr.delete()
        self.assertEqual(shmobj.freecount(), self.start_mem)
        #Make sure we don't throw an error when we call tearDown
        self.setUp()


if __name__=='__main__':
    unittest.main()
