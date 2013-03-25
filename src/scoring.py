import string
import numpy as np

# Create a scoring matrix
# Rewards:
# * identical byte values (2)
# * values that lies within the ASCII range (2 or 1)
# * numeric values close to each other (1 or 0)
# Ignores:
# * existing gaps (0)
# Discourages:
# * everything else (-1)
alphanum = map(ord, string.printable)[:62]
non_alphanum = map(ord, string.printable)[62:]
S = -1 * np.ones((257, 257))
for i in range(256):
    for j in range(256):
        diff = abs(i - j)
        if diff <= 10:
            s = 1
        elif diff <= 20:
            s = 0
        else:
            continue
        S[i,j] = s
for i in alphanum:
    for j in alphanum:
        S[i,j] = 2
for i in non_alphanum:
    for j in non_alphanum:
        S[i,j] = 1
for i in range(256):
    S[i,i] = 2
S[256,:] = np.zeros(257)
S[:,256] = np.zeros(257)
S = S.astype(np.int16)

