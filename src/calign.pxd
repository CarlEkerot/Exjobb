from libcpp cimport bool

cdef extern from 'align.h':
    cdef struct align_t:
        int s
        size_t len
        short* a1
        short* a2

    align_t align(size_t len_a, short* a, size_t len_b, short* b, int d, object S, bool local)

