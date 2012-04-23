#ifndef __xxshmalloc_h
#define __xxshmalloc_h

#include <errno.h>
#include <fcntl.h>
#include <semaphore.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <unistd.h>


/****
    malloc ANSI K&R C; modified to manage one block of shared memory
    To initialize a piece of memory (which might be shared):
        xx_init_shmalloc(char *memory, unsigned nbytes)
    Then call xx_shmalloc() and xx_shfree().
    We merely use the single block until it is gone.  We do not support
    the morecore routine which wouldm use sbrk, etc. to get more memory.
    This version keeps the head of the list of free blocks in the static
    variable freep.
*****/

#if !defined(MAP_ANONYMOUS) && defined(MAP_ANON) 
#define MAP_ANONYMOUS MAP_ANON 
#endif 

void xxshmalloc_init(void *memory, int nbytes);
void xxshmalloc_finalize(void);
void *xx_add_pages(unsigned int numpages);
void xx_add_to_free(void *memory, int nbytes);
void *xx_shmalloc(unsigned nbytes);
int xx_shfree(void *ap);
int xx_shfreecount(void);
void xx_print_freelist(void);
int xx_is_freed_ptr(void *ptr);

typedef long Align;

union header
{
    struct
    {
        union header *ptr;        /* next block if on free list */
        unsigned size;                /* size of this block */
    } s;
    Align x;
};

typedef union header Header;

#endif
