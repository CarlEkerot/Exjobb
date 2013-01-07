
def to_bin(s):
    line = ""
    for i in range(0, len(s), 2):
        if i % 8 == 0:
            print line
            line = ""
        byte = s[i] + s[i+1]
        binstr = bin(int(byte, 16))[2:]
        line += '%08d ' % int(binstr)
