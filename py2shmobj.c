#include <Python.h>

#include <fcntl.h>
#include <semaphore.h>
#include <stdlib.h>
#include <sys/ipc.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <unistd.h>

#include "dict.h"
#include "list.h"
#include "xxshmalloc.h"

/* Tweakables */
#define PYSHMOBJ_INIT_SHMEM_PAGES 8

/* following must match values in shmobj.py */
#define TYPEINT 1
#define TYPEDBL 2
#define TYPESTR 3 
#define TYPELST 4
#define TYPEDCT 5
#define TYPEPTR 9  

int PYSHMOBJ_PAGESIZE;

//-------------------------------
//Int Methods
//-------------------------------

PyObject *py2shmint_alloc(PyObject *self, PyObject *args)
{
    int *p;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,""))
        return NULL;

    p = (int *) xx_shmalloc(sizeof(int));
    if(p == NULL)
        Py_RETURN_NONE;    

    cobj = PyCObject_FromVoidPtr((void*)p,NULL);
    return cobj;
}

PyObject *py2shmint_set(PyObject *self, PyObject *args)
{
    int *p, val;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"Oi",&cobj,&val))
        return NULL;
    p = (int *) PyCObject_AsVoidPtr(cobj);
    *p = val;
    Py_RETURN_NONE;    
}

PyObject *py2shmint_get(PyObject *self, PyObject *args)
{
    int *p;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"O",&cobj))
        return NULL;
    p = (int *) PyCObject_AsVoidPtr(cobj);
    if(xx_is_freed_ptr((void*)p))
       Py_RETURN_NONE; 
    else
        return Py_BuildValue("i",*p);
}



//-------------------------------
//Double Methods
//-------------------------------

PyObject *py2shmdbl_alloc(PyObject *self, PyObject *args)
{
    double *p;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,""))
        return NULL;
    p = (double *) xx_shmalloc(sizeof(double));
    if(p == NULL)
        Py_RETURN_NONE;    
    cobj = PyCObject_FromVoidPtr((void*)p,NULL);
    return cobj;
}

PyObject *py2shmdbl_set(PyObject *self, PyObject *args)
{
    double *p, val;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"Od",&cobj,&val))
        return NULL;
    p = (double *) PyCObject_AsVoidPtr(cobj);
    *p = val;
    Py_RETURN_NONE;    
}

PyObject *py2shmdbl_get(PyObject *self, PyObject *args)
{
    double *p;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"O",&cobj))
        return NULL;
    p = (double *) PyCObject_AsVoidPtr(cobj);
    if(xx_is_freed_ptr((void*)p))
       Py_RETURN_NONE; 
    else
        return Py_BuildValue("f",*p);
}

//-------------------------------
//String Methods
//-------------------------------

PyObject *py2shmstr_alloc(PyObject *self, PyObject *args)
{
    int slen;
    char *p;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"i",&slen))
        return NULL;
    p = (char *) xx_shmalloc(slen + 1);  /* include room for null */
    if(p == NULL)
        Py_RETURN_NONE;    
    cobj = PyCObject_FromVoidPtr((void*)p,NULL);
    return cobj;
}

PyObject *py2shmstr_set(PyObject *self, PyObject *args)
{
    char *p;
    char *str;
    int slen;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"Os#",&cobj,&str,&slen))
        return NULL;
    p = (char *) PyCObject_AsVoidPtr(cobj);
    memcpy(p,str,slen);
    p[slen] = 0; //and the terminating null byte
    Py_RETURN_NONE;    
}

PyObject *py2shmstr_get(PyObject *self, PyObject *args)
{
    char *p;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"O",&cobj))
        return NULL;
    p = (char *) PyCObject_AsVoidPtr(cobj);
    if(xx_is_freed_ptr((void*)p))
       Py_RETURN_NONE; 
    else
        return Py_BuildValue("s",p);
}


//-------------------------------
//Pointer Methods
//-------------------------------
PyObject *py2shmptr_alloc(PyObject *self, PyObject *args)
{
    void *p;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,""))
        return NULL;
    p = (void *) xx_shmalloc(sizeof(void*));
    if(p == NULL)
        Py_RETURN_NONE;    
    cobj = PyCObject_FromVoidPtr((void*)p,NULL);
    return cobj;
}

