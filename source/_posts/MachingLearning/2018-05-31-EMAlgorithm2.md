---
layout: post
title: EM算法原理与推导(续)
date: 2018-05-27
category: 机器学习
tags:
- generative
- algorithm
- maths
- tools
- machinelearning
keywords:
description:
---

## 关于更新参数
关于参数如何更新，其实有多种解释都一样，但是为了理清思路，我们要明确一点就是我们即使不对混合模型的对数似然进行任何变化，也是可以做MLE估计的，只是得到的参数最优值不是一个解析式，而是一个涉及到“隐变量”的式子，这才导致我们后续的EM算法并通过迭代方式来最大化似然。用GMM举例子，我们希望极大化：

$$ l(\theta)=\sum_{i=1}^mlog\sum_zP(x^{(i)},z^{(i)};\theta)\qquad(1)$$
$$=\sum_{i=1}^mlog\sum_k\frac{1}{(2\pi)^{n/2}|\Sigma_i|^{1/2}}exp\Big(-\frac{1}{2}(x-\mu_i)^T\Sigma_i^{-1}(x-\mu_i)\Big)*\phi_k \quad(1.1)$$

这个式子计算的是X被生成的概率，而不考虑来自于哪个组分。我们就啥也不考虑，假设求$$$\mu_k$$$的最优值，直接令其梯度为零，就可以得到：

$$ \sum_{i=1}^m \frac{\phi_k\mathcal{N}(x_i|\mu_k,\Sigma_k)}{\sum_j\phi_j\mathcal{N}(x_i|\mu_j,\Sigma_j)}*\Sigma_k^{-1}(x^{(i)}-\mu_k)=0 \qquad(2)$$
$$ \mu_k:=\frac{\sum_{i=1}^mP(z^{(i)}=k|x^{(i)};\mu_k,\Sigma_k)x^{(i)}}{\sum_{i=1}^mP(z^{(i)}=k|x^{(i)};\mu_k,\Sigma_k)} \qquad(2.1)$$

注意（2）中的大的分式就是出现在（2.1）中的后验概率。注意在（2.1）的解的形式，是对数据集中所有数据点的加权平均的方式得到参数的解，后验概率作为其中的权重因子。从感性上看，解的形式很好理解，正常单个的高斯分布参数估计就是求数据点的均值来得到高斯分布的均值参数，而GMM就是以“按劳分配“的方式更新。另外其他的参数更新也可以直接通过对（1.1）的MLE得到。
不出意外地，每个参数的估计公式中，都有**reponsibility**的参与，而责任作为后验概率，又依赖于参数，这使得我们清晰的得到EM算法迭代的思路。

