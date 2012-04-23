#!/usr/bin/python

import sys, shmobj, time, os

ROWS = 100
COLUMNS = 100
MAXTHREADS = 128

shmobj.add_shmem_pages(1000)

class globmem(object):
    def __init__(self):
        self.a = shmobj.SHMLST([])
        self.b = shmobj.SHMLST([])
        self.st = shmobj.SHMLST([])
        self.pq = shmobj.SHMLST([])

        for i in range(ROWS+2):
            self.a.append(shmobj.SHMLST([]))
            self.b.append(shmobj.SHMLST([]))
            self.st.append(shmobj.SHMDBL(0))
            for j in range(COLUMNS+2):
                self.a[i].append(shmobj.SHMDBL(0))
                self.b[i].append(shmobj.SHMDBL(0))

        for i in range(ROWS+1):
            self.pq.append(shmobj.SHMDBL(0))

        self.pqbeg = shmobj.SHMINT(0)
        self.pqend = shmobj.SHMINT(0)
        self.niters = shmobj.SHMINT(0)
        self.nprocs = shmobj.SHMINT(0)
        self.nrows = shmobj.SHMINT(0)
        self.ncols = shmobj.SHMINT(0)
        self.pq_mutex = shmobj.semaphore()
        #self.pq_cv = condition var???
        self.nbythread = shmobj.SHMLST([])
        for i in range(MAXTHREADS):
            self.nbythread.append(shmobj.SHMDBL(0))
        self.barrier_lock = shmobj.semaphore()

def slave(x):
    id = int(x)
    work(id)

def phi(x, y):
    x = float(x)
    y = float(y)
    return ((x * x) - (y * y) + (x * y))

def gridinit(m, r, c):

    for j in range(c + 2):
        (m[0][j]).set( phi(1,j+1) )
        (m[r+1][j]).set( phi(r+2,j+1) )

    for i in range(1, r+2):
        (m[i][0]).set( phi(i+1,1) )
        (m[i][c+1]).set( phi(i+1,c+2) )

    bndavg = avgbnd(m,r,c)
    print "boundary average = %f" % bndavg

    # initialize the interior of the grids to the average over the boundary
    for i in range(1,r+1):
        for j in range(1,c+1):
            (m[i][j]).set( 0 )
            # m[i][j] = bndavg; this optimization hinders debugging 


def queueprob(x):
    (glob.pq[glob.pqend]).set( x )
    glob.pqend = ((glob.pqend + 1) % (ROWS + 1))
    #print "in queueprob: glob.pq = ",
    #for i in range(glob.pqend):
    #    print "%d" % glob.pq[i],
    #print

#compute(double p[ROWS+2][COLUMNS+2],double q[ROWS+2][COLUMNS+2], int r, int ncols)
def compute(p,q,r,ncols):
    for j in range(1, ncols+1):
        (q[r][j]).set( (p[r-1][j] + p[r+1][j] + p[r][j-1] + p[r][j+1]) / 4.0 )

def putprob(r):
    qprob = 0
    (glob.st[r]).set( glob.st[r] + 1 )

    if (r == 1):
        (glob.st[0]).set( glob.st[r] )
    elif (r == glob.nrows):
        (glob.st[glob.nrows+1]).set( glob.st[r] )

    if (glob.st[r] < glob.niters):

        if ((r > 1) and (glob.st[r-2] >= glob.st[r]) \
               and (glob.st[r-1] == glob.st[r])):
            queueprob(r-1)
            qprob = 1

        if (r < glob.nrows and glob.st[r+1] == glob.st[r] \
               and glob.st[r+1] <= glob.st[r+2]):
            queueprob(r+1)
            qprob = 1

        if (glob.st[r-1] == glob.st[r] and \
               glob.st[r] == glob.st[r+1]):
            queueprob(r)
            qprob = 1

    if qprob == 1:
        return 1       # new problem
    else:
        return 0       # no new problem

