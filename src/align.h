#include <stdbool.h>

typedef struct align_t {
    short* a1;
    short* a2;
    int s;
} align_t;

align_t align(const char* a, const char* b, int d, int (*S)(char, char), bool local);
