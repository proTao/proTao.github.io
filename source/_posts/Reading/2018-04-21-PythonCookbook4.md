---
layout: post
date: 2018-04-21
title: Python Cookbook3 (4)迭代器与生成器
category: 读书笔记
tags:
- reading
- python
keywords:
description:
---


### 0. 章前tips

这一章有关迭代器。这里一定要区分迭代器和可迭代对象。range是惰性可迭代对象（当然了，迭代器也是惰性的），却不是迭代器。`iter(range(n))`才能获得range对象的迭代器，实际上使用iter可以从任何可迭代对象中获得迭代器，迭代器唯一能做的就是next直到StopIteration。所有的迭代器都是可迭代对象，意思是你可以从一个迭代器中得到一个迭代器，因此你可以遍历一个迭代器。
```python
a = [1,2,3]
it1 = iter(a)
it2 = iter(it1)

# 其实it1和it2是同一个对象的两个引用

```
enumerate、zip、reversed和其他一些内置函数会返回迭代器。生成器（无论来自生成器函数还是生成器表达式）是一种创建迭代器的简单方法。注意下面的代码中，a不是一个元组，a是一个生成器对象。生成器表达式是列表推倒式的生成器版本，看起来像列表推导式，但是它返回的是一个生成器对象而不是列表对象。
```python
a = (for i in range(10))
```

而range本身不是迭代器，因为无法对于range调用next函数。与迭代器不同的是，我们可以遍历一个 range 对象而不「消耗」它。range 对象在某种意义上是「惰性的」，因为它不会生成创建时包含的每个数字，相反，当我们在循环中需要的时候，它才将这些数字返回给我们。不像生成器，range 对象有长度，并且可以被索引。如果你想要一个 range 对象的描述，可以称它们为懒序列，range 是序列（如列表，元组和字符串），但并不包含任何内存中的内容，而是通过计算来回答问题。


<!-- more -->


```python
a = range(10)

# 这一段代码可以多次执行
for i in a:
    print(a)
```
你可以询问他们是否包含某元素而不改变他们的状态。迭代器的特点是，当遍历它时，这些元素将从迭代器中被消耗掉，有时候这个特性可以派上用场（以特殊的方式处理迭代器）。
```python
a = range(3)
b = iter([1,2,3])
print(2 in a)
print(2 in a)
print(2 in b)
print(2 in b)
```