## 期望最大化
既然这个算法叫期望最大化，那么这里就仔细看看期望在哪，怎么最大化的。
其实一切都在[上一篇文章](https://protao.github.io/2018/05/27/MachingLearning-2018-05-27-EMAlgorithm/#more)的（9）式中了。还是老生常谈的那句话，这几篇文章中寂静说过很多很多次了，**我们算不了复杂的边缘概率，于是妥协为计算联合分布的概率。但是想算联合分布，我们需要知道人为扩展出来的隐变量，但是我们不知道，所幸我们知道隐变量当前状态下的后验概率。那么好，我们就计算联合分布（的对数）的期望。**这个期望，在PRML一书中，用下式表示：

$$ \mathcal{Q}(\theta, \theta^{old})=\sum_ZP(Z|x,\theta^{old})lnP(x,Z|\theta) \qquad(3)$$
$$ \mathcal{Q}(\theta, \theta^{old})=\sum_i\sum_ZP(Z|x^{(i)},\theta^{old})lnP(x^{(i)},Z|\theta) \qquad(3.1)$$
（3）是单个数据点的形式，容易推导，（3.1）是全部数据的形式，是真正的期望函数。这个就是我们的算法中核心的期望，也是最大化的目标，我们希望给调整$$$\theta$$$，来最大化这个式子，在M步中$$$\theta^{old}$$$是固定的，后验分布也是固定的。（3.1）式其实和[上一篇文章](https://protao.github.io/2018/05/27/MachingLearning-2018-05-27-EMAlgorithm/#more)的（9）和（10）式是一致的。log里的形式不太一样，但是不会影响最终的结果。

### 举例：伯努利混合模型
*参考PRML*

假设数据是D维向量，该数据的每一个维度来自于一个独立的伯努利分布，然后混合模型来自于K个component的线性组合，此时我们有$$$KD$$$个参数，可以认为$$$\mu_{ij}$$$表示第i个多维伯努利组分的第j维的参数。那么显变量的对数似然为：
$$ln(X;\mu,\pi)=\sum_{i=1}^mln\Big( \sum_{k=1}^K\pi_k\prod_{d=1}^D\mu_{kd}^{x_{id}}(1-\mu_{kd})^{1-x_{id}} \Big)$$
这个无法直接求解，按照上面叙述的，直接写出E步需要求的后验概率和期望：
后验概率：
$$ \omega_{nk}=P(z_n=k|x_n;\pi,\mu)=\frac{\pi_kP(x_n|\mu_k)}{\sum_j\pi_jP(x_n|\mu_j)} $$
联合分布对数似然的期望:
$$ \mathbb{E}_Z\big[lnP(X,Z|\mu,\pi)\big]=\sum_i\sum_Z\omega_{nk}\big(ln\pi_k+\sum_{d=1}^D[x_{id}ln\mu_{kd}+(1-x_{id})ln(1-\mu_{kd})]\big) $$
然后M步对其最大化。

#### 实践
```python
import numpy as np
import pathlib
from scipy.special import logsumexp
from sklearn.metrics import confusion_matrix

p=pathlib.Path("trainingDigits/")
cache=[]
label=[]
for fname in p.iterdir():
    with open(str(fname),'r') as f:
        cache.append(i.strip() for i in f.readlines())
        label.append(int(str(fname.name)[0]))
data=np.array([[list(map(int,line)) for line in digit] for digit in cache])
label=np.array(label)

p=pathlib.Path("testDigits/")
cache=[]
answer=[]
for fname in p.iterdir():
    with open(str(fname),'r') as f:
        cache.append(i.strip() for i in f.readlines())
        answer.append(int(str(fname.name)[0]))
test=np.array([[list(map(int,line)) for line in digit] for digit in cache])
answer=np.array(answer)

M = len(data)
D = np.prod(data[0].shape)
K = len(np.unique(label))

# initial by label
init_mu=[]
init_phi=[]
for i in range(K):
    index=label==i
    labeled_data=data[index].reshape(-1,D)
    init_mu.append(np.sum(labeled_data,axis=0)/len(labeled_data))
    init_phi.append(sum(label==i)/M)

init_mu=np.array(init_mu)
init_phi=np.array(init_phi)



class MixtureBernoulli:
    def __init__(self,K,D,M):
        self.K=K # 组分数
        self.D=D # 数据维度
        self.M=M # 数据规模
        self.phi = np.random.ranf((1,K))
        self.phi /= sum(self.phi)
        self.mu = np.random.ranf((K,D))
    
    def setPara(self, phi=None, mu=None):
        if phi is not None:
	        self.phi = phi
        if mu is not None:
        	self.mu = mu
    
    def _log_bernoulli(self, X):
        np.clip(self.mu, 1e-10, 1-1e-10, out=self.mu)
        return (X[:,None,:]*np.log(self.mu)+(1-X[:,None,:])*np.log(1-self.mu)).sum(axis=-1)

    def _E_Step(self, X):
        responsibility=np.log(self.phi)+self._log_bernoulli(X)
        responsibility -= logsumexp(responsibility, axis=1).reshape((X.shape[0],1))
        return np.exp(responsibility)

    def _M_Step(self, X, responsibility):
        # Nk是所有数据点在第k个组分的权重和，所以sum(Nk)=M
        Nk = np.sum(responsibility,axis=0).reshape((1,self.K))
        self.mu = ((X.T @ responsibility)/Nk).T
        self.phi=Nk/self.M
    
    def fit(self,X,verbose=False):
        i=0

        while True:
            old_params = np.hstack((self.phi.ravel(), self.mu.ravel()))
            resp = self._E_Step(X)
            self._M_Step(X, resp)
            if np.allclose(old_params, np.hstack((self.phi.ravel(), self.mu.ravel()))):
                break
            else:
                i += 1
                print("iteration {}".format(i))
                if verbose:
                    pred=np.argmax(resp,axis=1)
                    print(pred[:1600].reshape(400,-1)[:,0].reshape((20,20)))

    def classify_proba(self, X):
        """
        posterior probability of cluster
        p(z|x,theta)
        Parameters
        ----------
        X : (sample_size, ndim) ndarray
            input
        Returns
        -------
        output : (sample_size, n_components) ndarray
            posterior probability of cluster
        """
        return self._E_Step(X)
        
    def classify(self, X):
        """
        classify input
        max_z p(z|x, theta)
        Parameters
        ----------
        X : (sample_size, ndim) ndarray
            input
        Returns
        -------
        output : (sample_size,) ndarray
            corresponding cluster index
        """
        return np.argmax(self.classify_proba(X), axis=1)
        
mb = MixtureBernoulli(K,D,M)
mb.setPara(phi=init_phi, mu=init_mu)
mb.fit(data.reshape(-1, D),verbose=True)

pred=mb.classify(test.reshape(test.shape[0],32*32))
confusion_matrix(pred, answer)

mu0=mb.mu[0].reshape((32,32))
plt.imshow(mu0, cmap="gray")
plt.show()
```

最后的分类正确率是87%左右。

还是别人家的代码好啊。注意`logsumexp`这个函数，我就知道有，但是没找到！然后为了防止下溢出用了对数计算，还有`np.clip`辅助。多分类问题使用`sklearn.metric`中的混淆矩阵函数进行直观评估。还有自带的`pathlib`是好帮手。

## EM算法与KL散度
限制考虑单个数据的情况，因为是对数似然，全部数据集只需要求和。
$$J(Q,\theta)=\sum_{z^{(i)}}Q_i(z^{(i)})log\frac{P(x^{(i)},z^{(i)};\theta)}{Q_i(z^{(i)})} \qquad(4)$$
$$J(Q,\theta)=\sum_{z^{(i)}}Q_i(z^{(i)})log\frac{P(z^{(i)}|x^{(i)};\theta)P(x^{(i)};\theta)}{Q_i(z^{(i)})} \qquad(4.1)$$
$$J(Q,\theta)=\sum_{z^{(i)}}Q_i(z^{(i)})lnP(x^{(i)};\theta)+\sum_{z^{(i)}}Q_i(z^{(i)})log\frac{P(z^{(i)}|x^{(i)};\theta)}{Q_i(z^{(i)})} \qquad(4.2)$$
$$J(Q,\theta)=lnP(x^{(i)};\theta)-KL(Q||P) \qquad(4.3)$$
$$lnP(x^{(i)};\theta)=J(Q,\theta)+KL(Q||P) \qquad(4.4)$$

KL散度这里不展开说，只需要知道：KL散度衡量两个分布的距离，P是被衡量的分布，Q是用来拟合的分布，当两个分布一样的时候，KL散度为零。
（4.4）式的意义在于，将真正的对数似然拆分成了两部分，第一部分是我们固定$$$\theta$$$构建的下界，第二部分是在$$$\theta$$$处，下界和真正似然的差距。KL距离是一定大于零的，**在给定$$$\theta$$$时**，对数似然可以想（4.4）一样拆成两部分，我们希望下界$$$J$$$尽可能的大，以使得得到最紧的下界，即KL距离尽可能的小，所以必须要让Q分布等于$$$P(z|x;\theta)$$$，于是得到了和第一篇文章中使用Jensen不等式殊途同归的结果。

![图1：在$$$\theta$$$上优化对数似然](/img/EM2.png)
![图2：固定$$$\theta$$$看（4.4）式](/img/EM3.png)

图2的左图表示图1中$$$\theta_{old}$$$经过E步之后，（4.4）式中三个部分的各个状态：在$$$\theta_{old}$$$处，下界紧贴目标函数且KL距离为0的状态。图2的右图表示图1中$$$\theta_{new}$$$的经过M步的状态，即对下界进行优化，得到新的参数估计。此时在图一中花了三条横线，分别对应图2右图中的三条线，**紫色线表示本次E步之前的对数似然，然后从$$$\theta_{old}$$$变成$$$\theta_{new}$$$后，$$$J(Q,\theta)$$$提升到了蓝线的高度，$$$lnP(x^{(i)};\theta)$$$提升到了红线的高度，$$$KL(Q||P)$$$从0变成了蓝红两线的间距**，然后本次的M又会把这个间距缩小成0，以此类推。

参考：
1. [怎么通俗易懂地解释EM算法并且举个例子?](https://www.zhihu.com/question/27976634?sort=created)
2. [关于EM算法的九层境界的浅薄介绍，Hinton和Jordan理解的EM算法](http://www.elecfans.com/d/604076.html)
3. [从最大似然到EM算法：一致的理解方式](https://spaces.ac.cn/archives/5239)
4. [梯度下降和EM算法：系出同源，一脉相承](https://spaces.ac.cn/archives/4277)
5. Patttern Recognition and Machine Learning 中译版
6. [PRML读书伴侣ch9](https://github.com/ctgk/PRML/blob/master/prml/rv/bernoulli_mixture.py)