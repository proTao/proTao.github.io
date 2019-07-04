---
layout: post
date: 2018-05-07
title: 基数估计：FM算法
category: 大数据
tags:
- bigdata
- algorithm
- dataprocessing
keywords:
description:
---

## LogLog算法

参考《大数据——互联网大规模数据挖掘与分布式处理一书》中所提到的FM算法，下面给出简单的python实现。


代码中比较重要的就是testFM函数。重要的参数是each_group_k，表示了LogLog中用后多少位表示桶号，然后对所有元素求平均进行估计。group_num是参考《大数据》书上提到的中位数方法的小改进，就是不只是使用平均进行估计，而是使用不同的哈希函数LogLog算法重复多遍，然后每个LogLog算法内求平均，多个LogLog算法内求中位数。
结果改进的并不多，索性直接用一组LogLog，hashmap设置的大一些来得直接。

另一个需要说明的地方就是代码返回的最后乘了一个magic number0.79402。这个的原因是值求平均的化得到的是有偏估计，需要使用这个数修正偏差得到无偏估计，这个数怎么得到的还是去看原论文吧......我是没看。

<!-- more -->

```python
def streamGen(streamlen=100, c=10):
    # 实现一个流数据生成器，第一个参数给定流数据长度，第二个参数给定流数据中可能出现的不同元素种类数
    i = 0
    while i < streamlen:
        yield random.randrange(c)
        i += 1

def countEndsZeros(dig, verbose=False):
    # dig是一个字符串，表示一个元素的二进制哈希值
    i = len(dig)-1
    while i and dig[i]=='0':
        i -= 1
    return len(dig)-1-i


def testFM(stream, group_num=1, each_group_k = 13):
    standard_ans = set()
    each_group = 1<<each_group_k
    estimators_num = group_num * each_group
    estimators = [0] * estimators_num
    salts = "1234567890-=qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM,.?!@#$%^&*()_+"
    for new_item in stream:
        standard_ans.add(new_item)
        for i in range(group_num):
            h = int(hashlib.md5(bytes(str(new_item)+salts[i], encoding="ascii")).hexdigest(), base=16)
            bucket = h&(each_group-1) + i*each_group
            bucket_hash = h >> each_group_k
            estimators[bucket] = max(estimators[bucket], countEndsZeros(bin(bucket_hash)))

        if verbose:
            print(estimators)

    means = []

    for i in range(group_num):
        group_esti = sum(estimators[i*each_group:(i+1)*each_group])/each_group
        means.append(group_esti)
    print(means)
    sorted(means)
    return len(standard_ans), 2**means[int(group_num//2)]*each_group*0.79402
```


对于LogLog算法，桶越多越好，但是这个是对于大量流元素而言的，即基本上每个桶都不为零，如果在刚开始的时候或者流中不同元素远远小于桶数的时候，估计将会产生很大的偏差。

```bash
In [258]: res = [testFM(streamGen(100,100)) for i in range(10)]
[0.010009765625]
Out[259]: (61, 6549.8993294722495)

In [260]: res = [testFM(streamGen(10000,10000)) for i in range(10)]
[0.7119140625]
Out[261]: (6373, 10654.396931644287)

In [262]: testFM(streamGen(100000,100000)) for i in range(10)
3.3028564453125
(63003, 64191.90240800883)
```

通过上述代码可以发现，我们始终默认桶数是2^13=8192。当元素比较大的时候算法工作的比较好。然而元素较少的时候，比如流长度为100的时候，产生了非常大的偏差，原因在于，观察算法输出的桶统计的平均数是0.0100097，然而在最后返回的时候会乘以桶的数目，即2**0.010009765625*2**13*0.79402=6549.8993294722495。

> 分桶平均的基本原理是将统计数据划分为m个桶，每个桶分别统计各自的kmax并能得到各自的基数预估值，最终对这些估计值求平均得到整体的基数估计值。LLC中使用几何平均数预估整体的基数值，但是当统计数据量较小时误差较大；HLL在LLC基础上做了改进，采用调和平均数，调和平均数的优点是可以过滤掉不健康的统计值。



因此HyperLogLog使用的是调和平均数，使用调和平均数的话会使算法变得更加复杂一些，因为偏差修正值对随着数据规模的改变而改变。

> 虽然调和平均数能够适当修正算法误差，但作者给出一种分阶段修正算法。当HLL算法开始统计数据时，统计数组中大部分位置都是空数据，并且需要一段时间才能填满数组，这种阶段引入一种小范围修正方法；当HLL算法中统计数组已满的时候，需要统计的数据基数很大，这时候hash空间会出现很多碰撞情况，这种阶段引入一种大范围修正方法。最终算法用伪代码可以表示为如下。

伪代码：
```python
m = 2^b   # with b in [4...16]

if m == 16:
    alpha = 0.673
elif m == 32:
    alpha = 0.697
elif m == 64:
    alpha = 0.709
else:
    alpha = 0.7213/(1 + 1.079/m)

registers = [0]*m   # initialize m registers to 0

###########################################################################
# Construct the HLL structure
for h in hashed(data):
    register_index = 1 + get_register_index( h,b ) # binary address of the rightmost b bits
    run_length = run_of_zeros( h,b ) # length of the run of zeroes starting at bit b+1
    registers[ register_index ] = max( registers[ register_index ], run_length )

##########################################################################
# Determine the cardinality
DV_est = alpha * m^2 * 1/sum( 2^ -register )  # the DV estimate

if DV_est < 5/2 * m: # small range correction
    V = count_of_zero_registers( registers ) # the number of registers equal to zero
    if V == 0:  # if none of the registers are empty, use the HLL estimate
          DV = DV_est
    else:
          DV = m * log(m/V)  # i.e. balls and bins correction

if DV_est <= ( 1/30 * 2^32 ):  # intermediate range, no correction
     DV = DV_est
if DV_est > ( 1/30 * 2^32 ):  # large range correction
     DV = -2^32 * log( 1 - DV_est/2^32)
```








参考:
1. [超酷算法：基数估计](http://blog.jobbole.com/78255/)
2. 《解读Cardinality Estimation算法》系列 —— 张洋
3. [神奇的HyperLogLog算法](http://www.rainybowe.com/blog/2017/07/13/%E7%A5%9E%E5%A5%87%E7%9A%84HyperLogLog%E7%AE%97%E6%B3%95/index.html?utm_source=tuicool&utm_medium=referral)
4. [HyperLogLog Demo](http://content.research.neustar.biz/blog/hll.html)
5. [调和平均数](https://baike.baidu.com/item/%E8%B0%83%E5%92%8C%E5%B9%B3%E5%9D%87%E6%95%B0/9661021)

