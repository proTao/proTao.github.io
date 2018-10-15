---
layout: post
date: 2018-04-21
title: Python Cookbook3 (3)数字日期和时间
category: 读书笔记
tags:
- reading
- python
keywords:
description:
---

### 1. 数字的舍入
使用`round`函数。round 函数返回离它最近的偶数。也就是说,对 1.5 或者 2.5 的舍入运算都会得到 2。
```python
print(round(12.3)) # 12
print(round(1.23, 1)) # 1.2
print(round(1.25, 1)) # 1.2
print(round(1.27, 1)) # 1.3
print(round(127, -1)) # 130
```
如果只希望输出一定的宽度（也会舍入啊？没明白区别在哪），使用`format`。
```python
format(1.23456, '0.2f') # 1.23
format(1.23456, '0.3f') # 1.235
```

### 2. 执行精确的浮点数运算
浮点数的一个普遍问题是它们并不能精确的表示十进制数。并且,即使是最简单的数学运算也会产生小的误差。这些错误是由底层 CPU 和 IEEE 754 标准通过自己的浮点单位去执行算术时的特征。由于 Python 的浮点数据类型使用底层表示存储数据,因此你没办法去避免这样的误差。
```python
print(1.2+2.4) # 反正不是3.6...
```
使用`Decimal`模块，再去书里面看。

### 3. 数字的格式化输出
```python
x = 1234.56789
print(format(x, '0.2f'))
print(format(x, '>10.1f')) # 10位长度右对齐
print(format(x, '<10.1f')) # 10位长度左对齐
print(format(x, '^10.1f')) # 10位长度居中
```
当指定数字的位数后,结果值会根据 round() 函数同样的规则进行四舍五入后返回。`format`同样适用于`Decimal`。


* * *



1. [知乎：怎样才算是精通python](https://www.zhihu.com/question/19794855/answer/129270643)
2. [Python格式化字符串](http://python.jobbole.com/85319/)
3. [Python3.5 协程究竟是个啥](http://python.jobbole.com/86481/)
4. [python多重继承新算法C3介绍](http://www.jb51.net/article/55748.htm)
5. [Python: 你不知道的 super](http://python.jobbole.com/86787/)
6. [python的类变量与实例变量以及__dict__属性](https://www.cnblogs.com/duanv/p/5947525.html)
7. [详解Python中 __get__和__getattr__和__getattribute__的区别](http://www.jb51.net/article/86749.htm)
8. [Python黑魔法————描述器](http://python.jobbole.com/85176/)
9. [Python中的classmethod和staticmethod有什么具体用途](https://www.zhihu.com/question/20021164)
10. [如何理解python装饰器](https://www.zhihu.com/question/26930016)
11. [详解python的装饰器](https://www.cnblogs.com/cicaday/p/python-decorator.html)
12. [Python __getattribute__ vs __getattr__ 浅谈](http://python.jobbole.com/84095/)
13. [你真的理解Python中MRO算法吗？](http://python.jobbole.com/85685/)
14. [关于python中inspect模块的一些探究](https://blog.csdn.net/weixin_35955795/article/details/53053762)
15. [Python “黑魔法” 之 Meta Classes](http://python.jobbole.com/85126/)
16. [Range对象并不是迭代器](https://blog.csdn.net/IaC743nj0b/article/details/79547122)
