from random import random
from bisect import bisect_left
from itertools import accumulate

def roulette_sampling(p:dict, n):
    # 轮盘赌
    assert type(p) is dict
    samples = [None] * n
    keys = list(p.keys())
    values = p.values()
    cdf = list(accumulate(values))
    for i in range(n):
        random_p = random()
        index = bisect_left(cdf, random_p)
        samples[i] = keys[index]
    return samples

from collections import Counter
test_p = {'a':0.1, 'b':0.3, 'c':0.6}
print(Counter(roulette_sampling(test_p, 10000)))