import os
import sys
def tail(f, n=1, bsize=4098):
    """Tail a file and get X lines from the end"""
    # place holder for the lines found
    lines = []
    offset = -bsize

    # loop until we find n lines
    while len(lines) < n:
        try:
            f.seek(offset, os.SEEK_END)
        except IOError:  # either file is too small, or too many lines requested
            f.seek(0)
            lines = f.readlines()
            break

        lines = f.readlines()
        offset -= bsize

    return lines[-n:]

if __name__ == "__main__":

    with open(sys.argv[1],'rb') as f:
        lines = tail(f,10)
        print(lines)

