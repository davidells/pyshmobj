#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MAXTHREADS 16


#include "askfor.h"
    
    #  NOTE: This program contains some features which are more
    #    general than required for this specific task.  Please
    #    remember that we hope to use this as a more-or-less
    #    prototypical use of trees in numeric algorithms.  For
    #    example, the definition of tree_node includes "first_child"
    #    and "sibling" pointers, although they are never actually
    #    used (and, the tree could in any event just be
    #    a binary tree, rather than a binary tree representing
    #    a general tree).  Our intent is to discuss the topics
    #    of "general trees", "representing general trees with
    #    binary trees", etc.  It is also the case that the
    #    use of queue_nodes is unnecessary; you could just
    #    add a link field to the tree_nodes and queue the
    #    ready tree_nodes in the pool.  
    
    #  this structure gives the format of a node in the tree
    #   representing the gradual subdivision of the interval.
    #   Each node represented a portion of the interval from
    #   "xl" to "xr".

#int queue_node();

import askfor, shmobj, sys

class tree_node(object):
    def __init__(self):
        self.xl = 0.0
        self.xm = 0.0
        self.xr = 0.0
        self.yl = 0.0
        self.ym = 0.0
        self.yr = 0.0
        self.integral = 0.0
        self.status = 0
        self.parent = 0 #tree_node()
        self.first_child = 0 #tree_node()
        self.sibling = 0 #tree_node()
        self.t_lock = 0 #shombj.semaphore

#struct tree_node {
#    double xl;                /* the left bound */
#    double xm;                /* the midpoint */
#    double xr;                /* the right bound */
#    double yl,ym,yr;        /* values of the function */
#    double integral;        /* computed value of the integral */
#    int status;                /* 0->not subdivided;
#                           1->one side completed
#                           2->both sides completed
#                           
#                           another way to think of this field is
#                           as a count of the number of subcalculations
#                           that have been completed
#                           */
#    struct tree_node *parent; /* pointer to the parent node */
#    struct tree_node *first_child,*sibling;
#    pthread_mutex_t t_lock;
#};

class queue_node(object):
    def __init__(self):
        self.next = 0 #queue_node()
        self.node = 0 #tree_node()

#struct queue_node {
#    struct queue_node *next; /* link to next node in pool or q_avail */
#    struct tree_node *node;  /* when node is in pool, this field points
#                                to a node in the tree that has been
#                                queued in the "pool" of work.
#                                */
#};

# variables
#   
#   tree     - the tree representing the current state
#   of the computation
#   
#   pool     - the pool of problems.  Initially, only one node
#   will be in the pool, and it will represent the
#   entire interval
#   
#   q_avail  - avail-list for queue nodes
#   
#   t_avail  - avail-list for tree nodes
#   
#   nthreads - number of processes to participate in the
#   calculation
#   
#   normdiff - the error you are willing to tolerate in a
#   unit interval

class globmem(object):
    def __init__(self):
        self.TAVL = 0 #shmobj.semaphore
        self.t_avail = 0 #tree_node()
        self.tree = 0 #tree_node()

        self.QAVL = 0 #shmobj.semaphore
        self.q_avail = 0 #queue_node()
        self.pool = 0 #queue_node()

        self.nthreads = 0
        self.normdiff = 0.0

        self.MO = 0 #askfor_monitor()

#struct globmem {
#    pthread_mutex_t TAVL;
#    struct tree_node *t_avail;  /* list of available tree_nodes */
#    struct tree_node *tree;     /* the tree being built */
#    
#    pthread_mutex_t QAVL;
#    struct queue_node *q_avail; /* list of available queue_nodes */
#    struct queue_node *pool;    /* pool of available work */
#    
#    int nthreads;                /* number of processes */
#    double normdiff;                /* absolute amount of tolerable error */
#    
#    askfor_monitor_t MO;
#} *glob;

#double func(double);
#void *work(void *);