详见[Python：range 对象并不是迭代器](https://blog.csdn.net/IaC743nj0b/article/details/79547122)

对于支持随机访问的数据结构：list、tuple等，迭代器和经典的for循环（索引访问）相比，并无优势，反而失去了索引值。不过可以使用内置函数enumerate（）找回这个索引值。但对于无法随机访问的数据结构：set（），迭代器是唯一的访问元素的方式。
**省内存**：迭代器不需要事先准备好整个迭代过程中的所有元素，仅仅在迭代到某个元素时才计算该元素，而在这之前或之后，元素可以不存在或销毁。

### 1. 手动遍历迭代器
```python
# 捕获迭代终止异常
a = [1,2,3]
it = iter(a)
try:
    while True:
        ch = next(it)
        print(ch)
except StopIteration:
    print("结束")

# 为迭代失败设置异常值
a = [1,2,3]
it = iter(a)
ch = True
while ch:
    ch = next(it,None)
    print(ch)
```

对于返回的StopIteration异常，我们在迭代中通常使用的 for 语句会自动处理这种细节,所以你无需担心。

### 2. 代理迭代
Python 的迭代器协议需要 iter() 方法返回一个实现了 next() 方法的迭代器对象。如果你只是迭代遍历其他容器的内容,你无须担心底层是怎样实现的。你所要做的只是传递迭代请求既可。这里的 iter() 函数的使用简化了代码, iter(s) 只是简单的通过调用s.iter() 方法来返回对应的迭代器对象,就跟 len(s) 会调用 s.len() 原理是一样的。
```python
# 同样用magic method实现，类似于__len__
class L:
    def __init__(self, val, n):
        self.val = val
        self.l = range(n)
        self.length = n
    def __len__(self):
        return self.length
    def __iter__(self):
        return iter(self.l)
    def __repr__(self):
        return "type is L, length is {}, value is {}".format(self.length, self.val)
    def __str__(self):
        return "print func return val:{}".format(self.val)

l = L(-1,5)
print(len(l))
print(l)
for i in l:
    print(i)
```

### 3. 使用生成器创建新的迭代模式
一个函数中需要有一个 yield 语句即可将其转换为一个**生成器**。为了使用这个函数,你可以用 for 循环迭代它或者使用其他接受一个可迭代对象的函数 (比如 sum() , list() 等)。一个函数中需要有一个 yield 语句即可将其转换为一个生成器。跟普通函数不同的是,生成器只能用于迭代操作。
```python
def myrange(start, stop, increment):
    x = start
    while x < stop:
        yield x
        x += increment
```

到这里可能会有点混乱，迭代器生成器是一个东西吗？如果不是的话有什么区别嘛？
看图说话：
![生成器迭代器的关系](/img/generator.png)

一言以蔽之，生成器就是方便的迭代器，你只需要写一个yield语句，系统自动帮你实现迭代器协议。

参考：[Iterables vs. Iterators vs. Generators](https://nvie.com/posts/iterators-vs-generators/)


### 4. 实现迭代器协议



### 5. 反向迭代
反向迭代仅仅当对象的大小可预先确定或者对象实现了 reversed () 的特殊方法时才能生效。如果两者都不符合,那你必须先将对象转换为一个列表才行。要注意的是如果可迭代对象元素很多的话,将其预先转换为一个列表要消耗大量的内存。

定义一个反向迭代器可以使得代码非常的高效,因为它不再需要将数据填充到一个列表中然后再去反向迭代这个列表。
```python
class Countdown:
    def __init__(self, start):
        self.start = start

    # Forward iterator
    def __iter__(self):
        n = self.start
        while n > 0:
            yield n
            n -= 1

    # Reverse iterator
    def __reversed__(self):
        n = 1
        while n <= self.start:
            yield n
            n += 1

for rr in reversed(Countdown(30)):
    print(rr)

for rr in Countdown(30):
    print(rr)
```

### 6. 带有外部状态的生成器函数
我们定义了一个类，类中实现了__iter__魔术方法。我们可以对该对象使用for循环遍历，但是如果不用for循环，要先用iter()全局方法将这个对象转化为迭代器，这也就告诉我们，实现了__iter__的类不是迭代器，而是可迭代对象。而for in循环会自动将可迭代对象转化为迭代器并通过next方法遍历。(这可以通过dis包反编译出的指令看出来)。实现了__next__的才是迭代器。
而生成器就是一个普通的python函数，它特殊的地方在于函数体中没有return关键字，函数的返回值是一个生成器对象。当执行生成器函数时它返回的是一个生成器对象，此时函数体中的代码并不会执行，只有显示或隐示地调用返回的对象的next方法的时候才会真正执行里面的代码。
生成器在Python中是一个非常强大的编程结构，可以用更少地中间变量写流式代码，此外，相比其它容器对象它更能节省内存和CPU，当然它可以用更少的代码来实现相似的功能。

参考：[完全理解 Python 迭代对象、迭代器、生成器](http://python.jobbole.com/87805/)

### 7. 迭代器切片
刚接触到python的人最先接触到的python的特性应该就是切片，对于迭代器的话不能用常规的内存容器上的切片方式。
可以使用`itertools.islice()`，接收参数(对象，开始，终止，步长)。迭代器和生成器不能使用标准的切片操作,因为它们的长度事先我们并不知道 (并且也没有实现索引)。函数 islice() 返回一个可以生成指定元素的迭代器,它通过遍历并丢弃直到切片开始索引位置的所有元素。然后才开始一个个的返回元素,并直到切片结束索引位置。这里要着重强调的一点是 islice() 会消耗掉传入的迭代器中的数据。

### 8. 跳过可迭代对象的开始部分
使用`itertools.dropwhile()`，使用时,你给它传递一个函数对象和一个可迭代对象。返回在第一次函数对象返回False处，返回该位置后面的**所有**元素。

### 9. 排列组合的迭代
在刷leetcode的时候自己实现过排列组合生成器了，也看到了python solution中别人用到了这几个工具函数。
这里只提一下相关的工具函数：在`itertools`包中的`combinations`,`permutations`,`combinations_with_replacement`，其中组合函数允许传入一个额外参数表示需要几个元素的组合。
另外，如果只需要排列组合可能数目的话`scipy.special.perm`和`scipy.special.comb`。

### 10. 对序列进行带索引值的迭代
内置的`enumerate`。
注意：通常可以优雅的替代计数器

### 11. 同时迭代多个序列
zip啦。

注意1：一旦其中某个序列到底结尾,迭代宣告结束。如果想遍历到最长序列，使用`itertools.zip_longest`。
注意2：返回的是迭代器。
注意3：可以接受多于两个的列表。

### 12. 不同集合元素上的迭代：`itertools.chain`
使用 chain() 的一个常见场景是当你想对不同的集合中所有元素执行某些操作的时候。
itertools.chain() 接受一个或多个可迭代对象最为输入参数。然后创建一个迭代器,依次连续的返回每个可迭代对象中的元素。这种方式要比先将序列合并再迭代要
高效的多。

### 13. 创建数据处理管道
通过生成器


### 14. 展开嵌套的序列
注意 yield from 语句,它将 yield 操作代理到父生成器上去。语句 yield from it 简单的返回生成器 it 所产生的所有值。

```python
from collections import Iterable

def flatten(items, ignore_types=(str, bytes)):
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, ignore_types):
            yield from flatten(x)
        else:
            yield x

items = [1, 2, [3, 4, [5, 6], 7], 8]
# Produces 1 2 3 4 5 6 7 8
for x in flatten(items):
print(x)
```
要注意的一点是, yield from 在涉及到基于协程和生成器的并发编程中扮演着更加重要的角色。


### 15. 顺序迭代合并后的排序迭代对象
`heap.merge`
heapq.merge 可迭代特性意味着它不会立马读取所有序列。这就意味着你可以在非常长的序列中使用它,而不会有太大的开销。它仅仅是检查所有序列的开始部分并返回最小的那个,这个过程一直会持续直到所有输入序列中的元素都被遍历完。

### 16. 使用迭代器代替while无限循环
iter 函数一个鲜为人知的特性是它接受一个可选的 callable 对象和一个标记 (结尾) 值作为输入参数。当以这种方式使用的时候,它会创建一个迭代器,这个迭代器会不断调用 callable 对象直到返回值和标记值相等为止。这种特殊的方法对于一些特定的会被重复调用的函数很有效果,比如涉及到 I/O调用的函数。举例来讲,如果你想从套接字或文件中以数据块的方式读取数据,通常你得要不断重复的执行 read() 或 recv() ,并在后面紧跟一个文件结尾测试来决定是否终止。


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
