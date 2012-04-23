#include "list.h"

list_t *list_init(list_t *list)
{
    list->termnode.next = &list->termnode;
    list->termnode.prev = &list->termnode;
    list->count = 0;
    return list;
}

void list_insert_after(list_t *list, list_node_t *n, list_node_t *after)
{
    n->prev = after;
    n->next = after->next;
    after->next->prev = n;
    after->next = n;
    list->count++;
}

void list_insert_before(list_t *list, list_node_t *n, list_node_t *before)
{
    list_insert_after(list, n, before->prev);
}

list_node_t *list_remove(list_t *list, list_node_t *n)
{
    n->prev->next = n->next;
    n->next->prev = n->prev;
    n->next = NULL;
    n->prev = NULL;
    list->count--;
    return n;
}

list_node_t *list_node_init(list_node_t *n, void *data, int type, size_t size)
{
    n->next = NULL;
    n->prev = NULL;
    list_node_fill(n, data, type, size);
    return n;
}

void list_append(list_t *list, list_node_t *node)
{
    //Last item is before terminating node.
    list_insert_before(list, node, &list->termnode);
}

void list_prepend(list_t *list, list_node_t *node)
{
    //First item is after terminating node.
    list_insert_after(list, node, &list->termnode);
}

list_node_t *list_first(list_t *list)
{
    return list_next(list, &(list->termnode));
}

list_node_t *list_last(list_t *list)
{
    return list_prev(list, &(list->termnode));
}

int list_count(list_t *list)
{
    return list->count;
}

void list_node_fill(list_node_t *n, void *data, int type, size_t size)
{
    n->data = data;
    n->data_type = type;
    n->data_sz  = size;
}

void *list_node_data(list_node_t *n, int *type, int *size)
{
    *type = n->data_type;
    *size = n->data_sz;
    return n->data;
}

list_node_t *list_next(list_t *list, list_node_t *n)
{
    return list_node_client_val(list, n->next);
}

list_node_t *list_prev(list_t *list, list_node_t *n)
{
    return list_node_client_val(list, n->prev);
}

list_node_t* list_get_node(list_t* list, int index)
{
    int i;
    list_node_t* n;

    if(list_count(list) < index)
        return NULL;

    n = list_first(list);
    for (i = 0; i < index; i++){
        n = n->next;
    }

    return list_node_client_val(list, n);
}
                    
list_node_t* list_node_client_val(list_t *list, list_node_t *n)
{
    if (n != &(list->termnode))
        return n;
    else
        return NULL;
}