def slave(arg):
    p5_init(0)
    work(arg)

#void *slave(void *arg)
#{
#    p5_init(0);  /* also called in main with arg 0 */
#    work(arg);
#}

def main():
    p5_init(1)
    glob = globmem()

    glob.t_avail = 0
    glob.q_avail = 0

    t_node = tree_node()
    glob.tree = t_node
    
    #print "left boundary:",
    t_node.xl = float(raw_input())
    #print "right boundary:",
    t_node.xr = float(raw_input())
    
    #if (t_node->xr > 15.0):
    #    print "right boundary too big; try 15.0"
    #    sys.exit(0)
    
    # set up original node - the midpoint, function
    #   values, and first approx of integral must be
    #   stored in the node
    t_node.xm = (t_node.xl + t_node.xr) / 2.0
    
    t_node.yl = func(t_node.xl)
    t_node.ym = func(t_node.xm)
    t_node.yr = func(t_node.xr)
    
    t_node.integral = ((t_node.xr - t_node.xl) * \
        (t_node.yl + t_node.yr + (4 * t_node.ym))) / 6.0
    
    t_node.status = 0
    t_node.parent = None
    
    # stack the single node 
    #askfor_update(&(glob->MO),queue_node,(void *) t_node);
    askfor_update(glob.MO,queue_node,t_node)
    
    #print "'allowable difference' for a unit: ",
    glob.normdiff = float(raw_input())
    #print "number of threads: ",
    glob.nthreads = float(raw_input())

    askfor_init(glob.MO, glob.nthreads)
    
    # RMB: stime = clock();                /* note time includes process creation */
    
    # create the slave threads 
    for i in range(glob.nthreads):
        p5_tcreate(slave, None)
    
    #/* join the slaves in processing nodes in the pool */
    work(None)
    
    #//  RMB: etime = clock();
    
    print "integral = %lf" % glob.tree.integral
    #//  RMB: printf("time = %d milliseconds\n",(etime - stime));
    
    p5_finalize()

#main(int argc,char *argv[])
#{
#    char c;
#    double r;
#    int i, j, thrdranks[MAXTHREADS];
#    long stime,etime;
#    struct tree_node *t_node;
#    struct tree_node *alloc_tree_node();
#    pthread_t tid[MAXTHREADS];
#    
#    
#    p5_init(1);  /* also called in slave with arg 0 */
#
#    glob = (struct globmem *) malloc(sizeof(struct globmem));
#    
#    glob->t_avail = NULL;
#    glob->q_avail = NULL;
#    pthread_mutex_init(&(glob->TAVL),NULL);
#    pthread_mutex_init(&(glob->QAVL),NULL);
#    
#    t_node = alloc_tree_node(); 
#    glob->tree = t_node;
#    
#    // printf("left boundary: ");
#    scanf("%lf",&(t_node->xl));
#    // printf("right boundary: ");
#    scanf("%lf",&(t_node->xr));
#    
#    // if (t_node->xr > 15.0)
#    // {
#        // printf("right boundary too big; try 15.0\n");
#        // exit(0);
#    // }
#    
#    /* set up original node - the midpoint, function
#       values, and first approx of integral must be
#       stored in the node
#       */
#    t_node->xm = (t_node->xl + t_node->xr) / 2.0;
#    
#    t_node->yl = func(t_node->xl);
#    t_node->ym = func(t_node->xm);
#    t_node->yr = func(t_node->xr);
#    
#    t_node->integral = (t_node->xr - t_node->xl) *
#        (t_node->yl +
#         t_node->yr +
#         (4 * t_node->ym)) / 6.0;
#    
#    t_node->status = 0;
#    t_node->parent = NULL;
#    pthread_mutex_init(&(t_node->t_lock),NULL);
#    
#    /* stack the single node */
#    askfor_update(&(glob->MO),queue_node,(void *) t_node);
#    
#    // printf("'allowable difference' for a unit: ");
#    scanf("%lf",&(glob->normdiff));
#    // printf("number of threads: ");
#    scanf("%d",&(glob->nthreads));
#
#    askfor_init(&(glob->MO),glob->nthreads);
#    
#    //  RMB: stime = clock();                /* note time includes process creation */
#    
#    /* create the slave threads */
#    for (i=1; i < glob->nthreads; i++)  /* start at 1 */
#    {
#        p5_tcreate( slave, NULL );
#    }
#    
#    /* join the slaves in processing nodes in the pool */
#    work( NULL );
#    
#    //  RMB: etime = clock();
#    
#    printf("integral = %lf\n",glob->tree->integral); 
#    //  RMB: printf("time = %d milliseconds\n",(etime - stime));
#    
#    p5_finalize();
#}
#

