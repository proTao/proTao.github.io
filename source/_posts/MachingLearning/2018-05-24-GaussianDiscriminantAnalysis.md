
---
layout: post
title: 高斯判别模型（GDA）原理与推导
date: 2018-05-24
category: 机器学习
tags: 
- model
- generative
- maths
- tools
- machinelearning
keywords: 
description: 
---

## GDA原理
Gaussian Discriminant Analysis模型的理论十分简单，这里写这篇文章实际上是为后面GMM和EM算法做铺垫。另外，这篇文章是第一篇加上generative标签的文章，指的是生成式模型，因此也会在这里重点说明一下生成式和判别式的区别。

## Generative 与 Discriminative
判别式模型对条件概率\\(P(Y|X)\\)建模，不关注数据分布，重点关注类间的分类超平面，SVM就是典型的判别式模型，在PGM中典型的就是CRF，这点特别容易弄错，尽管CRF是无向概率图模型，属于马尔科夫网络，对无向边给定联合概率分布，但是求解计算计算概率的时候通过除以归一化因子得到条件概率，这里先说这么多，后面会有文章详细总结。还有神经网络也是判别式，现在的神经网络就是利用强大的高维拟合能力得到分类面。而生成式模型则是对数据与标签的联合概率进行建模，然后来了新的数据之后，根据贝叶斯公式，利用类别先验概率和给定数据后的似然进行分类，典型的模型包括，NaiveBayes，HMM，还有这里介绍的GDA，以及后面介绍的GMM。

<!-- more -->

### GDA模型原理
原理其实很简单，认为每个类别来自于一个高斯分布\\(Gaussian(\mu, \Sigma)\\).
而不同的类别的先验概率是一个Multinoulli分布，在二分类任务就就是一个bernoulli分布，参数是\\(\phi\\)，前面已经提到，GDA是生成式模型，那么就是对联合概率\\(P(X,Y)\\)(在下面的推导的第二步中很明显的看出来)进行建模。
\\(P(X)=\sum_yP(X,Y=y)=P(X|Y=0)P(Y=0)+P(X|Y=1)P(Y=1)\\)，其中，\\(P(Y)=\phi^y(1-\phi)^{1-y}\\)， ** 即\\(\phi\\)是类别1的概率 **。

$$ P(X|Y=0)=\frac{1}{(2\pi)^{n/2}|\Sigma_0|^{1/2}}exp\Big(-\frac{1}{2}(x-\mu_0)^T\Sigma_0^{-1}(x-\mu_0)\Big) $$
$$ P(X|Y=1)=\frac{1}{(2\pi)^{n/2}|\Sigma_1|^{1/2}}exp\Big(-\frac{1}{2}(x-\mu_1)^T\Sigma_1^{-1}(x-\mu_1)\Big) $$
上面公式中，n是特征维数。把上面这两个条件概率整合到一起：
$$ P(X|Y)=P(X|Y=0)^{1-y}*P(X|Y=1)^y $$

因此对数似然为：

$$ l(\theta)=l(\phi,\mu_0,\mu_1,\Sigma_0,\Sigma_1) $$
$$ =log\prod_{i=1}^mP(x_i,y_i;\phi,\mu_0,\mu_1,\Sigma_0,\Sigma_1) $$
$$ =log\prod_{i=1}^mP(x_i|y_i;\phi,\mu_0,\mu_1,\Sigma_0,\Sigma_1)P(y_i;\phi) $$
$$ =\sum_{i=0}^m\Big[logP(x_i|y_i;\phi,\mu_0,\mu_1,\Sigma_0,\Sigma_1)+logP(y_i;\phi)\Big] $$
$$ =\sum_{i=0}^m\Big[(1-y^{(i)})logP(X|Y=0)+y^{(i)}logP(X|Y=1)+y^{(i)}log\phi+(1-y^{(i)})log(1-\phi)\Big] $$
其中累加和内部共有四项，其中给定类别标签的条件概率我没有展开，但是也可以轻易的看出来，\\(\mu_0\\)和\\(\Sigma_0\\)只与第一项有关，\\(\mu_1\\)和\\(\Sigma_1\\)只与第二项有关，先验概率\\(\phi\\)只与后两项有关。后面做GMM推导的时候就会发现，我们公式在这里，可以直接去进行极大似然的推导，因此实际上无需迭代，通过解析方法可以直接得到模型参数，下面就通过极大似然估计对模型参数进行估计。另外，在后面的推导中，a用表示1类的数据数，b表示0类的数据数，（在更正式的推导中使用的是指示函数）。