PyObject *py2shmptr_set(PyObject *self, PyObject *args)
{
    int **p;
    void *a;
    PyObject *cobj,*cobja;

    if ( ! PyArg_ParseTuple(args,"OO",&cobj,&cobja))
        return NULL;
    p = (int **)PyCObject_AsVoidPtr(cobj);
    a = PyCObject_AsVoidPtr(cobja);
    *p = (int*)a;
    Py_RETURN_NONE;    
}

PyObject *py2shmptr_get(PyObject *self, PyObject *args)
{
    int **p;
    void *a;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"O",&cobj))
        return NULL;

    p = (int **)PyCObject_AsVoidPtr(cobj);
    if(xx_is_freed_ptr((void*)p))
        Py_RETURN_NONE; 

    a = (void*)*p;
    cobj = PyCObject_FromVoidPtr((void*)a,NULL);
    return cobj;
}


//-------------------------------
//Dictionary Methods
//-------------------------------

static int dict_compare_keys_func(const void *key1, const void *key2)
{
    //Note this implies a max key length of 255.
    return strncmp(key1, key2, 255);
}

PyObject *py2shmdict_init(PyObject *self, PyObject *args)
{
    dict_t *d;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,""))
        return NULL;
    d = (dict_t *) xx_shmalloc(sizeof(dict_t));
    if(d == NULL)
        Py_RETURN_NONE;    
	dict_init(d, DICTCOUNT_T_MAX, dict_compare_keys_func);
    cobj = PyCObject_FromVoidPtr((void*)d,NULL);
    return cobj;
}

PyObject *py2shmdict_insert(PyObject *self, PyObject *args)
{
    dict_t *d;
    dnode_t *np;
    void *key;
    PyObject *cobjd,*cobjdn,*cobjk;

    if ( ! PyArg_ParseTuple(args,"OOO", &cobjd, &cobjdn, &cobjk))
        return NULL;
    d = (dict_t*)PyCObject_AsVoidPtr(cobjd);
    np = (dnode_t*)PyCObject_AsVoidPtr(cobjdn);
    key = PyCObject_AsVoidPtr(cobjk);

    dict_insert(d, np, key);
    Py_RETURN_NONE;    
}

PyObject *py2shmdict_first(PyObject *self, PyObject *args)
{
    dict_t *dp;
    dnode_t *np;
    PyObject *cobjd,*cobjn;

    if ( ! PyArg_ParseTuple(args,"O",&cobjd))
        return NULL;
    dp = (dict_t *) PyCObject_AsVoidPtr(cobjd);
    np = dict_first(dp);
    if(np == NULL){
	    Py_RETURN_NONE;  
    } else {
	    cobjn = PyCObject_FromVoidPtr((void*)np,NULL);
	    return cobjn;
    }
}

PyObject *py2shmdict_next(PyObject *self, PyObject *args)
{
    dict_t *dp;
    dnode_t *np;
    PyObject *cobjd,*cobjn;

    if ( ! PyArg_ParseTuple(args,"OO",&cobjd,&cobjn))
        return NULL;
    dp = (dict_t *) PyCObject_AsVoidPtr(cobjd);
    np = (dnode_t *) PyCObject_AsVoidPtr(cobjn);
    np = dict_next(dp,np);
    if(np == NULL){
	    Py_RETURN_NONE;  
    } else {
	    cobjn = PyCObject_FromVoidPtr((void*)np,NULL);
	    return cobjn;
    }
}

PyObject *py2shmdict_lookup(PyObject *self, PyObject *args)
{
    dict_t *dp;
    dnode_t *np;
    char *key;
    PyObject *cobjd,*cobjn;

    if ( ! PyArg_ParseTuple(args,"Os",&cobjd,&key))
        return NULL;
    dp = (dict_t *) PyCObject_AsVoidPtr(cobjd);

    np = dict_lookup(dp,key);
    if (np == NULL) {
        Py_RETURN_NONE;
    } else {
        cobjn = PyCObject_FromVoidPtr((void*)np,NULL);
        return Py_BuildValue("O", cobjn);    
    }
}

