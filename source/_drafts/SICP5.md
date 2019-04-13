---
layout: post
date: 2019-04-11
title: SICP5
category: python
tags: 
- python
keywords:
description:
---

![生成器迭代器的关系](/img/generator.png)

## 一、python中的迭代器

首先要区分开迭代器和可迭代对象，前者是指实现了`__next__`和`StopIteration`迭代器协议的python对象，后者是指可以使用`iter`得到其迭代器的对象。比如，`iter(range(n))`可以获得range对象的迭代器，实际上使用iter可以从任何可迭代对象中获得迭代器，迭代器唯一能做的就是next直到StopIteration。所有的迭代器都是可迭代对象，意思是你可以从一个迭代器中得到一个迭代器，因此你可以遍历一个迭代器。通常对迭代器使用`iter`方法返回的是该迭代器自身。

```python
a = [1,2,3]

it1 = iter(a)
it2 = iter(it1)# 其实it1和it2是同一个对象的两个引用

```
enumerate、zip、reversed和其他一些内置函数会返回迭代器。生成器（无论来自生成器函数还是生成器表达式）是一种创建迭代器的简单方法，python对根据`yield`关键字自动实现迭代器协议。注意下面的代码中，a不是一个元组，a是一个生成器对象。生成器表达式是列表推倒式的生成器版本，看起来像列表推导式，但是它返回的是一个生成器对象而不是列表对象。看到这里可能有点乱，这些对象的具体关系可以看文章的封面图，自己想一下`range`对象在图的什么位置？（图片来源于：[Iterables vs. Iterators vs. Generators](https://nvie.com/posts/iterators-vs-generators/)）

<!-- more -->

```python
a = (i for i in range(10))
```

`range`（当然了，迭代器也是惰性的），却不是迭代器，因为迭代器中的元素是消耗的，然后`range`对象却不是，而且`range`对象还实现了长度和下标的方法，因此更准确的来看，`range`更像是一个列表，只不过是惰性求值的。因为`range`本身不是迭代器，因为无法对于`range`调用`range`函数。与迭代器不同的是，我们可以遍历一个 range 对象而不「消耗」它。range 对象在某种意义上是「惰性的」，因为它不会生成创建时包含的每个数字，相反，当我们在循环中需要的时候，它才将这些数字返回给我们。如果你想要一个 range 对象的描述，可以称它们为懒序列，range 是序列（如列表，元组和字符串），但并不包含任何内存中的内容，而是通过实时计算来返回需要的值。迭代器的特点是，当遍历它时，这些元素将从迭代器中被消耗掉，有时候这个特性可以派上用场（以特殊的方式处理迭代器）。




```python
a = range(10)

# 这一段代码可以多次执行
for i in a:
    print(a)

print(5 in a)
print(5 in a)

b = iter([1,2,3])

print(2 in b)
print(2 in b)
```


迭代器不需要事先准备好整个迭代过程中的所有元素，仅仅在迭代到某个元素时才计算该元素，而在这之前或之后，元素可以不存在或销毁，因此迭代器是一种重要的**节省内存**的方式，这一点在无限流数据中体现的更为明显。迭代器另外的好处是，提供一种方法顺序访问一个聚合对象中各个元素, 而又无须暴露该对象的内部表示，这种好处本身来源于python中所谓的“迭代器协议”实际上是实现了设计模式中的迭代器模式，这种设计模式用于以不同的方式来遍历整个整合对象，把在元素之间游走的责任交给迭代器，而不是聚合对象。使用迭代器模式，可以帮助我们：(1)访问一个聚合对象的内容而无须暴露它的内部表示。 (2)需要为聚合对象提供多种遍历方式。(3)为遍历不同的聚合结构提供一个统一的接口。迭代器模式的类图如下：

![迭代器模式类图](/img/iterator_pattern_uml_diagram.jpg)


## 二、设计一个惰性序列

这里我们设计一个惰性求值的懒序列，主要思想与代码参考《SICP-python描述》一书。如果让我们设计一个`range`对象，最简单的设计思想就是维护上下界与`__iter__`接口，求指定下标的值可以直接用`start+index*step`得到，长度也可以使用`(end-start)/step`求得。但是如果是更复杂的懒序列呢？比如我想实现一个求出下一个素数的懒序列该如何实现？下面的设计中使用递归的思路完成对懒序列的实现，可以在其中发现函数式编程思想的影子。下面的`Stream`类使用**延时计算**的方法模拟了一个流对象，然而并没有显式的直接维护其局部状态，并不断地对其进行更新或者赋值，我们要做的只维护当前值与计算下一个值的方法，这种结构无法随机访问，但是非常适合顺序访问，因此也很容易实现它的迭代器接口。



```python
class Stream(object):
    """A lazily computed recursive list."""
    def __init__(self, first, compute_rest, empty=False):
        self.first = first
        self._compute_rest = compute_rest
        self.empty = empty
        self._rest = None
        self._computed = False
    @property
    def rest(self):
        """Return the rest of the stream, computing it if necessary."""
        assert not self.empty, 'Empty streams have no rest.'
        if not self._computed:
            print("computing")
            self._rest = self._compute_rest()
            self._computed = True
        return self._rest
    def __repr__(self):
        if self.empty:
            return '<empty stream>'
        if self._rest:
            return 'Stream({0}, {1})'.format(repr(self.first), repr(self._rest))
        else:
            return 'Stream({0}, {1})'.format(repr(self.first), repr(self._compute_rest))
Stream.empty = Stream(None, None, True)

def make_next_integer():
    i = 1
    def inner():
        nonlocal i
        i += 1
        return Stream(i, inner)
    return inner

pos_stream = Stream(1, make_next_integer())

def map_stream(fn, s):
    if s.empty:
        return s
    def compute_rest():
        return map_stream(fn, s.rest)
    return Stream(fn(s.first), compute_rest)


def filter_stream(fn, s):
    if s.empty:
        return s
    def compute_rest():
        return filter_stream(fn, s.rest)
    if fn(s.first):
        return Stream(s.first, compute_rest)
    return compute_rest()

def truncate_stream(s, k):
    if s.empty or k == 0:
        return Stream.empty
    def compute_rest():
        return truncate_stream(s.rest, k-1)
    return Stream(s.first, compute_rest)

def stream_to_list(s):
    r = []
    while not s.empty:
        r.append(s.first)
        s = s.rest
    return r
    
def primes(pos_stream):
    def not_divible(x):
        return x % pos_stream.first != 0
    def compute_rest():
        return primes(filter_stream(not_divible, pos_stream.rest))
    return Stream(pos_stream.first, compute_rest)
```

## 三、构建数据处理管道

我们使用协程,引入了一种不同的方式来解构复杂的计算。它是一种针对有序数据的任务处理方式。就像子过程那样,协程会计算复杂计算的一小步。但是,在使用协程时,没有主函数来协调结果。反之,协程会自发链接到一起来组成流水线。可能有一些协程消耗输入数据,并把它发送到其它协程。也可能有一些协程,每个都对发送给它的数据执行简单的处理步骤。最后可能有另外一些协程输出最终结果。

协程和子过程的差异是概念上的:子过程在主函数中位于下级,但是协程都是平等的,它们协作组成流水线,不带有任何上级函数来负责以特定顺序调用它们。

```python
def gen_str(s):
    """a string generator, using s as a seed
    """
    salt = "usbdhcgsta"
    for i in range(10):
        s = s[1:] + salt[i]
        yield s

def producer_str(start, next_str, next_coroutine):
    for s in next_str(start):
        print("gen_str -> {} : {}".format(next_coroutine.__name__, s))
        next_coroutine.send(s)
    next_coroutine.close()

def filter_start(start, next_coroutine):
    print("start [filter_start]")
    try:
        while True:
            s = (yield)
            print("[filter receive] : ", s)
            if s.startswith(start):
                print("[filter -> {}]:{}".format(next_coroutine.__name__, s))
                next_coroutine.send(s)
    except GeneratorExit:
        next_coroutine.close()
        print("[filter_start] done")

def consumer_print():
    print("start [consumer_print]")
    try:
        while True:
            s = (yield)
            print("->[consumer_print] : {}".format(s))
    except GeneratorExit:
        print("[consumer_print] done!")

myprinter = consumer_print()
next(myprinter) # start it

myfilter = filter_start("p", myprinter)
next(myfilter) # start it

producer_str("apple", gen_str, myfilter)
"""输出为：
start [consumer_print]
start [filter_start]
gen_str -> filter_start : ppleu
[filter receive] :  ppleu
[filter -> consumer_print]:ppleu
->[consumer_print] : ppleu
gen_str -> filter_start : pleus
[filter receive] :  pleus
[filter -> consumer_print]:pleus
->[consumer_print] : pleus
gen_str -> filter_start : leusb
[filter receive] :  leusb
gen_str -> filter_start : eusbd
[filter receive] :  eusbd
gen_str -> filter_start : usbdh
[filter receive] :  usbdh
gen_str -> filter_start : sbdhc
[filter receive] :  sbdhc
gen_str -> filter_start : bdhcg
[filter receive] :  bdhcg
gen_str -> filter_start : dhcgs
[filter receive] :  dhcgs
gen_str -> filter_start : hcgst
[filter receive] :  hcgst
gen_str -> filter_start : cgsta
[filter receive] :  cgsta
"""
```

注意后续有其他处理协程的函数内部，需要负责将后续的携程关闭，否则后续的协程会一直等待。


## 参考文章
[廖雪峰：异步IO](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/00143208573480558080fa77514407cb23834c78c6c7309000)
详见[Python：range 对象并不是迭代器](https://blog.csdn.net/IaC743nj0b/article/details/79547122)
