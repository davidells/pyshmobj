#!/usr/bin/env python

import os, sys, time
import shmobj

sem = shmobj.semaphore()

for i in range(0,5):
    rc = os.fork()
    if rc == 0:
        print "%s: new forked child started..." % os.getpid()
        sem.wait()
        print "%s: obtained lock" % os.getpid()
        time.sleep(1)
        print "%s: releasing lock" % os.getpid()
        sem.post()
        sys.exit(0)

for i in range(0,5):
    os.wait()

print "All children done, parent exiting..."
