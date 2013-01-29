import numpy

def align(a, b, d, S, local=False):
    """
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
    """
    F = numpy.ndarray((len(b) + 1, len(a) + 1), dtype=int)
    if local:
        F[0,:] = [0 for i in range(len(a) + 1)]
        F[:,0] = [0 for i in range(len(b) + 1)]
    else:
        F[0,:] = [d * i for i in range(len(a) + 1)]
        F[:,0] = [d * i for i in range(len(b) + 1)]

    max_val = 0
    max_i = 0
    max_j = 0
    for i in range(1, len(b) + 1):
        for j in range(1, len(a) + 1):
            match = F[i-1,j-1] + S(a[j-1], b[i-1])
            delete = F[i-1,j] + d
            insert = F[i,j-1] + d
            mdiz = [match, delete, insert]
            if local:
                mdiz.append(0)
            F[i,j] = max(mdiz)
            if F[i,j] > max_val:
                max_val = F[i,j]
                max_i = i
                max_j = j

    a1 = []
    a2 = []
    if local:
        i = max_i
        j = max_j
    else:
        i = len(b)
        j = len(a)
    while i > 0 or j > 0:
        if local and F[i,j] == 0:
            break
        if i > 0 and j > 0 and F[i,j] == F[i-1,j-1] + S(a[j-1], b[i-1]):
            a1.append(a[j-1])
            a2.append(b[i-1])
            i -= 1
            j -= 1
        elif i > 0 and F[i,j] == F[i-1,j] + d:
            a1.append(None)
            a2.append(b[i-1])
            i -= 1
        else:
            a1.append(a[j-1])
            a2.append(None)
            j -= 1

    a1.reverse()
    a2.reverse()
    return (a1, a2, max_val)

