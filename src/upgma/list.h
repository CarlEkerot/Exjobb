#ifndef LIST_H
#define LIST_H

typedef struct list_node_t list_node_t;

struct list_node_t {
    list_node_t* next;
    void* data;
};

struct list_t {
    list_node_t* head;
    list_node_t* tail;
} list_t;

list_t* new_list(void* data);
void free_list(list_t** list);
void list_insert(list_t* list, void* data);
void list_remove(list_t* list, list_node_t* node);
void append_list(list_t* l1, list_t* l2);

#endif

