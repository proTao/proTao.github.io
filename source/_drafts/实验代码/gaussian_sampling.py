from random import random, gauss
from math import log, sqrt, cos, sin, pi
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np


def BoxMuller(mu=0, sigma=1, iter=1000):
    rand1 = np.random.random(size=(iter,))
    rand2 = np.random.random(size=(iter,))
    x = np.sqrt(-2*np.log(rand1)) * np.sin(2*np.pi*rand2)
    # y = np.sqrt(-2*np.log(rand1)) * np.sin(2*np.pi*rand2)
    return x

def _reject_unit_round(iter=1000):
    count = 0
    x_samples = [None] * iter
    y_samples = [None] * iter
    r_samples = [None] * iter
    
    while count < iter:
        flag = True
        while flag:
            x = random()*2-1
            y = random()*2-1
            r = x ** 2 + y ** 2
            if 0 < r <= 1:
                flag = False
                x_samples[count] = x
                y_samples[count] = y
                r_samples[count] = r
        count += 1
    return np.array(x_samples), np.array(y_samples), np.array(r_samples)

def MarsagliaPolar(mu=0,  sigma=1, iter=1000):
    x, y, r = _reject_unit_round(iter)
    return x * np.sqrt(-2 * np.log(r) / r)



if __name__ == "__main__":
    # sns.distplot([BoxMuller() for i in range(5000)])
    # sns.distplot([gauss(0,1) for i in range(5000)])
    sns.distplot(MarsagliaPolar(iter=5000))
    plt.show()
