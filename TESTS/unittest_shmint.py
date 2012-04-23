#!/usr/bin/env python

import shmobj
import sys, os, unittest

class ShmIntTestCase(unittest.TestCase):
    def setUp(self):
        self.start_mem = shmobj.freecount()
        self.shmint_a = shmobj.SHMINT(4)
        self.shmint_b = shmobj.SHMINT(5)
        self.shmint_c = shmobj.SHMINT(66)
        self.lint_a = 4
        self.lint_b = 5
        self.lint_c = 66
    
    def tearDown(self):
        pass

    def testMath(self):
        a,b,c = self.shmint_a, self.shmint_b, self.shmint_c
        self.assertEqual(a+b, b+a)
        self.assertEqual(c-b, 61)
        self.assertEqual(a+66, a+c)
        self.assertEqual(a*b, 20)

    def testString(self):
        self.assertEqual(str(self.shmint_a), str(self.lint_a))

    def testEqual(self):
        a = self.shmint_a
        self.assertEqual(a, self.shmint_a)
        self.assertEqual(self.shmint_a, self.lint_a)
        self.assertEqual(self.shmint_a, 4)

    def testDelete(self):
        self.shmint_a.delete()
        self.shmint_b.delete()
        self.shmint_c.delete()
        self.assertEqual(shmobj.freecount(), self.start_mem)


if __name__=='__main__':
    unittest.main()