PyObject *py2shmdict_remove(PyObject *self, PyObject *args)
{
    dict_t *dp;
    dnode_t *np;
    PyObject *cobjd,*cobjn;

    if ( ! PyArg_ParseTuple(args,"OO",&cobjd,&cobjn))
        return NULL;
    dp = (dict_t *) PyCObject_AsVoidPtr(cobjd);
    np = (dnode_t *) PyCObject_AsVoidPtr(cobjn);
    dict_delete(dp,np);
    Py_RETURN_NONE;    
}

PyObject *py2shmdict_count(PyObject *self, PyObject *args)
{
    dict_t *d;
    PyObject *cobjd;
    unsigned long count;

    if ( ! PyArg_ParseTuple(args, "O", &cobjd))
        return NULL;
    d = (dict_t *)PyCObject_AsVoidPtr(cobjd);
    count = dict_count(d);
    return Py_BuildValue("k", count);
}
    

//-------------------------------
//Dictionary Node Methods
//-------------------------------
PyObject *py2shmdnode_alloc(PyObject *self, PyObject *args)
{
    dnode_t *np;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,""))
        return NULL;
    np = (dnode_t *) xx_shmalloc(sizeof(dnode_t));
    if(np == NULL)
        Py_RETURN_NONE;
    cobj = PyCObject_FromVoidPtr((void*)np,NULL);
    return cobj;
}

PyObject *py2shmdnode_init(PyObject *self, PyObject *args)
{
    void *ep;
    dnode_t *np;
    int type, len;
    PyObject *cobjn,*cobje;

    if ( ! PyArg_ParseTuple(args,"OOii",&cobjn,&cobje,&type,&len))
        return NULL;
    np = PyCObject_AsVoidPtr(cobjn);
    ep = PyCObject_AsVoidPtr(cobje);
    dnode_init(np,ep,type,len);  /* make ptr to an element the data value in a dict node */
    Py_RETURN_NONE;    
}

PyObject *py2shmdnode_get(PyObject *self, PyObject *args)
{
    void *ep;
    dnode_t *np;
    int type, len;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"O",&cobj))
        return NULL;
    np = (dnode_t *) PyCObject_AsVoidPtr(cobj);
    ep = dnode_get(np, &type, &len);

    if(xx_is_freed_ptr(ep))
        return Py_BuildValue("(Oii)", Py_None, 0, 0);

    cobj = PyCObject_FromVoidPtr((void*)ep,NULL);
    return Py_BuildValue("(Oii)",cobj,type,len);
}

PyObject *py2shmdnode_put(PyObject *self, PyObject *args)
{
    void *ep;
    dnode_t *np;
    int type, len;
    PyObject *cobjn,*cobje;

    if ( ! PyArg_ParseTuple(args,"OOii",&cobjn,&cobje,&type,&len))
        return NULL;
    np = PyCObject_AsVoidPtr(cobjn);
    ep = PyCObject_AsVoidPtr(cobje);
    dnode_put(np,ep,type,len);  
    Py_RETURN_NONE;
}

PyObject *py2shmdnode_getkey(PyObject *self, PyObject *args)
{
    void *kp;
    dnode_t *np;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args, "O", &cobj))
        return NULL;

    np = (dnode_t *) PyCObject_AsVoidPtr(cobj);
    kp = (void *) dnode_getkey(np);
    if(xx_is_freed_ptr(kp))
        Py_RETURN_NONE;

    cobj = PyCObject_FromVoidPtr(kp, NULL);
    return Py_BuildValue("O", cobj);
}


//-------------------------------
//List Methods
//-------------------------------
PyObject *py2shmlist_init(PyObject *self, PyObject *args)
{
    list_t *p;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,""))
        return NULL;
    p = (list_t *) xx_shmalloc(sizeof(list_t));
    if(p == NULL)
        Py_RETURN_NONE;    
    list_init(p);
    cobj = PyCObject_FromVoidPtr((void*)p,NULL);
    return cobj;
}

PyObject *py2shmlist_append(PyObject *self, PyObject *args)
{
    list_t *lp;
    list_node_t *np;
    PyObject *cobjl,*cobjn;

    if ( ! PyArg_ParseTuple(args,"OO",&cobjl,&cobjn))
        return NULL;
    lp = (list_t *) PyCObject_AsVoidPtr(cobjl);
    np = (list_node_t *) PyCObject_AsVoidPtr(cobjn);
    list_append(lp,np);
    Py_RETURN_NONE;    
}