对于\\(\phi\\)，我们只关心后两项，直接从全参数的极大似然中去掉无关的前两项：
$$ l(\phi)=\sum_{i=0}^m[y^{(i)}log\phi+(1-y^{(i)})log(1-\phi)] $$
$$ l(\phi)=\sum_{class1}log\phi+\sum_{class0}log(1-\phi) $$
$$ l(\phi)=alog\phi+blog(1-\phi) $$
$$ \frac{\partial l(\phi)}{\partial\phi}=\frac{a}{\phi}+\frac{b}{1-\phi} $$
令上式等于0，可以解得\\(\hat{\phi}=\frac{a}{a+b}=\frac{a}{m}\\)，即1类在总样本中占得比例，从最大似然的思想考虑，这个结论应该是理所应当的。

对于\\(\mu_0\\)，我们只关心第一项，对于\\(\mu_1\\)，我们只关心第二项，这里只进行\\(\mu_0\\)的推导，\\(\mu_1\\)根据对称性同理易得。类似于上面的推导，我们在推导中只保留相关项即第一项，后三项忽略。
$$ l(\mu_0)=\sum_{i=0}^m(1-y^{(i)})logP(X|Y=0) $$
$$ l(\mu_0)=\sum_{i=0}^m(1-y^{(i)})log\bigg(\frac{1}{(2\pi)^{n/2}|\Sigma_0|^{1/2}}exp(-\frac{1}{2}(x-\mu_0)^T\Sigma_0^{-1}(x-\mu_0))\bigg) $$
$$ l(\mu_0)=\sum_{i=0}^m(1-y^{(i)})\Big(-\frac{1}{2}log\big((2\pi)^n|\Sigma_0|\big)-\frac{1}{2}(x-\mu_0)^T\Sigma_0^{-1}(x-\mu_0)\Big) $$
删除掉与\\(\mu_0$\\)无关的项，另外当y等于1的时候，累加项为0,，因此：
$$ l(\mu_0)=\sum_{class0}\Big(-\frac{1}{2}(x-\mu_0)^T\Sigma_0^{-1}(x-\mu_0)\Big) $$
$$ \frac{\partial l(\mu_0)}{\mu_0}=-\frac{1}{2}\sum_{class0}\Big(\frac{\partial}{\partial\mu_0}(x-\mu_0)^T\Sigma_0^{-1}(x-\mu_0)\Big) $$
$$ \frac{\partial l(\mu_0)}{\mu_0}=-\frac{1}{2}\sum_{class0}\Big(\Sigma_0^{-1}(x-\mu_0)\Big) $$
$$ \frac{\partial l(\mu_0)}{\mu_0}=-\frac{1}{2}\Sigma_0^{-1}\sum_{class0}\Big(x-\mu_0\Big) $$
令上式为0，解得\\(\hat\mu_0=\frac{\sum_{class0}x^{(i)}}{b}\\)，实际上就是所有0类样本的均值向量，其实就是把0类样本单拿出来，对其进行高斯建模，求解参数。

