---
layout: post
date: 2017-08-23
title: python算法
category: 读书笔记
tags: 
- algorithm 
- python
keywords: 
description: 
---

# 第一章
## 习题
- 1-1 不对，数据量会随之越来越大，因此算法的重要性会越来越高。

- 1-2 bruce嘛，挨个搜索，用过的标记一下。

# 第二章
## point
- O(nlgn)=O(lgn!)
- 算法设计的目标是降低渐进复杂度，算法工程的目的是降低常数
- 使用timeit计时，（我不太了解，我觉得time模块也可以替代，不知道孰优孰劣），在命令行中使用python -m timeit。
- 使用cProfile查看函数瓶颈（会把每一行的执行时间计算出来）。
- python -i 在交互模式中引入使用py文件中的全局定义。
- 一个图的最佳表示方法取决于再图上进行的算法。如果是对一个节点的所有边进行遍历。那么邻接**列表**更好，如果是要检查是否有邻接关系存在，那么邻接**集合**会更好。当然，如果邻接列表有序，在上面的搜索可以降低到对数级别。
- 小tips，对列表中某一项的删除代价还是挺高的，如果对列表的顺序没有要求，可以使用把删除项的值覆盖为列表中最后一项的值，然后调用pop方法。
- 使用x=float("inf")来为x赋值无穷大
- numpy真的很强大，包括对数组的处理.
- 在scipy中有专门的处理稀疏矩阵的sparse包
- **Bunch模式**

```python
class Bunch(dict):
	def __init__(self, *args, **kwds):
    	super(Bunch, self).__init__(*args,**kwds)
        self.__dict__ = self
```

- 假如你有一个类称为MyClass和这个类的一个实例MyObject。当你调用这个对象的方法MyObject.method(arg1, arg2)的时候,这会由Python自动转为MyClass.method(MyObject, arg1,arg2)——这就是self的原理了。
- 一个子类型在任何需要父类型的场合可以被替换成父类型,即对象可以被视作是父类的实例,这种现象被称为多态现象。
- 不一定所有的图都被显式的静态的存储，也可以在计算到该节点时该节点根据某些参数计算出自己的邻居。比如魔方问题。
- 子问题图
- 图工具：
	- networkX
	- python-graph
	- Graphine
	- Graph-tool
	- Pygr
	- Gato
	- PADS
- python的append有过度分配的特性
- 使用浮点数时务必小心。比如，sum(0.1 for i in range(10)) == 1.0返回结果是False。在这里可以使用类似unitest模块中的assertAmostEqual函数：
```python
def almost_equal(x, y, places=7):
	# places是精确到小数点后第几位
    return round(abs(x-y),places)==0
```

- 如果需要精确的浮点数计算，使用decimal模块或者Sage模块都是可以替代的选择。
- 两个接近等值的浮点数相减会损失大量的有效数字，因此尽量避免类似的操作。比如：用1/(sqrt(x+1)+sqrt(x))代替sqrt(x+1)-sqrt(x)

# 第三章 计数初步
## point
- python中的排序算法timsort是归并排序的一种自然适应版。它在保留最糟的，线性对数时间级别的同时，兼具实现了最佳的线性级别的运行时间。

# 第四章 归纳/递归和归简
## point
- 很多函数式语言提供尾递归优化机制。即修改尾递归为循环，使得其不受最大递归深度的限制。
- 
