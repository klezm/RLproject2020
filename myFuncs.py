from functools import cache
import numpy as np


@cache
def cached_power(base, exponent):
    return np.power(base, exponent)
