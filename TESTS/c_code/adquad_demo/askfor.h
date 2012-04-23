#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <pthread.h>

#define P5_MAX_THREADS 16

struct askfor_monitor
{
    int prob_done;
    int qsize;
    int nthreads;
    pthread_mutex_t mon_lock;
    pthread_cond_t queue_cv;
};
typedef struct askfor_monitor askfor_monitor_t;

