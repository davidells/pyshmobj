#!/usr/bin/env python

import os, shmobj

if __name__ == "__main__":
    x = shmobj.SHMINT(44)
    print x.__class__, x
    y = x + 33
    print y.__class__, y
    x = shmobj.SHMINT(x + 55)
    print '--------------------'
    print x.__class__, x
    print '--------------------'
    x = shmobj.SHMINT(88)
    print '--------------------'
    print x.__class__, x
    print '--------------------'
    x = shmobj.SHMINT(22)  # should be back at original malloc addr
    print '--------------------'
    print x.__class__, x
    print '--------------------'
