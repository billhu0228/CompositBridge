import numpy as np


def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)


def sin2(x):
    s = 0
    for n in range(4):
        s += (-1) ** n / factorial(2 * n + 1) * x ** (2 * n + 1)
    return s


for deg in range(91):
    rad = deg / 180.0 * np.pi
    print("%i,%.3f,%.3f" % (deg, np.sin(rad), sin2(rad)))