def getprob(v):
    rc = 1
    p = v
    #if glob.pool is not None:
    if glob.pool:
        p = glob.pool
        glob.pool = glob.pool.next
        rc = 0
    return rc
    
#int getprob(void **v)
#{
#    int rc = 1;   /* any non-zero means NO problem found */
#    struct queue_node **p;
#    
#    p = (struct queue_node **) v;
#    if (glob->pool != NULL)
#    {
#        *p = glob->pool;
#        glob->pool = glob->pool->next;
#        rc = 0;    /* FOUND a problem */
#    }
#    return(rc);
#}

def work(arg):
    rc = 0
    num_done = 0
    q_node = 0
    t_node = 0

    myrank = p5_rank() 
    p5_dprintf("MYRANK=%d\n", myrank)

    #while (askfor(&(glob->MO),getprob,(void *)&q_node) == 0)
    # notice above wants ADDRESS of glob.MO
    while (askfor(glob.MO), getprob, q_node == 0):
        num_done += 1
        t_node = q_node.node
        dealloc_queue_node(q_node)
        evaluate(t_node)
    p5_dprintf("exiting work, did %d\n", num_done)
        
    

#void *work(void *arg)
#{
#    int myrank;
#    int rc, num_done = 0;
#    struct tree_node *t_node;
#    struct queue_node *q_node;
#    
#    myrank = p5_rank();
#    p5_dprintf("MYRANK=%d\n",myrank);
#
#    while (askfor(&(glob->MO),getprob,(void *)&q_node) == 0)
#    {
##        num_done++;
#        t_node = q_node->node;
#        dealloc_queue_node(q_node);
#        evaluate(t_node);   /* process the node */
#    }
#    p5_dprintf("exiting work, did %d\n",num_done);
#}

#/* evaluate processes a node, which may cause subnodes
#   to be created and stacked.
#   */

#def evaluate(n):
#    xlm = 0
#evaluate(struct tree_node *n)
#{
#    double xlm;  /* midpoint of left interval */
#    double xrm;  /* midpoint of right interval */
#    double leftint; /* integral of left */
#    double rightint; /* integral of right */
#    double ylm,yrm;  /* evaluated function for the midpoints */
#    struct tree_node *lch,*rch;  /* pointers to children */
#    struct tree_node *p; 
#    double diff;
#    struct tree_node *alloc_tree_node();
#    
#    /* first calculate the next level of approximation to
#       see whether we are close enough
#       */
#    xlm = (n->xl + n->xm) / 2;
#    xrm = (n->xm + n->xr) / 2;
#    ylm = func(xlm);
#    yrm = func(xrm);
#    leftint = (n->xm - n->xl) * ((n->yl + n->ym + (4 * ylm)) / 6);
#    rightint = (n->xr - n->xm) * ((n->ym + n->yr + (4 * yrm)) / 6);
#    
#    
#    diff = fabs(n->integral - (leftint + rightint));
#    
#    if (diff < (glob->normdiff / (n->xr - n->xl)))
#    {
#        
#        /* keep the more accurate estimate, and process completion
#           of this node
#           */
#        n->integral = leftint + rightint;
#        postcomp(n);
#    }
#    else
#    {
#        /* build the left node and stack it in the
#           pool of work to do
#           */
#        lch = alloc_tree_node();
#        lch->xl = n->xl;
#        lch->xm = xlm;
#        lch->xr = n->xm;
#        lch->yl = n->yl;
#        lch->ym = ylm;
#        lch->yr = n->ym;
#        lch->integral = leftint;
#        lch->status = 0;
#        lch->parent = n;
#        pthread_mutex_init(&(lch->t_lock),NULL);
#
#        askfor_update(&(glob->MO),queue_node,(void *)lch);
#        
#        /* we now process the right child */
#        rch = alloc_tree_node();
#        rch->xl = n->xm;
#        rch->xm = xrm;
#        rch->xr = n->xr;
#        rch->yl = n->ym;
#        rch->ym = yrm;
#        rch->yr = n->yr;
#        rch->integral = rightint;
#        rch->status = 0;
#        rch->parent = n;
#        pthread_mutex_init(&(rch->t_lock),NULL);
#        
#        evaluate(rch);
#    }
#}

