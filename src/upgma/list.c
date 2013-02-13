#include <stdlib.h>
#include "list.h"

list_t* new_list(void* data)
{
    list_t*         list;
    list_node_t*    head;

    list = malloc(sizeof(list_t));
    head = malloc(sizeof(list_node_t));
    if (list == NULL || head == NULL) {
        exit(1);
    }

    head->next = NULL;
    head->data = data;

    list->head = head;
    list->tail = head;

    return list;
}

void free_list(list_t** list)
{
    list_node_t* node;
    list_node_t* tmp;

    if (*list == NULL) {
        return;
    }

    node = (*list)->head;
    while (node != NULL) {
        tmp = node;
        node = node->next;
        free(tmp);
    }

    free(*list);

    *list = NULL;
}

void list_insert(list_t* list, void* data)
{
    list_node_t* node;

    node = malloc(sizeof(list_node_t));
    if (node == NULL) {
        exit(1);
    }

    list->tail->next = node;
    list->tail = node;
}

void list_remove(list_t* list, list_node_t* node)
{
    list_node_t* pred;
    list_node_t* curr;

    curr = list->head;
    while (curr != NULL && curr != node) {
        pred = curr;
        curr = curr->next;
    }

    if (curr != NULL) {
        pred->next = curr->next;
        free(curr);
    }
}

void append_list(list_t* l1, list_t* l2)
{
    l1->tail->next = l2->head;
    l1->tail = l2->tail;
}

