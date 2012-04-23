#include "askfor.h"

static int next_rank = 0, next_tid = 0;
static pthread_key_t datakey;
static pthread_t tids[P5_MAX_THREADS];
static pthread_mutex_t dprintf_lock;

static void freedata(void *);
static void freedata(void *p)
{
    free(p);
}

/* only called once per thread; only called with flag = 1 once during pgm */
void p5_init(int flag)
{
    int *p;

    if (flag)
    {
        pthread_key_create(&datakey,freedata);
        pthread_mutex_init(&dprintf_lock,NULL);
    }
    p = (int *) malloc(sizeof(int)); /* assume malloc thread-safe */
    *p = next_rank++;
    pthread_setspecific(datakey,(void *)p);
}

int p5_rank()
{
    int *p;

    p = (int *) pthread_getspecific(datakey);
    return *p;
}


void p5_dprintf(char *fmt, ...)
{
    int rank;
    va_list ap;

    rank = *( (int *)pthread_getspecific(datakey) );
    pthread_mutex_lock(&dprintf_lock);
    va_start( ap, fmt );
    printf("%d: ",rank);
    vprintf(fmt, ap);
    va_end(ap);
    fflush(stdout);
    pthread_mutex_unlock(&dprintf_lock);
}

void p5_tcreate( void *(*sub)(void *), void *arg)
{
    pthread_create(&tids[next_tid++], NULL, sub, arg);
}

void p5_finalize()
{
    int i;

    for (i=0; i < next_tid; i++)
        pthread_join(tids[i],NULL);
}

void askfor_init(struct askfor_monitor *afm, int nthreads)
{
    afm->prob_done = 0;
    afm->qsize = 0;
    afm->nthreads = nthreads;
    pthread_mutex_init(&(afm->mon_lock),NULL);
    pthread_cond_init(&(afm->queue_cv),NULL);
}

int askfor(struct askfor_monitor *afm,
           int (*getprob_fxn)(void *),
           void *problem)
{
    int rc, work_found;

    pthread_mutex_lock(&(afm->mon_lock));
    work_found = 0;
    while ( ! work_found  &&  ! afm->prob_done)
    {
        rc = (*getprob_fxn)(problem);
        if (rc == 0)  /* got work */
        {
            work_found = 1;
        }
        else if (afm->qsize == afm->nthreads-1)
        {
            afm->prob_done = 1;
        }
        else
        {
            afm->qsize++;  /* I am now on the queue */
            /* It's OK to come out for a "spurious" reason; I'm in a big loop */
            pthread_cond_wait( &(afm->queue_cv), &(afm->mon_lock) );
            afm->qsize--;
        }
    }
    if (afm->qsize > 0)
        pthread_cond_signal(&(afm->queue_cv));
    pthread_mutex_unlock(&(afm->mon_lock));
    if (afm->prob_done)
        rc = afm->prob_done;
    else  /* work_found */
        rc = 0;
    return rc;
}

void askfor_update(struct askfor_monitor *afm,
                   int (*putprob_fxn)(void *),
                   void *problem)
{
    pthread_mutex_lock(&(afm->mon_lock));
    if (putprob_fxn(problem))
    {
        pthread_cond_signal(&(afm->queue_cv));
    }
    pthread_mutex_unlock(&(afm->mon_lock));
}

void askfor_probend(struct askfor_monitor *afm, int code)
{
    pthread_mutex_lock(&(afm->mon_lock));
    afm->prob_done = code;
    pthread_mutex_unlock(&(afm->mon_lock));
}
