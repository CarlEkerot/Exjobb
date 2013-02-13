#ifndef CUPGMA_H
#define CUPGMA_H

typedef enum node_type_t {
    PARENT,
    LEAF,
} node_type_t;

typedef struct feature_t {
    float* data;
    size_t size;
} feature_t;

typedef struct node_t node_t;

struct node_t {
    node_type_t type;
    union {
        struct {
            node_t* left;
            node_t* right;
            short score;
        } parent;
        struct {
            size_t index;
            feature_t* features;
        } leaf;
    } u;
};

node_t* upgma();

#endif