PyObject *py2shmlist_insert(PyObject *self, PyObject *args)
{
    int index;
    list_t *lp;
    list_node_t *np, *np_at_index;
    PyObject *cobjl,*cobjn;

    if ( ! PyArg_ParseTuple(args,"OiO",&cobjl,&index,&cobjn))
        return NULL;

    lp = (list_t *) PyCObject_AsVoidPtr(cobjl);
    np = (list_node_t *) PyCObject_AsVoidPtr(cobjn);

    if(index >= list_count(lp)){
       list_append(lp, np);
    } else {
        np_at_index = list_get_node(lp,index);
        if(np_at_index == NULL){
            return NULL;
        }
        list_insert_before(lp, np, np_at_index);
    }
    Py_RETURN_NONE;    

}

PyObject *py2shmlist_remove(PyObject *self, PyObject *args)
{
    list_t *lp;
    list_node_t *np;
    PyObject *cobjl,*cobjn;

    if ( ! PyArg_ParseTuple(args,"OO",&cobjl,&cobjn))
        return NULL;
    lp = (list_t *) PyCObject_AsVoidPtr(cobjl);
    np = (list_node_t *) PyCObject_AsVoidPtr(cobjn);
    list_remove(lp,np);
    Py_RETURN_NONE;    
}

PyObject *py2shmlist_first(PyObject *self, PyObject *args)
{
    list_t *lp;
    list_node_t *np;
    PyObject *cobjl,*cobjn;

    if ( ! PyArg_ParseTuple(args,"O",&cobjl))
        return NULL;
    lp = (list_t *) PyCObject_AsVoidPtr(cobjl);
    np = list_first(lp);
    if(np == NULL){
	    Py_RETURN_NONE;  
    } else {
	    cobjn = PyCObject_FromVoidPtr((void*)np,NULL);
	    return cobjn;
    }
}

PyObject *py2shmlist_last(PyObject *self, PyObject *args)
{
    list_t *lp;
    list_node_t *np;
    PyObject *cobjl,*cobjn;

    if ( ! PyArg_ParseTuple(args,"O",&cobjl))
        return NULL;
    lp = (list_t *) PyCObject_AsVoidPtr(cobjl);
    np = list_last(lp);
    if(np == NULL){
	    Py_RETURN_NONE;  
    } else {
	    cobjn = PyCObject_FromVoidPtr((void*)np,NULL);
	    return cobjn;
    }
}

PyObject *py2shmlist_next(PyObject *self, PyObject *args)
{
    list_t *lp;
    list_node_t *np;
    PyObject *cobjl,*cobjn;

    if ( ! PyArg_ParseTuple(args,"OO",&cobjl,&cobjn))
        return NULL;
    lp = (list_t *) PyCObject_AsVoidPtr(cobjl);
    np = (list_node_t *) PyCObject_AsVoidPtr(cobjn);
    np = list_next(lp,np);
    if(np == NULL){
	    Py_RETURN_NONE;  
    } else {
	    cobjn = PyCObject_FromVoidPtr((void*)np,NULL);
	    return cobjn;
    }
}

PyObject *py2shmlist_prev(PyObject *self, PyObject *args)
{
    list_t *lp;
    list_node_t *np;
    PyObject *cobjl,*cobjn;

    if ( ! PyArg_ParseTuple(args,"OO",&cobjl,&cobjn))
        return NULL;
    lp = (list_t *) PyCObject_AsVoidPtr(cobjl);
    np = (list_node_t *) PyCObject_AsVoidPtr(cobjn);
    np = list_prev(lp,np);
    if(np == NULL){
	    Py_RETURN_NONE;  
    } else {
	    cobjn = PyCObject_FromVoidPtr((void*)np,NULL);
	    return cobjn;
    }
}

