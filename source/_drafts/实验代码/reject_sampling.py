import numpy as np
import scipy.stats as st
import seaborn as sns
import matplotlib.pyplot as plt


sns.set()


def p(x):
    return (st.norm.pdf(x, loc=30, scale=10) + st.norm.pdf(x, loc=80, scale=20)) / 2


def q(x):
    return st.norm.pdf(x, loc=50, scale=30)





def rejection_sampling(p, q, xs, iter=1000, draw=False):
    samples = []
    k = max(p(xs) / q(xs))
    if draw:
        plt.plot(xs, p(xs))
        plt.plot(xs, k*q(xs))
        # plt.show()

    for _ in range(iter):
        z = np.random.normal(50, 30)
        u = np.random.uniform(0, k*q(z))

        if u <= p(z):
            samples.append(z)

    return np.array(samples)


if __name__ == '__main__':
    xs = np.arange(-50, 151)
    s = rejection_sampling(p, q, xs, iter=10000, draw=True)
    sns.distplot(s, norm_hist=True)
    plt.show()
