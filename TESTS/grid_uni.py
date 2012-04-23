#!/usr/bin/python

import sys

ROWS = 1000
COLUMNS = 1000

class globmem(object):
    def __init__(self):
        self.a = []
        self.b = []
        self.st = []
        self.pq = []

        for i in range(ROWS+2):
            self.a.append([])
            self.b.append([])
            self.st.append(0)
            for j in range(COLUMNS+2):
                self.a[i].append(0)
                self.b[i].append(0)

        for i in range(ROWS+1):
            self.pq.append(0)

        self.pqbeg = 0
        self.pqend = 0
        self.niters = 0
        self.nproc = 0
        self.rows = 0
        self.ncols = 0

def slave():
    work('s')

def phi(x, y):
    x = float(x)
    y = float(y)
    return ((x * x) - (y * y) + (x * y))

#gridinit(double m[ROWS+2][COLUMNS+2],int r,int c)
def gridinit(m, r, c):
    #int i, j;
    #double bndavg;
    

    for j in range(c + 2):
        m[0][j] = phi(1,j+1)
        m[r+1][j]= phi(r+2,j+1)

    for i in range(1, r+2):
        m[i][0] = phi(i+1,1)
        m[i][c+1] = phi(i+1,c+2)

    bndavg = avgbnd(m,r,c)
    print "boundary average = %f" % bndavg

    # initialize the interior of the grids to the average over the boundary
    for i in range(1,r+1):
        for j in range(1,c+1):
            m[i][j] = 0
            # m[i][j] = bndavg; this optimization hinders debugging 


def queueprob(x):
    glob.pq[glob.pqend] = x
    glob.pqend = (glob.pqend + 1) % (ROWS + 1)
    #print "in queueprob: glob.pq = ",
    #for i in range(glob.pqend):
    #    print "%d" % glob.pq[i],
    #print

#compute(double p[ROWS+2][COLUMNS+2],double q[ROWS+2][COLUMNS+2], int r, int ncols)
def compute(p,q,r,ncols):
    for j in range(1, ncols+1):
        q[r][j] = (p[r-1][j] + p[r+1][j] + p[r][j-1] + p[r][j+1]) / 4.0

def putprob(r):
    qprob = 0
    glob.st[r] += 1

    if (r == 1):
        glob.st[0] = glob.st[r]
    elif (r == glob.rows):
        glob.st[glob.rows+1] = glob.st[r]

    if (glob.st[r] < glob.niters):

        if ((r > 1) and (glob.st[r-2] >= glob.st[r]) \
               and (glob.st[r-1] == glob.st[r])):
            queueprob(r-1)
            qprob = 1

        if (r < glob.rows and glob.st[r+1] == glob.st[r] \
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
        glob.pqbeg = (glob.pqbeg+1) % (ROWS + 1)
        rc = 0
    return(rc, p)

#void work(char who)            /* main routine for all processes */
def work(who):
    r = 0
    (rc, r) = getprob(r)
    while (rc == 0):
        if ((glob.st[r] % 2) == 0):
            compute(glob.a, glob.b, r, glob.ncols)
        else:
            compute(glob.b, glob.a, r, glob.ncols)
        putprob(r)
        (rc, r) = getprob(r)

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
        print "usage: %s nrows ncols niters\n" % (sys.argv[0])
        sys.exit(-1)

    glob = globmem()

    glob.rows = int(sys.argv[1])
    glob.ncols = int(sys.argv[2])
    glob.niters = int(sys.argv[3])

    print "nrows\tncols\tniters\n"
    print "%d \t  %d \t  %d \t\n" % \
       (glob.rows,glob.ncols,glob.niters)

    gridinit(glob.a, glob.rows, glob.ncols)
    gridinit(glob.b, glob.rows, glob.ncols)
    
    glob.pqbeg = 0
    glob.pqend = 0
    
    for i in range(glob.rows):
        queueprob(i+1)

    # initialize the status vector 
    for i in range(glob.rows + 2):
        glob.st[i] = 0

    work('m')

     
    #print "the resulting grid:\n"
    #if (glob.niters % 2 == 0):
    #    printgrid(glob.a,glob.rows,glob.ncols)
    #else:
    #    printgrid(glob.b,glob.rows,glob.ncols)

    if (glob.niters % 2 == 0):
        avg = avggrid(glob.a, glob.rows, glob.ncols)
    else:
        avg = avggrid(glob.b, glob.rows, glob.ncols)
    print "average value of grid = %f" % avg