PyObject *py2shmlist_getnode(PyObject *self, PyObject *args)
{
    int index;
    list_t *lp;
    list_node_t *np;
    PyObject *cobjl, *cobjn;

    if ( ! PyArg_ParseTuple(args,"Oi",&cobjl,&index))
        return NULL;

    lp = (list_t *) PyCObject_AsVoidPtr(cobjl);
    np = list_get_node(lp,index);
    if (np == NULL)
        Py_RETURN_NONE;

    cobjn = PyCObject_FromVoidPtr((void*)np,NULL);
    return cobjn;
}

PyObject *py2shmlist_count(PyObject *self, PyObject *args)
{
    list_t *lp;
    PyObject *cobjl;

    if ( ! PyArg_ParseTuple(args,"O",&cobjl))
        return NULL;
    lp = (list_t *) PyCObject_AsVoidPtr(cobjl);
    return Py_BuildValue("i",list_count(lp));
}

//-------------------------------
//List Node Methods
//-------------------------------
PyObject *py2shmlnode_alloc(PyObject *self, PyObject *args)
{
    list_node_t *np;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,""))
        return NULL;
    np = (list_node_t *) xx_shmalloc(sizeof(list_node_t));
    if(np == NULL)
        Py_RETURN_NONE;    
    cobj = PyCObject_FromVoidPtr((void*)np,NULL);
    return cobj;
}

PyObject *py2shmlnode_init(PyObject *self, PyObject *args)
{
    void *ep;
    list_node_t *np;
    int type, len;
    PyObject *cobjn,*cobje;

    if ( ! PyArg_ParseTuple(args,"OOii",&cobjn,&cobje,&type,&len))
        return NULL;
    if (type == TYPEINT)
	len = sizeof(int);
    np = PyCObject_AsVoidPtr(cobjn);
    ep = PyCObject_AsVoidPtr(cobje);
    list_node_init(np,ep,type,len);  /* make ptr to an element the data value in a list node */
    Py_RETURN_NONE;    
}

PyObject *py2shmlnode_put(PyObject *self, PyObject *args)
{
    void *ep;
    list_node_t *np;
    int type, len;
    PyObject *cobjn,*cobje;

    if ( ! PyArg_ParseTuple(args,"OOii",&cobjn,&cobje,&type,&len))
        return NULL;
    np = PyCObject_AsVoidPtr(cobjn);
    ep = PyCObject_AsVoidPtr(cobje);
    list_node_fill(np,ep,type,len);  /* make ptr to an element the data value in a list node */
    Py_RETURN_NONE;    
}

PyObject *py2shmlnode_get(PyObject *self, PyObject *args)
{
    void *ep;
    list_node_t *np;
    int type, len;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"O",&cobj))
        return NULL;
    np = (list_node_t *) PyCObject_AsVoidPtr(cobj);
    ep = list_node_data(np,&type,&len);
    if(xx_is_freed_ptr(ep))
        return Py_BuildValue("(Oii)", Py_None, 0, 0);

    cobj = PyCObject_FromVoidPtr((void*)ep,NULL);
    return Py_BuildValue("(Oii)",cobj,type,len);
}


//-------------------------------
//Semaphore Methods
//-------------------------------
PyObject *py2shmsem_open(PyObject *self, PyObject *args)
{
    sem_t *sem;
    char *semname;
    int semval;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"si",&semname,&semval))
        return NULL;

    sem = sem_open(semname, O_CREAT, 0600, semval);
    //printf("SEMNAME %d :%s:\n",strlen(semname),semname);
    if (sem == (sem_t *) SEM_FAILED)
    {
        perror("error in sem_open call in py2shmsem_open");
        if(errno == ESPIPE)
            printf("you may need write permission in /dev/shm\n");
        return NULL;
    }
    cobj = PyCObject_FromVoidPtr((void*)sem,NULL);
    return Py_BuildValue("O", cobj);
}

PyObject *py2shmsem_wait(PyObject *self, PyObject *args)
{
    sem_t *sem;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"O",&cobj))
        return NULL;
    
    sem = (sem_t*)PyCObject_AsVoidPtr(cobj);
    if( sem_wait(sem) != 0 ){
        perror("error calling sem_wait in py2shmsem_wait");
        return NULL;
    }
    Py_RETURN_NONE;
}