def getprob(v):
    rc = 1
    p = v
    if (glob.pqbeg != glob.pqend):
        p = glob.pq[glob.pqbeg]
        glob.pqbeg = ((glob.pqbeg+1) % (ROWS + 1))
        rc = 0
    return(rc, p)

#void work(char who)            /* main routine for all processes */
def work(myid):
    r = 0

    if myid == 0:
        glob.barrier_lock.post()
    glob.barrier_lock.wait()
    glob.barrier_lock.post()

    glob.pq_mutex.wait()
    (rc, r) = getprob(r)
    glob.pq_mutex.post()
    while (rc == 0):
        (glob.nbythread[myid]).set( glob.nbythread[myid] + 1 )
        r = int(r)
        if ((glob.st[r] % 2) == 0):
            compute(glob.a, glob.b, r, glob.ncols)
        else:
            compute(glob.b, glob.a, r, glob.ncols)
        glob.pq_mutex.wait()
        putprob(r)
        (rc, r) = getprob(r)
        glob.pq_mutex.post()

#printgrid(double m[ROWS+2][COLUMNS+2], int r, int c)
def printgrid(m, r, c):
    for i in range(r+2):
        for j in range(c+2):
            print "%3d %3d %10.5f" % (i,j,m[i][j])

#double avggrid(double m[ROWS+2][COLUMNS+2], int r, int c)
def avggrid(m, r, c):
    avg = 0.0
    for i in range(r+2):
        for j in range(c+2):
            avg += m[i][j]
    return(avg/((r+2)*(c+2)))

#double avgbnd(double m[ROWS+2][COLUMNS+2], int r, int c)
def avgbnd(m, r, c):
    avg = 0.0

    for i in range(r+2):
        avg += m[i][0]
    for i in range(r+2):
        avg += m[i][c+1]
    for i in range(1, c+1):
        avg += m[0][i]
    for i in range(1, c+1):
        avg += m[r+1][i]

    return(avg/(2*(c+2) + 2*(r+2) - 4))  # average over boundary


if __name__=='__main__':
    #int i;
    #int timestart, timeend;
    #double avg;

    if len(sys.argv) < 3:
        print "usage: %s nprocs nrows ncols niters\n" % (sys.argv[0])
        sys.exit(-1)

    glob = globmem()

    glob.nprocs = int(sys.argv[1])
    glob.nrows = int(sys.argv[2])
    glob.ncols = int(sys.argv[3])
    glob.niters = int(sys.argv[4])

    print "nprocs\tnrows\tncols\tniters\n"
    print "%d \t %d \t  %d \t  %d \t\n" % \
       (glob.nprocs, glob.nrows,glob.ncols,glob.niters)

    gridinit(glob.a, glob.nrows, glob.ncols)
    gridinit(glob.b, glob.nrows, glob.ncols)
    
    glob.pqbeg = 0
    glob.pqend = 0
    
    for i in range(glob.nrows):
        queueprob(i+1)

    # initialize the status vector 
    for i in range(glob.nrows + 2):
        (glob.st[i]).set( 0 )

    (glob.nbythread[0]).set( 0 )

    glob.barrier_lock.wait()
    for i in range(1,glob.nprocs):
        (glob.nbythread[i]).set( 0 )
        rc = os.fork()
        if rc == 0:
            slave(i)
            sys.exit(0)

    starttime = time.time()
    work(0)
    endtime = time.time()

    for i in range(1, glob.nprocs):
        (pid,stat) = os.wait()
     
    #print "the resulting grid:\n"
    #if (glob.niters % 2 == 0):
    #    printgrid(glob.a,glob.nrows,glob.ncols)
    #else:
    #    printgrid(glob.b,glob.nrows,glob.ncols)

    if (glob.niters % 2 == 0):
        avg = avggrid(glob.a, glob.nrows, glob.ncols)
    else:
        avg = avggrid(glob.b, glob.nrows, glob.ncols)
    print "average value of grid = %f" % avg

    for i in range(0,glob.nprocs):
        print "done by %d : %d" % (i, glob.nbythread[i])
    print "time = %f" % (endtime-starttime)

