
import os
from cytoolz.curried import curry

class Micros(object):
    # TODO: see if these are any faster than simply calling the functions
    # directly.
    r = curry(os.read)
    w = curry(os.write)
    r0 = r(0)
    w1 = w(1)
    w2 = w(2)