PyObject *py2shmsem_post(PyObject *self, PyObject *args)
{
    sem_t *sem;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"O",&cobj))
        return NULL;

    sem = (sem_t*)PyCObject_AsVoidPtr(cobj);
    if ( sem_post(sem) != 0 ){
        perror("error calling sem_post in py2shmsem_post");
        return NULL;   
    }
    Py_RETURN_NONE;
} 

PyObject *py2shmsem_close(PyObject *self, PyObject *args)
{
    sem_t *sem;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"O",&cobj))
        return NULL;

    sem = (sem_t*)PyCObject_AsVoidPtr(cobj);
    if ( sem_close(sem) != 0 ){
        perror("error calling sem_close in py2shmsem_close");
        return NULL;   
    }
    Py_RETURN_NONE;
} 

PyObject *py2shmsem_unlink(PyObject *self, PyObject *args)
{
    char *semname;
    if ( ! PyArg_ParseTuple(args,"s",&semname))
        return NULL;

    if (sem_unlink(semname) < 0) {
        /* We ignore ENOENT to allow multiple processes to call unlink
         * without causing an error and faulty exit. */
        /* Apparently APPLE sets EINVAL instead of ENOENT (bug) */
        if (errno != ENOENT  &&  errno != EINVAL) {
            perror("error in sem_unlink call in py2shmsem_unlink");
            return NULL;
        }
    }
    Py_RETURN_NONE;
}


//-------------------------------
//Other Methods
//-------------------------------
PyObject *py2shmobj_del(PyObject *self, PyObject *args)
{
    void *p;
    PyObject *cobj;

    if ( ! PyArg_ParseTuple(args,"O",&cobj))
        return NULL;

    p = PyCObject_AsVoidPtr(cobj);
    xx_shfree(p);
    Py_RETURN_NONE;    
}

PyObject *py2shmobj_cleanup(PyObject *self, PyObject *args)
{
    if ( ! PyArg_ParseTuple(args,""))
        return NULL;
    xxshmalloc_finalize();
    exit(0);  /* a hokey way to force exit even when python hangs at very end */
    Py_RETURN_NONE;    
}

