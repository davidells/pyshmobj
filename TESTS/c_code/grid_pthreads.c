#include <stdio.h>
#include <pthread.h>
#include <sys/time.h>
#include <sched.h>

#define MAXTHREADS      128
#define ROWS 		10000
#define COLUMNS 	10000

struct globmem
{
    double a[ROWS+2][COLUMNS+2];
    double b[ROWS+2][COLUMNS+2];
    int st[ROWS+2], pq[ROWS+1];
    int pqbeg, pqend, niters, nprocs, nrows, ncols;
    pthread_mutex_t pq_mutex;
    pthread_cond_t pq_cv;
    int nbythread[MAXTHREADS];
    pthread_mutex_t barrier_lock;
} *glob;

double avggrid();
double avgbnd();

double timestamp()
{
    struct timeval tv;

    gettimeofday( &tv, ( struct timezone * ) 0 );
    return ( tv.tv_sec + (tv.tv_usec / 1000000.0) );
}

void *slave(void *x)
{
    int id = (int)x;
    work(id);
}

phi(int x, int y)
{
    return((x * x) - (y * y) + (x * y));   
}

main(int argc, char *argv[])
{
    int i, timestart, timeend;
    double avg;
    pthread_t thread_ids[MAXTHREADS];
    int thread_args[MAXTHREADS];
    double starttime, endtime;

    if (argc < 4)
    {
	printf("usage: %s nthreads nrows ncols niters\n",argv[0]);
	exit(-1);
    }

    setbuf(stdout,NULL);

    glob = (struct globmem *) malloc(sizeof(struct globmem));

    glob->nprocs = atoi(argv[1]);
    glob->nrows = atoi(argv[2]);
    glob->ncols = atoi(argv[3]);
    glob->niters = atoi(argv[4]);

    printf("nprocs\tnnrows\tncols\tniters\n");
    printf("%d \t %d \t  %d \t  %d \t\n",
	   glob->nprocs,glob->nrows,glob->ncols,glob->niters);

    gridinit(glob->a,glob->nrows,glob->ncols);
    gridinit(glob->b,glob->nrows,glob->ncols);
    
    glob->pqbeg = glob->pqend = 0;
    for (i=1; i <= glob->nrows; i++)
        queueprob(i);

    /* initialize the status vector */
    for (i=0; i < (glob->nrows+2); i++)
        glob->st[i] = 0;

    pthread_mutex_init(&glob->pq_mutex,NULL);
    pthread_mutex_init(&glob->barrier_lock,NULL);
    pthread_mutex_lock(&glob->barrier_lock);
    glob->nbythread[0] = 0;
    pthread_cond_init(&glob->pq_cv,NULL);
    for (i=1; i <= glob->nprocs-1; i++)
    {
	thread_args[i] = i;
	glob->nbythread[i] = 0;
	pthread_create(&thread_ids[i], NULL, slave, (void *)thread_args[i]);
    }

    starttime = timestamp();
    work(0);
    endtime = timestamp();

    for (i=1; i <= glob->nprocs-1; i++)
    {
	pthread_join(thread_ids[i],NULL);
    }

    /* 
    printf("the resulting grid:\n");
    if (glob->niters % 2 == 0)
        printgrid(glob->a,glob->nrows,glob->ncols);
    else
        printgrid(glob->b,glob->nrows,glob->ncols);
    */
    if (glob->niters % 2 == 0)
        avg = avggrid(glob->a,glob->nrows,glob->ncols);
    else
        avg = avggrid(glob->b,glob->nrows,glob->ncols);
    printf("average value of grid = %f\n",avg);
    for (i=0; i <= glob->nprocs-1; i++)
    {
	printf("done by %d : %d\n",i,glob->nbythread[i]);
    }
    printf("time = %f\n",endtime-starttime);
}

/* "m" is the matrix, "r" is the number of nrows of data (m[1]-m[r];
   m[0] and m[r+1] are boundaries), and "c" is the number of ncols
   of data.
*/

gridinit(double m[ROWS+2][COLUMNS+2], int r, int c)
{
    int i, j;
    double bndavg;
    
    for (j=0; j < (c + 2); j++)
    {
        m[0][j] = phi(1,j+1);
        m[r+1][j]= phi(r+2,j+1);
    }
    for (i=1; i < (r + 2); i++)
    {
        m[i][0] = phi(i+1,1);
        m[i][c+1] = phi(i+1,c+2);
    }
    bndavg = avgbnd(m,r,c);
    printf("boundary average = %f\n",bndavg);

    /* initialize the interior of the grids to the average over the boundary*/
    for (i=1; i <= r; i++)
        for (j=1; j <= c; j++)
            /* m[i][j] = bndavg; this optimization hinders debugging */
	    m[i][j] = 0;
}

