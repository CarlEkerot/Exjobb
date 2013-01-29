#include <stdlib.h>
#include <stdbool.h>

typedef struct align_t {
    int s;
    size_t len;
    short* a1;
    short* a2;
} align_t;

align_t align(const char* a, const char* b, int d, int (*S)(char, char), bool local);
