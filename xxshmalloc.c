#include "xxshmalloc.h"

static Header **sh_freep = NULL;       /* start of free list */
sem_t *xxshmalloc_sem;
char xxshmalloc_semname[80];

void xxshmalloc_init(void *memory, int nbytes)
{ 
    /* this is essentially a one-time version of K&R's morecore */
    unsigned nunits;
    Header *up;
    Header **sh_freep_temp;

    //Open semaphore for locking down access to sh_freep
    snprintf(xxshmalloc_semname, 80, "pyshmobj_%d_xxshmalloc_sem", getpid());
    xxshmalloc_sem = sem_open(xxshmalloc_semname, O_CREAT, 0600, 1);
    if (xxshmalloc_sem == (sem_t *) SEM_FAILED) {
        perror("error in sem_open call in xxshmalloc_init");
        if(errno == ESPIPE)
            printf("you may need write permission in /dev/shm\n");
    }

    //Init shared mem
    sh_freep = (Header**)malloc(sizeof(Header**));

    nunits = (nbytes - sizeof(Header)) / sizeof(Header);
    *sh_freep = (Header *) memory;
    (*sh_freep)->s.ptr = *sh_freep;
    (*sh_freep)->s.size = 0;
    up = (Header *) memory + 1;
    up->s.size = nunits;
    xx_shfree((void*)(up+1));

    // printf("INIT: *sh_freep=%x\n",(void*)*sh_freep);
    // printf("INIT: sohdr=%d nunits=%d\n",sizeof(Header),nunits);
    // printf("INIT: freeing=%x\n",(up+1));
    // printf("INIT: *sh_freep=%x, nunits=%d, *sh_freep->s.size=%d\n",
    //        (void*)*sh_freep, nunits, *sh_freep->s.size);

    //Here we move the sh_freep pointer into shared mem.
    sh_freep_temp = (Header**)xx_shmalloc(sizeof(Header**));
    *sh_freep_temp = *sh_freep;
    free(sh_freep);
    sh_freep = sh_freep_temp;

    // printf("INIT: *sh_freep=%x\n",(void*)*sh_freep);
}

void xxshmalloc_finalize()
{
    sem_close(xxshmalloc_sem);
    sem_unlink(xxshmalloc_semname);
}

void *xx_add_pages(unsigned int numpages)
{
    /* Allocate the specified number of shared memory pages using mmap */
    void *shmem;
    int shmemsz;
    int mmap_prot, mmap_flags;
    static int init_done = 0;
    
    if(numpages == 0)
        return NULL;

    shmemsz = numpages * getpagesize();
    mmap_prot = PROT_WRITE|PROT_READ;
    mmap_flags = MAP_ANONYMOUS | MAP_SHARED;

    shmem = mmap(0,shmemsz,mmap_prot,mmap_flags,-1,0); 
    if (shmem == (void *) -1) {
       perror("mmap in xx_add_pages");
       return NULL;
    }
    //printf("mmap to address %x\n", shmem);

    //printf("shmem_name=%s, is_new_shmem=%d\n", shmem_name, is_new_shmem);
    if(init_done == 0){
        xxshmalloc_init(shmem, shmemsz);
        init_done = 1;
    } else
        xx_add_to_free(shmem, shmemsz);

    return shmem;
}

void xx_add_to_free(void *memory, int nbytes)
{
    /* Adds the space pointed to by ptr memory 
     * to the free list of shmalloc mem. */

    unsigned nunits;
    Header *up;

    nunits = (nbytes - sizeof(Header)) / sizeof(Header);
    up = (Header *) memory + 1;
    up->s.size = nunits;
    xx_shfree((void*)(up+1));
}

void *xx_shmalloc(unsigned nbytes)
{
    Header *p, *prevp;
    unsigned nunits;

    nunits = ((nbytes + sizeof(Header) - 1) / sizeof(Header)) + 1;

    // printf("SHMALLOC: nbytes=%d *sh_freep=%u nunits=%d\n",
    //         nbytes,*sh_freep,nunits);

    if( sem_wait(xxshmalloc_sem) != 0 ){
        perror("error calling sem_wait in xx_shmalloc");
        return NULL;
    }

    if ((prevp = *sh_freep) == NULL) {
        printf("xx_shmalloc not yet initialized\n");
        sem_post(xxshmalloc_sem);
        exit(-1);
    }

    for (p = prevp->s.ptr; ; prevp = p, p = p->s.ptr)
    {
        if (p->s.size >= nunits)   /* big enough */
        {
            if (p->s.size == nunits)   /* exactly */
                prevp->s.ptr = p->s.ptr;
            else                       /* allocate tail end */
            {
                p->s.size -= nunits;
                p += p->s.size;
                p->s.size = nunits;
            }
            *sh_freep = prevp;
            // printf("SHMALLOC: returning %u\n",(void*)(p+1));
            sem_post(xxshmalloc_sem);
            return (void*)(p+1);
        }

        if (p == *sh_freep){    /* wrapped around the free list */
            sem_post(xxshmalloc_sem);
            return NULL;
        }
    }
}