对于\\(\Sigma_0\\)，依然是拿掉无关项，进行极大似然推导。
$$ l(\Sigma_0)=\sum_{i=0}^m(1-y^{(i)})logP(X|Y=0) $$
$$ l(\Sigma_0)=\sum_{i=0}^m(1-y^{(i)})log\bigg(\frac{1}{(2\pi)^{n/2}|\Sigma_0|^{1/2}}exp(-\frac{1}{2}(x^{(i)}-\mu_0)^T\Sigma_0^{-1}(x^{(i)}-\mu_0))\bigg) $$
$$ l(\Sigma_0)=\sum_{i=0}^m(1-y^{(i)})\Big(-\frac{1}{2}log\big((2\pi)^n|\Sigma_0|\big)-\frac{1}{2}(x^{(i)}-\mu_0)^T\Sigma_0^{-1}(x^{(i)}-\mu_0)\Big) $$
$$ l(\Sigma_0)=-\frac{1}{2}\sum_{class0}\Big(nlog(2\pi)^n+log|\Sigma_0|+(x^{(i)}-\mu_0)^T\Sigma_0^{-1}(x^{(i)}-\mu_0)\Big) $$
$$ \frac{\partial l(\Sigma_0)}{\partial \Sigma_0}=-\frac{1}{2}\sum_{class0}\Big(\frac{\partial}{\partial \Sigma_0}log|\Sigma_0|+\frac{\partial}{\partial \Sigma_0}(x^{(i)}-\mu_0)^T\Sigma_0^{-1}(x^{(i)}-\mu_0)\Big)$$
依然令上式为零，不过这里后续的推到依然有些困难，上面\\(\mu_0\\)的推导过程中用到了矩阵求导，不过比较简单，我没有多提，这里用到了两处矩阵求导，需要提一下，分别是：
$$ \frac{\partial|\Sigma|}{\partial\Sigma}=|\Sigma|\Sigma^{-1} $$
$$ \frac{\partial\Sigma^{-1}}{\partial\Sigma}=-\Sigma^{-2} $$
继续导数为零的推导：
$$\frac{\partial l(\Sigma_0)}{\partial \Sigma_0}=-\frac{1}{2}\sum_{class0}\Big(\frac{\partial}{\partial \Sigma_0}log|\Sigma_0|+\frac{\partial}{\partial \Sigma_0}(x^{(i)}-\mu_0)^T\Sigma_0^{-1}(x^{(i)}-\mu_0)\Big)=0$$
$$ \sum_{class0}\Big(\frac{\partial}{\partial \Sigma_0}log|\Sigma_0|+\frac{\partial}{\partial \Sigma_0}(x^{(i)}-\mu_0)^T\Sigma_0^{-1}(x^{(i)}-\mu_0)\Big)=0 $$
$$ \sum_{class0}\Big(\frac{1}{|\Sigma_0|}|\Sigma_0|\Sigma_0^{-1}+(x^{(i)}-\mu_0)(x^{(i)}-\mu_0)^T(-\Sigma_0^{-2})\Big)=0 $$
$$ \sum_{class0}\Big(\Sigma_0-(x^{(i)}-\mu_0)(x^{(i)}-\mu_0)^T\Big)=0 $$
$$ \Sigma_0=\frac{1}{b}\sum_{class0}(x^{(i)}-\mu_0)(x^{(i)}-\mu_0)^T $$

推导到这里，可以看出来，实际上就是对0类样本求解样本协方差，结合我们的高斯分布假设，这一结论依然是顺理成章，结合前面的推导，其实和对高斯样本的参数估计对比，GDA运用于分类唯一的就是加入了类别的先验概率\\(\phi\\)的分析，因此实际上GDA是一种很简单的模型。

另外，在CS229中讲的GDA实际上多个不同的高斯分布是共享协方差矩阵的，如果做出这样的假设，对于数据的要求实际上就更少了，这样的话，对协方差的推导就会有一点点变化：
$$ \Sigma=\frac{1}{m}\sum_{i=0}^{m}(x^{(i)}-\mu_{y_i})(x^{(i)}-\mu_{y_i})^T $$

