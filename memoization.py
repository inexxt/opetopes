# memoization helpers
import functools

from collections import Iterable

MEMO = {}

def convert_to_tuple(param):
    if not isinstance(param, Iterable) or isinstance(param, str):
        return param
    return tuple(convert_to_tuple(a) for a in param)

def clear_cache():
    MEMO.clear()

def memoize(f):
    memo = MEMO

    @functools.wraps(f)
    def helper(*args, **kwargs):
        item = (convert_to_tuple(args), tuple((convert_to_tuple(k), convert_to_tuple(kwargs[k])) for k in sorted(kwargs.keys())))
        if item not in memo:
            result = f(*args, **kwargs)
            memo[item] = result
        else:
            # print("Used memoization")
            pass
        return memo[item]

    return helper
