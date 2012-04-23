#include <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct list_node_t {
    struct list_node_t *next;
    struct list_node_t *prev;
    void *data;
    size_t data_sz;
    int data_type;
} list_node_t;

typedef struct list_t {
    list_node_t termnode;
    int count;
    int max_count;
} list_t;

list_node_t* list_node_init(list_node_t*, void*, int, size_t);
void list_node_fill(list_node_t*, void*, int, size_t);
void* list_node_data(list_node_t*, int*, int*);

list_t* list_init(list_t*);
int list_count(list_t*);
void list_append(list_t*, list_node_t*);
void list_prepend(list_t*, list_node_t*);
void list_insert_after(list_t*, list_node_t*, list_node_t*);
void list_insert_before(list_t*, list_node_t*, list_node_t*);
list_node_t* list_first(list_t*);
list_node_t* list_last(list_t*);
list_node_t* list_next(list_t*, list_node_t*);
list_node_t* list_prev(list_t*, list_node_t*);
list_node_t* list_remove(list_t*, list_node_t*);
list_node_t* list_get_node(list_t*, int);
list_node_t* list_node_client_val(list_t*, list_node_t*);

#ifdef __cplusplus
}
#endif
