#!/usr/bin/env python

import shmobj
import sys, os, unittest

class ShmDictTestCase(unittest.TestCase):
    def setUp(self):
        self.start_mem = shmobj.freecount()
        self.localdict = {}
        for i in range(0,20):
            key = shmobj.SHMSTR('key%02d' % i)
            val = shmobj.SHMINT(i)
            self.localdict[key] = val
        self.shmdict = shmobj.SHMDCT(self.localdict)
    
    def tearDown(self):
        self.shmdict.delete()

    def testKeys(self):
        shmkeys = sorted(self.shmdict.keys())
        lclkeys = sorted(self.localdict.keys())
        self.assertEqual(shmkeys, lclkeys)

    def testVals(self):
        shmvals = sorted(self.shmdict.values())
        lclvals = sorted(self.localdict.values())
        self.assertEqual(shmvals, lclvals)

    def testLength(self):
        shmlen = len(self.shmdict)
        lcllen = len(self.localdict)
        self.assertEqual(shmlen, lcllen)

    def testPop(self):
        oldlen = len(self.shmdict)
        testval = self.shmdict['key00']
        popval = self.shmdict.pop('key00')

        self.assertEqual(testval, popval)
        self.assertEqual(len(self.shmdict), oldlen - 1)

        self.shmdict[shmobj.SHMSTR('key00')] = popval

        self.assertRaises(KeyError, self.shmdict.pop, 'not_there')
        self.assertEqual(self.shmdict.pop('not_there', 5), 5)

    def testClear(self):
        prev_mem = shmobj.freecount()
        newdict = shmobj.SHMDCT({})
        empty_d_size = prev_mem - shmobj.freecount()
        self.shmdict.clear()
        self.assertEqual(len(self.shmdict), 0)
        self.assertEqual(self.start_mem - shmobj.freecount(), 2 * empty_d_size)
        self.shmdict.delete()
        self.setUp()

    def testGetEntry(self):
        key = sorted(self.localdict.keys())[0]
        self.assertEqual(self.localdict[key], self.shmdict[key])
        self.assertEqual(self.localdict['key00'], self.shmdict['key00'])

    def testSetEntry(self):
        newkey = shmobj.SHMSTR('newkey')
        newval = shmobj.SHMINT(999)
        self.shmdict[newkey] = newval
        self.assertEqual(self.shmdict['newkey'], newval)
        self.shmdict['key00'] = newval
        self.assertEqual(self.shmdict['key00'], newval)
        self.assertEqual(self.shmdict['key00'], self.shmdict['newkey'])

    def testString(self):
        #Best we can do is make sure str's are same length, since there's
        #no guarantee on order of entries.
        self.assertEqual(len(str(self.shmdict)), len(str(self.localdict)))

    def testEqual(self):
        d = self.shmdict
        self.assertEqual(d, self.shmdict)
        d = shmobj.SHMDCT(self.shmdict.get_ptr(), internal=True)
        self.assertEqual(d, self.shmdict)
        d = self.shmdict.copy()
        self.assertEqual(d, self.shmdict)
        d.delete(shallow=True)

    def testDelete(self):
        self.shmdict.delete()
        self.assertEqual(shmobj.freecount(), self.start_mem)
        #Make sure we don't throw an error when we call tearDown
        self.setUp()

if __name__=='__main__':
    unittest.main()
