#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include "cupgma.h"
#include "list.h"

#ifndef min
#define min(a, b) ((a) < (b) ? (a) : (b))
#endif

#ifndef sq
#define sq(a) ((a) * (a))
#endif

static list_t* get_leaves(node_t* node)
{
    list_t* leaves;
    list_t* tmp;

    if (node->type == PARENT) {
        leaves = get_leaves(node->u.parent.left);
        tmp = get_leaves(node->u.parent.right);
        append_list(leaves, tmp);
        free(tmp);
    } else {
        leaves = new_list(node);
    }

    return leaves;
}

static short compare(node_t* n1, node_t* n2)
{
    list_t* a;
    list_t* b;
    list_node_t* i;
    list_node_t* j;
    feature_t* f_i;
    feature_t* f_j;
    size_t min_len;
    size_t k;
    size_t cnt;
    float dist = 0;
    float sum;

    a = get_leaves(n1);
    b = get_leaves(n2);

    for (i = a->head; i != NULL; i = i->next) {
        for (j = b->head; j != NULL; j = j->next) {
            f_i = ((node_t*) i->data)->u.leaf.features;
            f_j = ((node_t*) j->data)->u.leaf.features;
            min_len = min(f_i->size, f_j->size);

            sum = 0;
            for (k = 0; k < min_len; k++) {
                sum += sq(f_i->data[k] - f_j->data[k]);
            }
            dist += sqrt(sum);
            cnt++;
        }
    }
    dist /= cnt;

    free_list(&a);
    free_list(&b);

    return dist;
}

node_t* upgma(size_t len_features, float** features)
{
    list_t* worklist;
    size_t i;

    for (i = 0; i < len_features; i++) {
        worklist
    }

    for (i, msg) in enumerate(msgs):
        features = numpy.asarray(map(lambda (j, x): ord(x) / len(entropy[j]), enumerate(msg)))
        to_process.append(LeafNode(i, features))

    while len(to_process) > 1:
        score_min = float('inf')
        for (A, B) in itertools.combinations(to_process, 2):
            score = A.compare_to(B)
            if score < score_min:
                to_merge = (A, B)
                score_min = score
        (A, B) = to_merge
        to_process.remove(A)
        to_process.remove(B)
        to_process.append(ParentNode(A, B, score_min))

    return to_process[0]
}

