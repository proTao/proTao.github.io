---
layout: post
date: 2018-04-01
title: 仓鼠一样收集到的python技巧
category: python
tags: 
- python
- trick
keywords:
description:
---

![](/img/cover/hamster3.jpeg)

### 1. format_map函数
print("我叫{name},我今年{age}岁了".format_map(dict(name="张勇涛",age=15)))

### 2. print函数参数
sep=""
end="\n"
file=sys.stdout
flush=False(对文件有用，默认在文件关闭时flush)

### 3. 协程
TODO

<!-- more -->

### 4. python的字典键
a={True:'a',1:'b',1.0:'c'}

Python字典中的键 是否相同（只有相同才会覆盖）取决于两个条件：

1、两者的值是否相等（比较`__eq__`方法）。
2、比较两者的哈希值是否相同（比较`__hash__`方法）。

字典表达式计算结果为 {true：'c'}，是因为键true，1和1.0都是相等的，并且它们都有相同的哈希值。

### 5. operator模块
参考[python operator模块学习](https://www.jianshu.com/p/1a3a2ae01c06)
operator模块是python中内置的操作符函数接口，它定义了一些算术和比较内置操作的函数。operator模块是用c实现的，所以执行速度比python代码快。
位操作：
> and_ 按位与
> invert 取反
> lshift(c,d) 左移位
> or_(c,d) 按位或
> rshift(d,c) 右移位
> xor(c,d) 异或

operator模块中的函数通过相应操作的标准Python接口（比如类的魔术方法）完成工作，所以它们不仅适用于内置类型，还适用于用户自定义类型。

属性和元素的getter方法

通过函数名执行对象的方法
```python
class Student(object):
    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name

stu1 = Student("tom")
```

执行stu1实例的getName方法有这么几种方式：
1. stu1.getName()
2. Student.getName(stu1)
3. f = operator.methodcaller("getName");f(stu1) # f是一个无参函数执行器，接受stu对象，执行对象成员函数
4. f = operator.methodcaller("getName", Student("tom"));f(Student); # f是一个有参函数执行器，参数是一个对象实例，接受一个类，执行类成员函数
5. getattr(stu1, "getName") #得到对象的方法，直接执行就行 


### 6. scipy.stats
统计模块
目前我用到的就是scipy.stats.binom.pmf，用来计算PMF，参数是（k，n，p）,都可以接受array-like的参数，对参数进行广播。


### bisect二分查找
不仅仅对列表进行二分查找，对任何实现了`__getitem__`和`__len__`这两个魔术方法的对象都可以为bisect的参数，因此可以利用这个在函数空间内进行二分搜索。
比如下面这个是我[leetcode875](https://leetcode.com/problems/koko-eating-bananas/description/)的代码。
```python
from math import ceil
from bisect import bisect_left

class Solution:
    def minEatingSpeed(self, piles, H):
        """
        :type piles: List[int]
        :type H: int
        :rtype: int
        """
        # 找到小于等于H的最大
        a = A(piles)
        return bisect_left(a, -H)

    
class A:
    def __init__(self, piles):
        self.piles = piles
        self.length = max(piles)
    def __getitem__(self, speed):
        # 这是一个单调减的函数
        if speed == 0:
            return float("-inf")
        else:
            return -sum(ceil(i / speed) for i in self.piles)
    
    def __len__(self):
        return self.length
```


### 7. 区分函数作用域与闭包
参考[Python五个知识点搞定作用域](http://python.jobbole.com/86465)
```python
a = 1
def f1():
    print(a)

def f2():
    a = 2
    f1()

f2() # output:1
```

关键是函数在未执行之前，作用域已经形成了，作用域链也生成了。

### 8. 删除长列表中的一项
对列表中某一项的删除代价还是挺高的，如果对列表的顺序没有要求，可以使用把删除项的值覆盖为列表中最后一项的值，然后调用pop方法。



### 9. 浮点数计算
使用浮点数时务必小心。比如，sum(0.1 for i in range(10)) == 1.0返回结果是False。在这里可以使用类似unitest模块中的assertAmostEqual函数：
```python
def almost_equal(x, y, places=7):
    # places是精确到小数点后第几位
    return round(abs(x-y),places)==0
```

两个接近等值的浮点数相减会损失大量的有效数字，因此尽量避免类似的操作。比如：用1/(sqrt(x+1)+sqrt(x))代替sqrt(x+1)-sqrt(x)

### 10. Bunch模式
```python
class Bunch(dict):
    def __init__(self, *args, **kwds):
        super(Bunch, self).__init__(*args,**kwds)
        self.__dict__ = self
struct=Bunch({'type': 'flat', 'genus': {'intensity': 'hot', 'level': 'medium'}, 'BOOL': True, 'family': 'chordata', 'size': 'huge'})
print(struct)
print(struct.type)
print(struct.genus.level) # 错误
```

- 假如你有一个类称为MyClass和这个类的一个实例MyObject。当你调用这个对象的方法MyObject.method(arg1, arg2)的时候,这会由Python自动转为MyClass.method(MyObject, arg1,arg2)——这就是self的原理了。

### 11. glob
`glob`完成文件通配符查找的相关操作。`iglob`方法可以返回一个迭代器。

### 12. numpy向量化函数
使用`np.vectorize`并行执行函数。

### 13. 默认未定义方法
```python
class A(object):
    def __init__(self,a,b):
        self.a1 = a
        self.b1 = b
        print('init')
    def a(self):
        print("a", self.a1, self.b1)
    def mydefault(self, *args, **kwargs):
        print('default')
    def __getattr__(self,name):
        return(self.mydefault)
a = A(1,2)
a.a()
a.b()
a.b(1)
a.b(name="tom")
```

### 14. 指定import
一个包里有三个模块，mod1.py, mod2.py, mod3.py，但使用from demopack import \*导入模块时，如何保证只有mod1、mod3被导入了？增加init.py文件，并在文件中增加：`__all__ = ['mod1','mod3']`


### 15. new 和 init
```python
class B(object):
    def fn(self):
        print('B fn')
    def __init__(self):
        print("B INIT")
class A(object):
    def fn(self):
        print('A fn')
    def __new__(cls,a):
        print("NEW", a)
        if a>10:
            return super(A, cls).__new__(cls)
        return B()
    def __init__(self,a):
        print("INIT", a)

a1 = A(5)
a1.fn()
a2=A(20)
a2.fn()
```
输出什么？使用new方法，可以决定返回那个对象，也就是创建对象之前，这个可以用于设计模式的单例、工厂模式。init是创建对象是调用的。

### 16. 真正的多进程

参考：
1. [python文档](https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor)
2. [Python并发编程之线程池/进程池--concurrent.futures模块](https://www.cnblogs.com/dylan-wu/p/7163823.html)

```python
import concurrent.futures
import math
import time

PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419
]

def is_prime(n):
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True

def main():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for number, prime in zip(PRIMES, executor.map(is_prime, PRIMES)):
            print('%d is prime: %s' % (number, prime))

if __name__ == '__main__':
    start = time.time()
    main()
    # for i in PRIMES:
        # print(i, is_prime(i))
    end = time.time()
    print(end - start)
```

### 17. 使用pathlib处理路径

### 18. 日期
`datetime`是python内置的日期库，`dateutil`是`datetime`的内置高级版本，`pendulum`对`datetime`封装了更智能的API。

### 19. flashtext
对于一些文本的搜索或者替换任务，正则表达式可以给力的完成，但是如果需要匹配的模式有上千条，使用`flashtext`可能是更好的选择，它的优点是不论搜索想有多少，运行的时间都是基本相同的。

### 20. fire
google开源的python转CLI的工具。

## 易错点
1. 默认参数的求值时机
```python
import time
def report(when=time.time()):
    return when

print(report())
print(report())
```
默认参数在定义的时候已经被确定。可以用lambda表达式代替。


相关阅读：
1. [干货分享：Python开发的高级技巧](http://developer.51cto.com/art/201611/522852.htm)
2. 别人家的[Python Trick](https://vimiix.com/python_tricks/#1)
3. 《Python3 Cookbook》
4. [wtfpython](https://github.com/satwikkansal/wtfpython)
5. [从字节码的角度加速python](http://python.jobbole.com/86545/)
