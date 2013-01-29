#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "align.h"

#ifndef max
#define max(a, b) ((a) > (b) ? (a) : (b))
#endif

/**

Performs local or global sequence alignment.

Parameters
----------
a       - first sequence
b       - second sequence
d       - gap penalty
S       - scoring function on the form S(char, char) -> int
local   - True for local alignment, False otherwise

Returns
-------
a1      - alignment of the first sequence
a2      - alignment of the second sequence
s       - alignment score

*/
align_t align(const char* a, const char* b, int d, int (*S)(char, char), bool local)
{
    size_t len_a = strlen(a);
    size_t len_b = strlen(b);
    size_t len_al;
    size_t i;
    size_t j;
    size_t max_i = 0;
    size_t max_j = 0;
    size_t cnt1 = 0;
    size_t cnt2 = 0;
    int match;
    int delete;
    int insert;
    int max_val = 0;
    int F[len_b + 1][len_a + 1];
    short tmp;
    short* a1;
    short* a2;
    align_t ret;

    // Initialize the matrix
    if (!local) {
        for (i = 0; i < len_a + 1; i++) {
            F[0][i] = d * i;
        }
        for (i = 0; i < len_b + 1; i++) {
            F[i][0] = d * i;
        }
    } else {
        for (i = 0; i < len_a + 1; i++) {
            F[0][i] = 0;
        }
        for (i = 0; i < len_b + 1; i++) {
            F[i][0] = 0;
        }
    }

    // Fill the matrix
    for (i = 1; i < len_b + 1; i++) {
        for (j = 1; j < len_a + 1; j++) {
            match = F[i-1][j-1] + S(a[j-1], b[i-1]);
            delete = F[i-1][j] + d;
            insert = F[i][j-1] + d;
            F[i][j] = max(match, delete);
            F[i][j] = max(F[i][j], insert);
            if (local) {
                F[i][j] = max(F[i][j], 0);
            }
            if (F[i][j] > max_val) {
                max_val = F[i][j];
                max_i = i;
                max_j = j;
            }
        }
    }

    // Backtrace through the matrix
    a1 = malloc((len_a + len_b) * sizeof(char));
    a2 = malloc((len_a + len_b) * sizeof(char));
    if (local) {
        i = max_i;
        j = max_j;
    } else {
        i = len_b;
        j = len_a;
    }
    while (i > 0 || j > 0) {
        if (local && !F[i][j]) {
            break;
        }
        if (i > 0 && j > 0 && F[i][j] == F[i-1][j-1] + S(a[j-1], b[i-1])) {
            a1[cnt1++] = a[j-1];
            a2[cnt2++] = b[i-1];
            i--;
            j--;
        } else if (i > 0 && F[i][j] == F[i-1][j] + d) {
            a1[cnt1++] = -1;
            a2[cnt2++] = b[i-1];
            i--;
        } else {
            a1[cnt1++] = a[j-1];
            a2[cnt2++] = -1;
            j--;
        }
    }

    // Reverse the alignments
    len_al = cnt1;
    for (i = 0; i <= len_al / 2; i++) {
        tmp = a1[i];
        a1[i] = a1[len_al - (i + 1)];
        a1[len_al - (i + 1)] = tmp;
        tmp = a2[i];
        a2[i] = a2[len_al - (i + 1)];
        a2[len_al - (i + 1)] = tmp;
    }

    ret.a1 = a1;
    ret.a2 = a2;
    ret.s = max_val;
    return ret;
}

int S(char a, char b) {
    if (a == b)
        return 2;
    return -1;
}

int main() {
    int i;

    for (i = 0; i < 100000; i++) {
        align_t al = align("ACACACTAATCGCGTACGATCGATCTCTAGCTAGC", "AGCACACATCGATCGATCTCTCGATCGATCGATCGATCGAT", -2, *S, true);
    }
    /*
    align_t al = align("ACACACTA", "AGCACACA", -2, *S, true);
    for (i = 0; i < 9; i++) {
        printf("%d ", al.a1[i]);
    }
    printf("\n");
    for (i = 0; i < 9; i++) {
        printf("%d ", al.a2[i]);
    }
    printf("\n");
    printf("%d\n", al.s);
    */
    return 0;
}
