import numpy
from functools import lru_cache
import pytail


@lru_cache
def file2hist(file):
    with open(file, "r") as f:
        lines = f.readlines()
        x = numpy.array([float(line) for line in lines])
    return hist(x)


def compare(ha, hb):
    prod = numpy.multiply(ha, hb)
    sqrt = numpy.sqrt(prod)
    sum = numpy.sum(sqrt)

    return sum


def hist(x):
    h = numpy.histogram(x, bins=200, range=(0, 2000))[0]
    h = h / numpy.sum(h)
    return h


def tail(filename, n=10):
    with open(filename, "rb") as f:
        return pytail.tail(f, n)


def stream2hist():
    lines = tail("data/current.txt", 60)
    # grab second token in each line (first is timestamp)
    x = numpy.transpose(numpy.array([float(line.split()[1]) for line in lines]))

    hs = hist(x)
    return hs


def getstatus():
    hs = stream2hist()
    # print(numpy.argmax(hs))
    w_s = compare(file2hist("data/wash"), hs)
    d_s = compare(file2hist("data/dry"), hs)
    b_s = compare(file2hist("data/both"), hs)

    m = numpy.argmax(numpy.array([w_s, d_s, b_s]))

    if numpy.argmax(hs) < 3:
        m = -1

    return m


if __name__ == "__main__":
    m = getstatus()
    print(m)