def evaluate(n):
    xlm = 0.0  # midpoint of left interval
    xrm = 0.0 # midpoint of right interval
    leftint = 0.0 # integral of left 
    rightint = 0.0 # integral of right 
    ylm = 0.0 # evaluated function for the midpoints
    yrm = 0.0 # midpoint of right interval
    lch = 0 # tree_node # pointers to children
    rch = 0 # tree_node # pointers to children
    p = 0 # tree_node
    diff = 0.0
    
    #struct tree_node *alloc_tree_node();
    #^^ what? function pointer?
    
    alloc_tree_node()
    
    # first calculate the next level of approximation to
    #   see whether we are close enough
    xlm = (n.xl + n.xm) / 2
    xrm = (n.xm + n.xr) / 2
    ylm = func(xlm)
    yrm = func(xrm)
    leftint = (n.xm - n.xl) * ((n.yl + n.ym + (4 * ylm)) / 6)
    rightint = (n.xr - n.xm) * ((n.ym + n.yr + (4 * yrm)) / 6)
    
    diff = fabs(n.integral - (leftint + rightint))
    
    if (diff < (glob.normdiff / (n.xr - n.xl))):
        # keep the more accurate estimate, and process completion
        #   of this node
        n.integral = leftint + rightint
        postcomp(n)
    else:
        # build the left node and stack it in the
        #   pool of work to do
        lch = alloc_tree_node()
        lch.xl = n.xl
        lch.xm = xlm
        lch.xr = n.xm
        lch.yl = n.yl
        lch.ym = ylm
        lch.yr = n.ym
        lch.integral = leftint
        lch.status = 0
        lch.parent = n

        #pthread_mutex_init(&(lch.t_lock),NULL)

        #askfor_update(&(glob->MO),queue_node,(void *)lch);
        # note the above asks for the ADDRESS of glob.MO
        askfor_update(glob.MO),queue_node,lch)
        
        # we now process the right child
        rch = alloc_tree_node()
        rch.xl = n.xm
        rch.xm = xrm
        rch.xr = n.xr
        rch.yl = n.ym
        rch.ym = yrm
        rch.yr = n.yr
        rch.integral = rightint
        rch.status = 0
        rch.parent = n

        #pthread_mutex_init(&(rch->t_lock),NULL);
        evaluate(rch)

# this routine handles the "completion" of a node,
#   which involves storing the answer in the parent node,
#   checking to see if this completes the parent, and processing
#   completion of the parent (if required).  The nodes are
#   returned to the avail list as they are removed from the
#   leaves of the tree (except the root!)
#
#postcomp(struct tree_node *n):
def postcomp(n):
    p = 0 #tree_node  #pointer to parent
    stat = 0   # status of the parent 
    
    p = n.parent
    if p:
        
    #if ((p = n->parent) != NULL)
        #pthread_mutex_lock(&(p->t_lock));
        p.t_lock.wait()

        if (p.status == 0):
            p.integral = 0.0
        p.integral += n.integral
        
        p.status += 1
        stat = p.status

        #pthread_mutex_unlock(&(p->t_lock));
        p.t_lock.post()
        
        dealloc_tree_node(n)
        
        #if (stat == 2)  /* if parent is complete too */
        if (stat == 2): # if parent is complete too
            postcomp(p)