int xx_shfree(void *ap)
{
    Header *bp, *p;

    if (!ap)    /* RMB: Do nothing with NULL pointers */ 
        return 0;        
    if (xx_is_freed_ptr(ap)){
        //fprintf(stderr, "xx_shfree: xx_is_freed_ptr = true\n");
        return 0;
    }

    bp = (Header *) ap - 1;        /* point to block header */

    if( sem_wait(xxshmalloc_sem) != 0 ){
        perror("error calling sem_wait in xx_shmalloc");
        return -1;
    }

    for (p = *sh_freep; !(bp > p && bp < p->s.ptr); p = p->s.ptr)
        if (p >= p->s.ptr && (bp > p || bp < p->s.ptr)) 
        {
            //printf("FREE: p=%x\n",p);
            break;                /* freed block at start or end of arena */
        }

    if (bp + bp->s.size == p->s.ptr)
    {                                /* join to upper nbr */
        bp->s.size += p->s.ptr->s.size;
        bp->s.ptr = p->s.ptr->s.ptr;
    }
    else
        bp->s.ptr = p->s.ptr;

    if (p + p->s.size == bp)
    {                                /* join to lower nbr */
        p->s.size += bp->s.size;
        p->s.ptr = bp->s.ptr;
    }
    else
        p->s.ptr = bp;

    *sh_freep = p;
    //printf("FREE: *sh_freep=%x, bp=%x, bp->s.size=%d\n",
    //        *sh_freep, bp, bp->s.size);
    sem_post(xxshmalloc_sem);
    return 0;
}


//Debug function
int xx_shfreecount(void)
{
    Header *p, *prevp;
    int count = 0;

    if( sem_wait(xxshmalloc_sem) != 0 ){
        perror("error calling sem_wait in xx_shmalloc");
        return -1;
    }

    if ((prevp = *sh_freep) == NULL)
    {
        printf("xx_shmalloc not yet initialized\n");
	    exit(-1);
    }

    for (p = prevp->s.ptr; ; prevp = p, p = p->s.ptr)
    {
        count += p->s.size;
        if (p == *sh_freep)    /* wrapped around the free list */
            break;    /* none left */
    }
    sem_post(xxshmalloc_sem);
    return count;
}

//Debug function
void xx_print_freelist(void)
{
    Header *p, *prevp;

    if( sem_wait(xxshmalloc_sem) != 0 ){
        perror("error calling sem_wait in xx_shmalloc");
        return;
    }

    if ((prevp = *sh_freep) == NULL)
    {
        printf("xx_shmalloc not yet initialized\n");
	    exit(-1);
    }

    printf("*sh_freep=%x, (*sh_freep)->s.ptr=%x\n", 
            (unsigned int)*sh_freep, (unsigned int)((*sh_freep)->s.ptr));

    for (p = prevp->s.ptr; ; prevp = p, p = p->s.ptr) {
        printf("p=%x, p->s.ptr=%x, p->s.size=%d\n", 
               (unsigned int)p, (unsigned int)(p->s.ptr), p->s.size);
        if (p == *sh_freep)    /* wrapped around the free list */
            break;    /* none left */
    }
    sem_post(xxshmalloc_sem);
}

int xx_is_freed_ptr(void *ptr)
{
    Header *p, *prevp, *hptr;
    hptr = (Header*)ptr;

    if( sem_wait(xxshmalloc_sem) != 0 ){
        perror("error calling sem_wait in xx_shmalloc");
        return -1;
    }

    if ((prevp = *sh_freep) == NULL)
    {
        printf("xx_shmalloc not yet initialized\n");
	    exit(-1);
    }

    for (p = prevp->s.ptr; ; prevp = p, p = p->s.ptr) {
        //fprintf(stderr, "xx_is_freed_ptr: p = %x, p + p->s.size = %x, ptr = %x in range? %d\n",
        //                                  p, p + p->s.size, ptr, (p <= ptr && ptr <= (p + p->s.size)));
        if(p <= hptr && hptr <= (p + p->s.size)){
            sem_post(xxshmalloc_sem);
            return 1;
        }
        if (p == *sh_freep){    /* wrapped around the free list */
            sem_post(xxshmalloc_sem);
            return 0;    /* none left */
        }
    }
}
