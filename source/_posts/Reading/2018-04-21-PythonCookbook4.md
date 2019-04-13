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

![](/img/python3_cookbook_cover.png)

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

<!-- more -->

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


一言以蔽之，生成器就是方便的迭代器，你只需要写一个yield语句，系统自动帮你实现迭代器协议。


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
使用`itertools.dropwhile`，使用时,你给它传递一个函数对象和一个可迭代对象。返回在第一次函数对象返回False处，返回该位置后面的**所有**元素。类似的还有`itertools.takewhile`，这个函数和`dropwhile`相反，作用是从第一个迭代器元素就开始返回，直到测试函数返回假值。

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
通过生成器可以方便的建立起数据处理的管道。下面分别使用`yield`实现了三个生成器，`filegen`接受一个（可以带通配符的）路径，返回的迭代器迭代满足通配符的所有文件；`linegen`接受一个文件名，迭代文件中的每一行；`wordgen`接受一个字符串，迭代其中的每一个单词。注意这三个生成器函数都是接受一个元素，返回多个元素。我们使用`iterator_concentrate`将两个可迭代对象组合起来。对于接受一个元素返回一个元素类型的数据处理管道，可以使用内建的`filter`、`map`和`itertools.filterfalse`进行生成。使用这些组件我们可以开发数据处理管道出来，在下一篇关于python数据流的文章中，还会介绍使用`yield from`以及协程计数连接数据处理管道的方法。这种方法的优点在于对于每一个子步骤都单独开发，耦合性很低，每一个代码片也有更高的复用的价值。

```python
from pathlib import Path
import glob
from collections import Generator, Callable, Iterable

def filegen(path_pattern) -> Generator:
    assert isinstance(path_pattern, str)
    for filename in glob.glob(path_pattern):
        path = Path(filename)
        if path.is_file():
            yield filename

def linegen(filepath) -> Generator:
    assert isinstance(filepath, str)
    with open(filepath) as f:
        yield from f

def wordgen(line) -> Generator:
    assert isinstance(line, str)
    for word in line.strip().split():
        yield word

def iterator_concentrate(it1, gf2):
    """
    it1 is a iterable object
    it2 is a generator function
    and every element from it1 is input of it2
    """
    assert isinstance(it1, Iterable)
    assert isinstance(gf2, Callable)
    for i in it1:
        yield from gf2(i)


if __name__ == "__main__":
    files = filegen("./*") # 文件生成器
    lines = iterator_concentrate(files, linegen) # 字符串生成器
    words = iterator_concentrate(lines, wordgen) # 单词生成器
    targetwords = filter(lambda s:s.startswith('a'), words) # 过滤器
    for w in targetwords:
        print(w)
```

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



### 15. 顺序迭代合并后的排序迭代对象
`heap.merge`
heapq.merge 可迭代特性意味着它不会立马读取所有序列。这就意味着你可以在非常长的序列中使用它,而不会有太大的开销。它仅仅是检查所有序列的开始部分并返回最小的那个,这个过程一直会持续直到所有输入序列中的元素都被遍历完。

```python
from memory_profiler import profile
from collections import Iterable
from itertools import chain
import heapq

@profile
def merge_seq(iters:list):
    for i in iters:
        assert isinstance(i, Iterable)

    for i in heapq.merge(*iters):
        pass
  
@profile
def merge_seq_bad(iters:list):
    for i in iters:
        assert isinstance(i, Iterable)

    for i in sorted(chain(*iters)):
        pass      

@profile
def main():
    l = []
    for i in range(1,100):
        l.append(list(range(i,i+100000, i)))

    print("start merge seq")
    merge_seq(l)
    print("start merge seq")
    merge_seq_bad(l)

if __name__ == "__main__":
    main()
```

可以在输出中看到，`heapq.merge`几乎不会增加内存。我们可以看一下python内部是怎么实现的，这里只贴出最核心的部分代码，并且把原理在注释中。注意到，函数内部的堆的大小与可迭代对象的个数成正比，而与可迭代对象的长度无关。具体实现可以参考[源码](https://github.com/python/cpython/blob/3.7/Lib/heapq.py)


### 16. 使用迭代器代替while无限循环
iter 函数一个鲜为人知的特性是它接受一个可选的 callable 对象和一个标记 (结尾) 值作为输入参数。当以这种方式使用的时候,它会创建一个迭代器,这个迭代器会不断调用 callable 对象直到返回值和标记值相等为止。这种特殊的方法对于一些特定的会被重复调用的函数很有效果,比如涉及到 I/O调用的函数。举例来讲,如果你想从套接字或文件中以数据块的方式读取数据,通常你得要不断重复的执行 read() 或 recv() ,并在后面紧跟一个文件结尾测试来决定是否终止。用这种方式写一个读文件的方法如下：
```python
filepath = "/etc/apt/sources.list"
with open(filepath) as f:
    for line in iter(f.readline().strip, ""):
        print(line)
```

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