## 与LR分类器的区别
如果把\\(p(y=1|x)\\)看作是关于x的函数的话，那么可以表示为LogisticRegression的形式。假设\\(p(x|y)\\)是共享协方差矩阵的多个高斯分布的话，那么\\(p(y|x)\\)就是一个LR模型，但是反之不成立。也就是说GDA是LR的特例，如果具有更强的假设，因此如果数据符合GDA的假设，使用GDA模型是具有更高的渐进效率(asymptotically efficient)的，并且可以使用更少的数据。与之形成对比的是，LR分类器对数据做了更弱的假设，因此变得更加鲁棒且对于模型假设是否成立不那么敏感。



## 实践

```python
from functools import partial
import math
import numpy as np
from numpy import linalg
from scipy import stats
from matplotlib import pyplot as plt
from sklearn.datasets.samples_generator import make_blobs

# 超参数设定
n=2 # 两个特征即二维数据
class_num=5 # 几类数据(可以在2~6之间调节以观察实验结果)

X, y = make_blobs(n_samples=1000, centers=class_num, n_features=n,cluster_std=0.7)

color=['green', 'red', 'blue', 'yellow', 'black','yellow']
x_min = min(X[:,0])-1
x_max = max(X[:,0])+1
y_min = min(X[:,1])-1
y_max = max(X[:,1])+1
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)


# 数据初步可视化
plt.scatter(X[:,0],X[:,1],s=2,c=list(map(lambda x:color[x], y)))
#plt.show()

label_X = []
mu = []
sigma = []
def gaussian_pdf(x, mu, sigma):
    return (linalg.det(sigma)*(np.pi*2)**2)**(-0.5) * math.exp(-0.5*np.dot(np.dot((x-mu).reshape(1,2),linalg.inv(sigma)),(x-mu).reshape(2,1)))

for i in range(class_num):
    label_X.append(X[y==i])
    mu.append(sum(label_X[i])/len(label_X[i]))
    sigma.append(sum(np.dot(a.reshape((2,1)), a.reshape((1,2))) for a in label_X[i]-mu[i])/len(label_X[i]))

sample_num = 100
x = np.linspace(x_min, x_max, sample_num)
y = np.linspace(y_min, y_max, sample_num)
X,Y = np.meshgrid(x,y)

Z=[]
for i in range(class_num):
    Z.append(np.array(list(map(partial(gaussian_pdf, mu=mu[i], sigma=sigma[i]), list(zip(X.flatten(),Y.flatten()))))).reshape(X.shape))

#plt.scatter(X,Y,c=sum(Z), alpha=0.4, marker=".") #不好看
Z=np.dstack(Z)
plt.scatter(X,Y,c=Z.argmax(axis=2), alpha=0.1, marker=".");
plt.show()
```
注：
1. `make_blob`函数生成的分布具有相同的协方差。另外生成数据的函数有`make_classification`和`make_gaussian_quantiles`。前者特点是可以生成冗余的特征（和其他某几个特征线性相关）或者重复特征，可以生成脏数据（类别标记错误）等等，很强大。后者感觉和`make_blobs`差不多。
2. 生成散点图用scatter，我总是记成plot函数

```python
# 生成三维存在线性相关的数据
X, y = make_classification(n_samples=1000, n_features=3, n_informative=3, n_redundant=0, n_repeated=0, n_classes=2, n_clusters_per_class=1, weights=None, flip_y=0.01, class_sep=1.0, hypercube=True, shift=0.0, scale=1.0, shuffle=True, random_state=None)
fig=plt.figure()
ax = fig.add_subplot(1, 1, 1, projection='3d')
ax.scatter3D(X[:,0],X[:,1],X[:,2],c=y)
plt.show()
```

参考
1. [高斯判别分析实现与分析](https://www.cnblogs.com/jcchen1987/p/4424436.html)
2. [sklearn文档：Plot randomly generated classification dataset](http://sklearn.apachecn.org/cn/0.19.0/auto_examples/datasets/plot_random_dataset.html#sphx-glr-auto-examples-datasets-plot-random-dataset-py)
3. 
