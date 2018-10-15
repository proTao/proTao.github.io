---
layout: post
date: 2017-6-24
title: numpy学习
category: 大数据
tags: 
- bigdata
- python
- numpy
keywords: 
description: 
---

## Numpy

### 学习动机

哪哪都用numpy！python数据处理不可能用不到他！

### 概览
- 核心类型是**ndarray对象**！

- ndarray数组大小不可变（*更改ndarray的大小将创建一个新的数组并删除原始数据*），封装了同质数据类型的n维数组。同质要求数组中存储相同的数据类型（*这使得在存储器中他们将具有相同的大小*）。**但是可以通过使用对象类型的数组来间接打破这一限制。**
- udarray的优势在于以python的代码长度达到c的运行速度，做到这一点的技术支持是NumPy内部预编译的c实现。这反映它的大部分功能的基础：**矢量化和广播**。
- 矢量化描述了在代码中没有任何显式循环:
- 广播就是指对矢量进行的操作“广播”至他的每一个元素。

### 基础

#### 数据类型

数据类型如下图：
![](/img/numpydatatype.png)

- 很多构造函数可以显示指定数据类型，如`arange(7,dtype=uint16)`
- 大部分类型之间可以强制类型转换，如：`float64()`,复数的类型转换会受到限制。
- 由于ndarray的同质性，可以方便的计算ndarray的占用空间，也可以使用`a.dtype.itemsize`查看内个数组元素在内存中占用的字节数。
- numpy的数据类型是dtype类，这个类也有属于自己的方法和属性。


#### ndarray数组
<!-- more -->
- 注意，一维数组的shape是(n,)，在吴恩达的课程中提到，这种数据类型会导致很多奇奇怪怪很难调试的bug，所以他推荐使用一维矩阵，即明确赋值n行1列。
- 索引方式不是array[x1][x2]...，而是array[x1,x2...]
- 切片和索引方式十分灵活，可以结合使用。如果在多维数组中执行翻转一维数组的命令,将在最前面的维度上翻转元素的顺序。如`print(c[::-1])`等同于`print(c[::-1,:,:])`,推荐写成完整的形式。
- ravel和flatten函数可以把数组展平，《Python数据分析基础教程：NumPy学习指南（第2版）》中说, flatten函数会请求分配内存来保存结果,而ravel函数只是返回数组的一个视图(view)，但是我尝试时没有尝试出这两个函数的区别。
- shape函数以tuple方式返回数组形状，reshape函数可以重新改变数组维度， resize和reshape函数的功能一样,但resize会直接修改所操作的数组。 
- transpose执行转置矩阵。二维的好说，三维矩阵转置没明白。
- NumPy数组有水平组合、垂直组合和深度组合等多种组合方式,我们将使用 vstack、dstack、hstack、column\_stack、row\_stack以及concatenate函数来完成数组的组合。hstack和vstack分别是将矩阵横向或者纵向组合，concatenate根据参数可以完成hstack和vstack的功能。 column\_stack函数对于一维数组将按列方向进行组合,而对于二维数组,column\_stack与hstack的效果是相同的;对于两个一维数组，row\_stack将直接层叠起来组合成一个二维数组，对于二维数组,row\_stack与vstack的效果是相同的。
- NumPy数组可以进行水平、垂直或深度分割,相关的函数有hsplit、vsplit、dsplit和split。我们可以将数组分割成相同大小的子数组,也可以指定原数组中需要分割的位置。
- 其他属性：
	- ndim：给出数组的维数,或数组轴的个数
	- size：给出数组元素的总个数
	- itemsize：数组中的元素在内存中所占的字节数
	- nbytes：这个属性的值其实就是itemsize和size属性值的乘积
	- T：转置
	- real：复数数组的实部
	- imag：复数数组的虚部
	- flat：返回一个flatiter对象,这是获得flatiter对象的唯一方式——我们无法访问flatiter的构造函数。这个所谓的“扁平迭代器”可以让我们像遍历一维数组一样去遍历任意的多维数组。除了遍历，可以用flatiter对象直接获取一个数组元素。
- tolist函数将ndarray转换为python的list。






     
> 矢量化编程是提高算法速度的一种有效方法。矢量化编程的思想就是尽量使用被高度优化的数值运算操作来实现算法。通常，一个编写Matlab/Octave程序的诀窍是：
>        代码中尽可能避免显式的for循环。
>通过不使用for循环实现相同功能，可以显著提升运行速度。对Matlab/Octave代码进行矢量化的工作很大一部分集中在避免使用for循环上，因为这可以使得Matlab/Octave更多地利用代码中的并行性，同时其解释器的计算开销更小。

### 更新于2018-06-02
在写EM算法第二篇文章的时候，自己实现混合伯努利分布，然后有各种矩阵乘的时候，都用numpy的广播解决，对此我只能说，NP大法好！
主要就是：
1. `@`实现矩阵乘
2. `_log_bernoulli`函数中，`X[:,None,:]*np.log(self.mu)`这一骚操作，本来我是要实现成for循环按列乘的，但是隐隐一个声音告诉我不要用for循环......尴尬。看了PRML读书伴侣，看到了这个小trick，利用None扩充ndarray的维度，然后尺寸对上了就可以利用广播进行矢量化计算了，美滋滋。
3. `np.clip`防止上下溢出，`np.allclose`检查参数收敛。





- - -
参考：
1. ufldl[矢量化编程](http://http://ufldl.stanford.edu/wiki/index.php?diff=2028&oldid=2027&title=%E7%9F%A2%E9%87%8F%E5%8C%96%E7%BC%96%E7%A8%8B)
2. [PRML读书伴侣ch9](https://github.com/ctgk/PRML/blob/master/prml/rv/bernoulli_mixture.py)