# this is the function to integrate
#double func(double x)
double func(x):
    
    i = 0
    
    # the attribute "static" assures that the values do not change
    #   between invocations of the function.  That is, a single static
    #   copy is allocated and referenced by all calls to the routine.
    #static int power = 30;
    #static int firstcall = 1;
    #static double factor;
    #static double pi;
    global power = 30
    global firstcall = 1
    global factor = 0.0
    global pi = 0.0
    v = 0.0
    
    
    if firstcall:
        factor = 1
        for (i=1; (i <= (power/2)); i++)
            factor = factor * (1 - (.5 / i))
        
        pi = 4 * atan((double) 1)
        firstcall = 0
    
    #// return(pow(sin((double) (pi * x)),(double) power) / factor);
    #for (i=0; i < 20000000; i++)
    #    ;  /* dummy work */

    for i range(20000000):
        pass #dummy work

    return float(x * x)

#  this routine allocates a tree_node from globally-shared
#  memory.
#struct tree_node *alloc_tree_node()
def alloc_tree_node():
    node = 0 #tree_node
    
    #pthread_mutex_lock(&(glob->TAVL));
    glob.TAVL.wait()

    node = glob.t_avail
    if node:
        node = tree_node()
        if not node:
            print "*** out of memory in alloc_tree_node ***"
            sys.exit(3)
    else:
        glob.t_avail = node.sibling

    #pthread_mutex_unlock(&(glob->TAVL));
    glob.TAVL.post()
    return node

#  this routine frees a tree_node
#dealloc_tree_node(struct tree_node *node)
def dealloc_tree_node(node):
    #pthread_mutex_lock(&(glob->TAVL));
    glob.TAVL.wait()
    node.sibling = glob.t_avail
    glob.t_avail = node
    #pthread_mutex_unlock(&(glob->TAVL));
    glob.TAVL.post()

#  this routine allocates a queue_node from globally-shared
#  memory.
#struct queue_node *alloc_queue_node()
def alloc_queue_node():
    #struct queue_node *node;
    node = 0
    
    #pthread_mutex_lock(&(glob->QAVL));
    glob.QAVL.wait()

    node = glob.q_avail
    if node:
        #node = (struct queue_node *) malloc(sizeof(struct queue_node));
        node = queue_node()
        if not node:
            print "*** out of memory in alloc_queue_node ***"
            sys.exit(3)
    else:
        glob.q_avail = node.next
    #pthread_mutex_unlock(&(glob->QAVL));
    glob.QAVL.post()
    return node

#  this routine frees a queue_node
#dealloc_queue_node(struct queue_node *node)
def dealloc_queue_node(node):
    #pthread_mutex_lock(&(glob->QAVL));
    glob.QAVL.wait()
    node.next = glob.q_avail
    glob.q_avail = node
    #pthread_mutex_unlock(&(glob->QAVL));
    glob.QAVL.post()

#  this node adds a tree_node to the pool of work.
#  This involves allocating a queue_node and hooking
#  it into the pool.  Because the pool is constantly
#  being altered by all of the processes, this must
#  be a monitor operation.
#int queue_node(struct tree_node *t_node)
def queue_node(t_node)
    #struct queue_node *alloc_queue_node();
    #function pointer?
    #alloc_queue_node = 0 #queue_node
    q_node = 0 #queue_node
    
    q_node = alloc_queue_node()
    q_node.node = t_node
    q_node.next = glob.pool
    glob.pool = q_node
    return 1          # new problem 