queueprob(int x)
{
    glob->pq[glob->pqend] = x;
    glob->pqend = (glob->pqend + 1) % (ROWS + 1);
}

compute(double p[ROWS+2][COLUMNS+2], double q[ROWS+2][COLUMNS+2], int r, int ncols)
{
    int j;

    for (j = 1; j <= ncols; j++) 
        q[r][j] = (p[r-1][j] + p[r+1][j] + p[r][j-1] + p[r][j+1]) / 4.0;
}

int putprob(int r)
{
    int qprob;

    qprob = 0;
    glob->st[r]++;
    if (r == 1)
        glob->st[0] = glob->st[r];
    else if (r == glob->nrows)
        glob->st[glob->nrows+1] = glob->st[r];

    if (glob->st[r] < glob->niters)
    {
        if ((r > 1) && (glob->st[r-2] >= glob->st[r]) 
		    && (glob->st[r-1] == glob->st[r]))
	{
            queueprob(r-1);
            qprob = 1;
        }
        if (r < glob->nrows && glob->st[r+1] == glob->st[r] 
			   && glob->st[r+1] <= glob->st[r+2])
	{
            queueprob(r+1);
            qprob = 1;
        }
        if (glob->st[r-1] == glob->st[r] && 
	    glob->st[r] == glob->st[r+1])
	{
            queueprob(r);
            qprob = 1;
        }
    }
    if (qprob)
        return(1);		/* new problem */
    else
	return(0);		/* no new problem */
}

int getprob(int *v)
{
    int rc = 1;
    int *p = (int *) v;

    if (glob->pqbeg != glob->pqend) 
    {
	/* printf("PROB AT %d IS %d\n",glob->pqbeg,glob->pq[glob->pqbeg]); */
	*p = glob->pq[glob->pqbeg];
	glob->pqbeg = (glob->pqbeg+1) % (ROWS + 1); 
	rc = 0;
    }
    return(rc);
}

work(int myid)			/* main routine for all processes */
{
    int r,rc,i;

    if (myid == 0)
	pthread_mutex_unlock(&glob->barrier_lock);
    pthread_mutex_lock(&glob->barrier_lock);
    pthread_mutex_unlock(&glob->barrier_lock);

    pthread_mutex_lock(&glob->pq_mutex);
    rc = getprob(&r);
    pthread_mutex_unlock(&glob->pq_mutex);
    while (rc == 0)
    {
	glob->nbythread[myid]++;
	if ((glob->st[r] % 2) == 0)
	{
	    compute(glob->a,glob->b,r,glob->ncols);
	    /* printf("%d: computing to B row=%d\n",myid,r); */
	}
	else 
	{
	    compute(glob->b,glob->a,r,glob->ncols);
	    /* printf("%d: computing to A row=%d\n",myid,r); */
	}
	pthread_mutex_lock(&glob->pq_mutex);
	putprob(r);
	rc = getprob(&r);
	pthread_mutex_unlock(&glob->pq_mutex);
	// sched_yield();
    }
}

printgrid(double m[ROWS+2][COLUMNS+2], int r, int c)
{
    int i,j;
    for (i = 0; i < (r+2); i++)
	for (j = 0; j < (c+2); j++)
	    printf("%3d %3d %10.5f\n",i,j,m[i][j]);
}

double avggrid(double m[ROWS+2][COLUMNS+2], int r, int c)
{
    int i,j;
    double avg = 0;

    for (i = 0; i < (r+2); i++)
	for (j = 0; j < (c+2); j++)
	    avg += m[i][j];
    return(avg/((r+2)*(c+2)));
}

double avgbnd(double m[ROWS+2][COLUMNS+2], int r, int c)
{
    int i,j;
    double avg = 0;

    for (i = 0; i < (r+2); i++)
	    avg += m[i][0];
    for (i = 0; i < (r+2); i++)
	    avg += m[i][c+1];
    for (i = 1; i < (c+1); i++)
	    avg += m[0][i];
    for (i = 1; i < (c+1); i++)
	    avg += m[r+1][i];
    return(avg/(2*(c+2) + 2*(r+2) - 4)); /* average over boundary */
}

