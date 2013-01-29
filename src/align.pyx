from libc.stdlib cimport malloc
from calign cimport align_t
from calign cimport align as calign_

cpdef align(a, b, d, S, local=False):
    cdef size_t len_a = len(a)
    cdef size_t len_b = len(b)
    cdef size_t i
    cdef short* ca = <short*> malloc(len_a * sizeof(short))
    cdef short* cb = <short*> malloc(len_b * sizeof(short))
    cdef align_t al

    for i in range(len_a):
        ca[i] = ord(a[i])
    for i in range(len_b):
        cb[i] = ord(b[i])
    al = calign_(len_a, ca, len_b, cb, d, S, local)

    a1 = []
    a2 = []
    for i in range(al.len):
        a1i = al.a1[i]
        a2i = al.a2[i]
        if a1i != -1:
            a1.append(a1i)
        else:
            a1.append(None)
        if a2i != -1:
            a2.append(a2i)
        else:
            a2.append(None)

    return (al.s, a1, a2)