PyObject *py2shmobj_equals(PyObject *self, PyObject *args)
{
    void *ptr_a, *ptr_b;
    PyObject *cobj_a, *cobj_b;

    if ( ! PyArg_ParseTuple(args,"OO", &cobj_a, &cobj_b))
        return NULL;
    ptr_a = (void *)PyCObject_AsVoidPtr(cobj_a);
    ptr_b = (void *)PyCObject_AsVoidPtr(cobj_b);

    if(ptr_a == ptr_b)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyObject *py2shmobj_add_shmem_pages(PyObject *self, PyObject *args)
{
    int count;

    if ( ! PyArg_ParseTuple(args,"i", &count))
        return NULL;

    if(xx_add_pages(count) == NULL)
        return NULL;

    Py_RETURN_NONE;
}

//Debug functions
PyObject *py2shmobj_freecount(PyObject *self, PyObject *args)
{
    int count;

    if ( ! PyArg_ParseTuple(args,""))
        return NULL;
    count = xx_shfreecount();
    return Py_BuildValue("i",count);
}
    
PyObject *py2shmobj_print_freelist(PyObject *self, PyObject *args)
{
    if ( ! PyArg_ParseTuple(args,""))
        return NULL;
    xx_print_freelist();
    Py_RETURN_NONE;
}

static PyMethodDef py2shmobj_methods[] = {

    //Int Methods
    {"shmint_alloc",       py2shmint_alloc,       METH_VARARGS, NULL},
    {"shmint_set",         py2shmint_set,         METH_VARARGS, NULL},
    {"shmint_get",         py2shmint_get,         METH_VARARGS, NULL},

    //Double Methods
    {"shmdbl_alloc",       py2shmdbl_alloc,       METH_VARARGS, NULL},
    {"shmdbl_set",         py2shmdbl_set,         METH_VARARGS, NULL},
    {"shmdbl_get",         py2shmdbl_get,         METH_VARARGS, NULL},

    //String Methods
    {"shmstr_alloc",       py2shmstr_alloc,       METH_VARARGS, NULL},
    {"shmstr_set",         py2shmstr_set,         METH_VARARGS, NULL},
    {"shmstr_get",         py2shmstr_get,         METH_VARARGS, NULL},

    //Pointer Methods
    {"shmptr_alloc",       py2shmptr_alloc,       METH_VARARGS, NULL},
    {"shmptr_set",         py2shmptr_set,         METH_VARARGS, NULL},
    {"shmptr_get",         py2shmptr_get,         METH_VARARGS, NULL},

    //Dictionary Methods
    {"shmdict_init",       py2shmdict_init,       METH_VARARGS, NULL},
    {"shmdict_insert",     py2shmdict_insert,     METH_VARARGS, NULL},
    {"shmdict_first",      py2shmdict_first,      METH_VARARGS, NULL},
    {"shmdict_next",       py2shmdict_next,       METH_VARARGS, NULL},
    {"shmdict_lookup",     py2shmdict_lookup,     METH_VARARGS, NULL},
    {"shmdict_remove",     py2shmdict_remove,     METH_VARARGS, NULL},
    {"shmdict_count",      py2shmdict_count,      METH_VARARGS, NULL},

    //Dict Node Methods
    {"shmdnode_alloc",     py2shmdnode_alloc,     METH_VARARGS, NULL},
    {"shmdnode_init",      py2shmdnode_init,      METH_VARARGS, NULL},
    {"shmdnode_get",       py2shmdnode_get,       METH_VARARGS, NULL},
    {"shmdnode_put",       py2shmdnode_put,       METH_VARARGS, NULL},
    {"shmdnode_getkey",    py2shmdnode_getkey,    METH_VARARGS, NULL},

    //List Methods
    {"shmlist_init",       py2shmlist_init,       METH_VARARGS, NULL},
    {"shmlist_append",     py2shmlist_append,     METH_VARARGS, NULL},
    {"shmlist_insert",     py2shmlist_insert,     METH_VARARGS, NULL},
    {"shmlist_remove",     py2shmlist_remove,     METH_VARARGS, NULL},
    {"shmlist_first",      py2shmlist_first,      METH_VARARGS, NULL},
    {"shmlist_last",       py2shmlist_last,       METH_VARARGS, NULL},
    {"shmlist_next",       py2shmlist_next,       METH_VARARGS, NULL},
    {"shmlist_prev",       py2shmlist_prev,       METH_VARARGS, NULL},
    {"shmlist_getnode",    py2shmlist_getnode,    METH_VARARGS, NULL},
    {"shmlist_count",      py2shmlist_count,      METH_VARARGS, NULL},

    //List Node Methods
    {"shmlnode_alloc",     py2shmlnode_alloc,     METH_VARARGS, NULL},
    {"shmlnode_init",      py2shmlnode_init,      METH_VARARGS, NULL},
    {"shmlnode_get",       py2shmlnode_get,       METH_VARARGS, NULL},
    {"shmlnode_put",       py2shmlnode_put,       METH_VARARGS, NULL},

    //Semaphore Methods
    {"shmsem_open",        py2shmsem_open,        METH_VARARGS, NULL},
    {"shmsem_wait",        py2shmsem_wait,        METH_VARARGS, NULL},
    {"shmsem_post",        py2shmsem_post,        METH_VARARGS, NULL},
    {"shmsem_close",       py2shmsem_close,       METH_VARARGS, NULL},
    {"shmsem_unlink",      py2shmsem_unlink,      METH_VARARGS, NULL},

    //Other methods
    {"shmobj_del",         py2shmobj_del,         METH_VARARGS, NULL},
    {"shmobj_cleanup",     py2shmobj_cleanup,     METH_VARARGS, NULL},
    {"shmobj_equals",      py2shmobj_equals,      METH_VARARGS, NULL},
    {"shmobj_freecount",   py2shmobj_freecount,   METH_VARARGS, NULL},
    {"shmobj_print_freelist", py2shmobj_print_freelist,  METH_VARARGS, NULL},
    {"shmobj_add_shmem_pages",py2shmobj_add_shmem_pages, METH_VARARGS, NULL},

    {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC
initpy2shmobj(void)
{
    void *shmem;

    PYSHMOBJ_PAGESIZE = getpagesize();
    Py_InitModule("py2shmobj", py2shmobj_methods);
    shmem = xx_add_pages(PYSHMOBJ_INIT_SHMEM_PAGES);
}
