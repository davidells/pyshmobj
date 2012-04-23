#!/usr/bin/env python

import os, shmobj

if __name__ == "__main__":
    sem = shmobj.semaphore()
    sem.wait()
    x = shmobj.SHMINT(44)
    print x.__class__, x
    rc = os.fork()
    if rc == 0:  # child
        sem.wait()
    else:
        x.set(55)
        sem.post()
        (pid,stat) = os.waitpid(rc,0)
    print os.getpid(), x.__class__, x
