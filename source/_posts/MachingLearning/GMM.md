---
layout: post
title: GMM模型原理与实践
date: 
category: 机器学习
tags:
- generative
- model
- maths
- tools
- machinelearning
keywords:
description:
---


## 模型
我们假设这篇文章的读者对于EM算法有着一定了解。

### 原理
在之前的文章[EM算法原理与推导](https://protao.github.io/2018/05/27/MachingLearning-2018-05-27-EMAlgorithm/)中我们提到：
> 假设我们有数据集\\(X=\{x_{(1)},x_{(2)},...,x_{(m)}\}\\)，我们想利用生成式模型建模\\(P(x;\theta)\\)。...... 认为数据来自于多个分布，只不过我们无法观测到数据被哪一个子分布生成，因此不能直接利用公式直接计算解析解。EM算法就是用来处理这种具有“隐标签”的问题的。

同样，在PRML一书第九章第一句话也给出了提纲挈领的表述：
> 如果我们定义观测变量和潜在变量的一个**联合概率分布**，那么对应的观测变量本身的**概率分布**可以通过求**边缘概率**的方法得到。这使得观测变量上的复杂的边缘概率分布可以通过观测变量与潜在变量组成的**扩展空间**上的更加便于计算的联合概率分布来表示。因此，潜在变量的引入使得复杂的概率分布可以由简单的分量组成。

高斯混合模型就是这种情况的特例。我们以比较简单的语言整理一下这两段话。（不要在意把我自己的文章中的话和机器学习圣经中的话放到一起这件事...）
关键是弄明白这三个粗体的“概率”的意思，我们是在为无标签数据建立无监督的生成式模型\\(P(x;\theta)\\)。在这里，所谓模型，就是概率。$$$ P(x;\theta)=\sum_zP(x^{(i)},z^{(i)};\theta) $$$，就是指“观测变量本身的**概率分布**可以通过求**边缘概率**的方法得到。”，用模型的方式说就是混合模型的就是多个模型的累加和。而边缘概率又是对联合概率中某一随机变量的求和，之所以“定义观测变量和潜在变量的一个**联合概率分布**”，是因为联合概率分布就是子模型，而子模型好求。而单个父模型扩展成多个子模型的原因是，我们增加了一个变量，这个变量是隐变量，从而人为增加了一个变量维度。

<!-- more -->

### 推导

子模型（联合分布）是高斯分布：
$$ P(X, Y=i)=P(X|Y=i)*P(Y=i) $$
$$=\frac{1}{(2\pi)^{n/2}|\Sigma_i|^{1/2}}exp\Big(-\frac{1}{2}(x-\mu_i)^T\Sigma_i^{-1}(x-\mu_i)\Big)*\phi_i $$

总模型（边缘分布）是子模型在隐变量上的累加：
$$ P(X)=\sum_iP(X, Y=i) $$


既然我们增加了隐变量，极大似然就不能直接用了，然后就能套到EM算法中了。
$$ l(\theta)=\sum_{i=1}^mlogP(x^{(i)};\theta)\qquad$$
$$ l(\theta)=\sum_{i=1}^mlog\sum_zP(x^{(i)},z^{(i)};\theta)\quad$$

根据之前EM算法中进行到最后的推导，E步需要求隐标签的后验分布，这个是好求的。我们已知\\(P(X|y)\\)的正态分布计算方式，那么通过贝叶斯公式就可以求得反向的条件概率。



## sklearn实践
sklearn.mixture中实现了GMM和变分贝叶斯GMM。主要实践一下GMM，下面是从sklearn官方示例演变的example。详见参考内容1。
```python
import matplotlib  as mpl
from matplotlib import  pyplot as plt
import numpy as np
from sklearn.datasets import make_classification
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import StratifiedKFold

colors = ['navy', 'turquoise', 'darkorange']


def make_ellipses(gmm, ax):
    for n, color in enumerate(colors):
        if gmm.covariance_type == 'full':
            covariances = gmm.covariances_[n][:2, :2]
        elif gmm.covariance_type == 'tied':
            covariances = gmm.covariances_[:2, :2]
        elif gmm.covariance_type == 'diag':
            covariances = np.diag(gmm.covariances_[n][:2])
        elif gmm.covariance_type == 'spherical':
            covariances = np.eye(gmm.means_.shape[1]) * gmm.covariances_[n]
        v, w = np.linalg.eigh(covariances)
        u = w[0] / np.linalg.norm(w[0])
        angle = np.arctan2(u[1], u[0])
        angle = 180 * angle / np.pi  # convert to degrees
        v = 2. * np.sqrt(2.) * np.sqrt(v)
        ell = mpl.patches.Ellipse(gmm.means_[n, :2], v[0], v[1],
                                  180 + angle, color=color)
        ell.set_clip_box(ax.bbox)
        ell.set_alpha(0.5)
        ax.add_artist(ell)

X, y = make_classification(n_samples=600, n_features=2, n_redundant=0, n_informative=2, n_classes=3, n_clusters_per_class=1, random_state=15, flip_y=0)


# Break up the dataset into non-overlapping training (75%) and testing
# (25%) sets.
skf = StratifiedKFold(n_splits=5)
# Only take the first fold.
train_index, test_index = next(iter(skf.split(X, y)))
X_train = X[train_index]
y_train = y[train_index]
X_test = X[test_index]
y_test = y[test_index]

def show_raw_data():
	# 以散点图的形式展示原始数据
    plt.scatter(X_train[:, 0], X_train[:, 1], marker='.', c=y_train, s=10)
    plt.scatter(X_test[:, 0], X_test[:, 1], marker='o', c=y_test, s=25)
    plt.show()

# show_raw_data()

# 注意这个n_classes也是把GMM当做监督学习来用，通过标签确定组分个数
# 然而作为非监督学习的GMM，这个参数的确定才是困难
n_classes=len(np.unique(y))
estimators = dict((cov_type, GaussianMixture(n_components=n_classes, covariance_type=cov_type, max_iter=20, random_state=0)) for cov_type in ['spherical', 'diag', 'tied', 'full'])
n_estimators = len(estimators)

# 初始化画布
plt.figure(figsize=(3 * n_estimators // 2, 6))
plt.subplots_adjust(bottom=.01, top=0.95, hspace=.15, wspace=.05, left=.01, right=.99)

# 模型训练
for index, (name, estimator) in enumerate(estimators.items()):
    # Since we have class labels for the training data, we can
    # initialize the GMM parameters in a supervised manner.

    # 这里是关键！将无监督算法当做有监督算法的话，用带标签数据去初始化参数
    # 如果把这个去掉，不要改变生成的数据（包括n_sample）和gmm模型的初始化（主要是random_state， 会发现结果完全改变，原因想一下就能明白）
    estimator.means_init = np.array([X_train[y_train == i].mean(axis=0) for i in range(n_classes)])

    # Train the other parameters using the EM algorithm.
    estimator.fit(X_train)

    h = plt.subplot(2, n_estimators // 2, index + 1)
    make_ellipses(estimator, h)

    for n, color in enumerate(colors):
        data = X_train[y_train == n]
        plt.scatter(data[:, 0], data[:, 1], s=0.8, color=color)

    # Plot the test data with crosses
    for n, color in enumerate(colors):
        data = X_test[y_test == n]
        plt.scatter(data[:, 0], data[:, 1], marker='x', color=color)

    y_train_pred = estimator.predict(X_train)
    train_accuracy = np.mean(y_train_pred.ravel() == y_train.ravel()) * 100
    plt.text(0.05, 0.9, 'Train accuracy: %.1f' % train_accuracy,
             transform=h.transAxes)

    y_test_pred = estimator.predict(X_test)
    test_accuracy = np.mean(y_test_pred.ravel() == y_test.ravel()) * 100
    plt.text(0.05, 0.8, 'Test accuracy: %.1f' % test_accuracy,
             transform=h.transAxes)

    plt.xticks(())
    plt.yticks(())
    plt.title(name)

# 展示画布
plt.legend(scatterpoints=1, loc='lower right', prop=dict(size=12))
plt.show()

def show_predict_area():
    x_grid = np.linspace(-5,5,101)
    y_grid = np.linspace(-5,5,101)
    x_grid, y_grid = np.meshgrid(x_grid, y_grid)
    pred_area = estimators['full'].predict(tuple(zip(x_grid.flatten(),y_grid.flatten())))

    plt.scatter(x_grid.flatten(), y_grid.flatten(), c=tuple(map(lambda x:colors[x], pred_area)), alpha=0.04)
    plt.scatter(X_train[:, 0], X_train[:, 1], marker='.', c=tuple(map(lambda x:colors[x], y_train)), s=10)
    plt.scatter(X_test[:, 0], X_test[:, 1], marker='o', c=tuple(map(lambda x:colors[x], y_test)), s=25)
    plt.show()

# show_predict_area()


```


参考：
1. [sklearn 文档：GMM covariances](http://sklearn.apachecn.org/cn/0.19.0/auto_examples/mixture/plot_gmm_covariances.html#sphx-glr-auto-examples-mixture-plot-gmm-covariances-py)
