#!/usr/bin/env python

import shmobj
import sys, os, unittest

class ShmDblTestCase(unittest.TestCase):
    def setUp(self):
        self.start_mem = shmobj.freecount()
        self.shmdbl_a = shmobj.SHMDBL(4.0)
        self.shmdbl_b = shmobj.SHMDBL(5.0)
        self.shmdbl_c = shmobj.SHMDBL(66.0)
        self.ldbl_a = 4.0
        self.ldbl_b = 5.0
        self.ldbl_c = 66.0
    
    def tearDown(self):
        pass

    def testMath(self):
        a,b,c = self.shmdbl_a, self.shmdbl_b, self.shmdbl_c
        self.assertEqual(a+b, b+a)
        self.assertEqual(c-b, 61.0)
        self.assertEqual(a+66, a+c)
        self.assertEqual(a*b, 20.0)

    def testString(self):
        self.assertEqual(str(self.shmdbl_a), str(self.ldbl_a))

    def testEqual(self):
        a = self.shmdbl_a
        self.assertEqual(a, self.shmdbl_a)
        self.assertEqual(self.shmdbl_a, self.ldbl_a)
        self.assertEqual(self.shmdbl_a, 4.0)
        self.assertEqual(self.shmdbl_a, 4)

    def testDelete(self):
        self.shmdbl_a.delete()
        self.shmdbl_b.delete()
        self.shmdbl_c.delete()
        self.assertEqual(shmobj.freecount(), self.start_mem)
        #Make sure we don't throw an error when we call tearDown
        self.setUp()


if __name__=='__main__':
    unittest.main()
