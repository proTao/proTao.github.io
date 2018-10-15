---
layout: post
date: 2017-9-1
title: 浅析Bloom Filter与java实现
category: 大数据
tags: 
- maths 
- bigdata
keywords:
description:
---

## 概述

布隆过滤器实际上对外表现为一个set类型，可以实现添加元素/判断元素是否存在/并集等操作。需要注意的是布隆过滤器不提供元素的删除功能，这一点特点使得他不能作为常规的集合类型使用，那么它的使用场景是保存大量固定元素的集合，并判断一个新到来的元素是否已经存在在这个集合中,s所谓“过滤器”也是因此得名。他以一定误报率（不在的元素判断为在）为代价，减少了大量存储空间。

## 原理
![](/img/Bloomfilter.png)

BF主要需要包含一个长度为m位的位图，和k个相互独立的哈希函数，哈希函数的值域在0到m-1之间。
如果希望加入一个元素，那么将该元素输入k个哈希函数得到k个索引，将BitArray中对应索引位置置1即可。
如果希望查询一个元素是否存在，同样将该元素输入k个哈希函数，得到k个索引，如果k个索引位置中任一位置不存在，如果所有位置都是1，那么该元素就有很大可能存在。

java实现：
```
public class BloomFilter<E> {

    private BitSet bf;
    private int bitArraySize = 100000000;
    private int numHashFunc = 10;

    public BloomFilter() {
        bf = new BitSet(bitArraySize);
    }

    public void add(E obj) {
        int[] indexes = getHashIndex(obj);

        for (int index : indexes) {
            bf.set(index);
        }
<!-- more -->
    }

    public boolean contains(E obj) {
        int[] indexes = getHashIndex(obj);

        for (int index : indexes) {
            if (bf.get(index) == false) {
                return false;
            }
        }
        return true;
    }

    public void union(BloomFilter<E> other) {
        bf.or(other.bf);
    }

    protected int[] getHashIndex(E obj) {
        int[] indexes = new int(numHashFunc);

        long seed = 0;
        byte[] digest;
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            md.update(obj.toString().getBytes());
            digest = md.digest();

            for (int i=0; i < 6; i++) {
                seed = seed ^ (((long)digest[i] & 0xFF))<<(8*i);
            }
        } catch (NoSuchAlgorithmException e) { }

        Random gen = new Random(seed);

        for (int i = 0; i < numHashFunc; i++) {
            indexes[i] = gen.nextInt(bitArraySize);
        }

        return indexes;
    }
}
```

## 伪正率
由于一个哈希函数应将一个元素等概率的映射到BitArray的一位，因此，某一位为1的概率是：

\\[1/m\\]

一个元素经过一个hash映射到BitArray后，某一位仍然是0的概率

\\[1-1/m\\]

因为一个元素需要经过k个hash映射，因此一个元素加入BF中，某一位仍然是0的概率：

\\[(1-1/m)^k\\]

同理，存放n个元素的BF，某一位是0的概率：

\\[(1-1/m)^{kn}\\]

存放n个元素的BF，某一位是1的概率：

\\[1-(1-1/m)^{kn}\\]

某k个不同比特位被这前面n个元素置1的概率

\\[(1-(1-1/m)^{kn})^k\\]

当m很大的时候

\\[ \lim_{x\rightarrow+\infty}(1-(1-1/m)^{kn})^k \\] <br/>
\\[ =\lim_{x\rightarrow+\infty}(1-(((1-1/m)^m)^{nk/m})^k\\] <br/>
\\[ =((1-e^{-kn/m})^k \\]

这个推导不是完全正确的,因为它假定每一位被设置的概率独立。但即使它是近似的,我们也可以看出误报的概率会随着m(数组)的比特数的增加而变小,随着n(插入元素)的数量增加而增大。并且即使我们通过没有假设独立的方式推导，还是可以得到相同的结果。

## 最优的哈希函数数量
我们假设\\[p=e^{-kn/m}\\]\\[k=-m/nln(p)\\]
他是当m趋近于无穷大时，存放n个元素的BF，某一位是1的近似概率。我们的目标函数是误报率，即\\[ ((1-e^{-kn/m})^k \\]
出于求导的方便考虑，我们对该函数的对数求导\\[ ln(((1-e^{-kn/m})^k) \\]
带入p，得到
\\[ -m/n*ln(p)ln(1-p) \\]

根据对称性，当p=0.5时，伪正率最低。所以最优的k应该等于ln2*m/n。



## 思考
在计算机科学中，我们常常会碰到时间换空间或者空间换时间的情况，即为了达到某一个方面的最优而牺牲另一个方面。Bloom Filter在时间空间这两个因素之外又引入了另一个因素：错误率。在使用Bloom Filter判断一个元素是否属于某个集合时，会有一定的错误率。也就是说，有可能把不属于这个集合的元素误认为属于这个集合（False Positive），但不会把属于这个集合的元素误认为不属于这个集合（False Negative）。在增加了错误率这个因素之后，Bloom Filter通过允许少量的错误来节省大量的存储空间。

## 参考
1. http://blog.csdn.net/dadoneo/article/details/6847481
2. hadoop in action
3. 维基百科
