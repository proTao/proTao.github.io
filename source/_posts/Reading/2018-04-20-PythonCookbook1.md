---
layout: post
date: 2018-04-20
title: Python Cookbook3 (1)数据结构与算法
category: 读书笔记
tags:
- reading
- python
keywords: 
description: 
---

![](/img/python3_cookbook_cover.png)

### 1. 解压序列赋值给多个变量
基本用法很简单，注意的是这种解压赋值可以用在任何可迭代对象上面,而不仅仅是列表或者元组。 包括字符串, 文件对象, 迭代器和生成器。
```python
a, b, c = "abc"
x1, x2, x3 = range(3) # 我也不知道这有啥用
```

### 2. 解压可迭代对象赋值给多个变量
扩展的迭代解压语法是专门为解压不确定个数或任意个数元素的可迭代对象而设计的。星号表达式在迭代元素为可变长元组的序列时是很有用的。星号表达式一定可以得到一个列表，即使没有元素分配给他。
```python
data = (
    ('scores', 98,97,99),
    ('names', 'tom','jack'),
    ('ages', )
)

for tag, *content in data:
    print("{}:{}".format(tag, content))
```

<!-- more -->

### 3. 保留最后n个元素
```python
def search(lines,   pattern,    history=5):
    previous_lines  =   deque(maxlen=history)
    for li  in  lines:
        if  pattern in  li:
            yield   li, previous_lines
        previous_lines.append(li)

with open(r'./cookbook/somefile.txt')    as  f:
    for line,   prevlines   in  search(f,   'python',   5):
        for pline   in  prevlines:
            print(pline,    end='')
        print(line, end='')
        print('-'   *   20)
```
我们在写查询元素的代码时,通常会使用包含yield表达式的生成器函数,也就是我们上面示例代码中的那样。这样可以将搜索过程代码和使用搜索结果代码解耦。
在队列两端插入或删除元素时间复杂度都是O(1),而在列表的开头插入或删除元素的时间复杂度为O(N)。

###  4. 查找最大或最小的n个元素
`import heapq`，使用heapq进行堆结构的相关操作。
复习一下堆：堆需要几个基本操作（上浮 shift_up、下沉 shift_down、插入 push、弹出 pop、取顶 top、堆排序 heap_sort），其中上浮在插入时用到，下沉在弹出时用到。通常只取出最大或最小的几个元素时，堆结构会用到。

### 5. 优先级队列
这里需要用到一个trick就是元组之间也是可以比较的，只要元组之间对应的元素均可以比较。
因此实现一个优先级队列需要维护一个最小堆，然后堆元素为(-priority, index, val)。index是一个自增1的序号，保证先插入的元素先弹出。
```python
# 原书中使用类来实现，但是后文提到过，如果只有少量的数据需要存储，可以使用闭包来实现
def makeHeap():
    data = []
    def top():
        try:
            res = data[0]
            return res
        except Exception:
            return None
    def res():
        pass
    def push(e):
        heapq.heappush(data, e)
    def pop():
        return heapq.heappop(data)
    def show():
        print(data)
    res.top = top
    res.push = push
    res.pop = pop
    res.show = show
    return res
```

### 6. 字典中的键映射多个值
没啥，就是以容器作为键。
有几个对于字典的小技巧，设置取值失败或设置初值的简易函数，比如setdefault和get，使用defaultdict代码会很简单，但是普通的访问会使得defaultdict新增数据。比如假设d = defaultdict(list)中没有键1，访问d[1]后会导致在d中创建一个{1: []}。

### 7. 字典排序
使用collections模块中的OrderedDict类，在迭代操作的时候它会保持元素被插入时的顺序,当你想要构建一个将来需要序列化或编码成其他格式的映射的时候,OrderedDict是非常有用的。比如,你想精确控制以JSON编码后字段的顺序,你可以先使用OrderedDict来构建这样的数据。
OrderedDict内部维护着一个根据键插入顺序排序的双向链表。每次当一个新的元素插入进来的时候,它会被放到链表的尾部。对于一个已经存在的键的重复赋值不会改变键的顺序。需要注意的是,一个OrderedDict的大小是一个普通字典的两倍,因为它内部维护着另外一个链表。

### 8. 字典的运算
如果你在一个字典上执行普通的数学运算,你会发现它们仅仅作用于键,而不是值。
例如求最大值：思路是使用zip
```python
prices={
	'ACME':	45.23,
	'AAPL':	612.78,
	'IBM':	205.55,
	'HPQ':	37.20,
	'FB':	10.75
}

prices_sorted = sorted(zip(prices.values(), prices.keys()))//排列或其他类似的操作

```

### 9. 查找两字典的相同键
为了寻找两个字典的相同点,可以简单的在两字典的keys()或者items()方法返回结果上执行集合操作。直接通过`-`,`&`等操作符。keys方法返回字典键的一个视图，键视图的一个很少被了解的特性就是它们也支持集合操作,比如集合并、交、差运算。所以,如果你想对集合的键执行一些普通的集合操作,可以直接使用键视图对象而不用先将它们转换成一个set。字典的items()方法返回一个包含(键,值)对的元素视图对象。这个对象同样也支持集合操作,并且可以被用来查找两个字典有哪些相同的键值对。


### 10. 删除序列相同元素并保持顺序
这个其实就是leetcode中很常见的数组题，需要注意的是，如果写一个函数，可以用生成器来写，即用yield代替return

### 11. 命名切片
一般来讲,代码中如果出现大量的硬编码下标值会使得可读性和可维护性大大降低。比如,如果你回过来看看一年前你写的代码,你会摸着脑袋想那时候自己到底想干嘛啊。这里的解决方案是一个很简单的方法让你更加清晰的表达代码到底要做什么。内置的slice(start, stop, step)函数创建了一个切片对象(具有start，stop， step属性),可以被用在任何切片允许使用的地方。
可以使用切片对象的indices方法调整切片对象避免索引溢出。
```python
a = slice(5,50,2)
s = "helloworld"
s[a.indices(len(s))] # 'w','r','d'
```

### 12. 序列中出现最多的元素
collections.Counter类就是专门为这类问题而设计的,它甚至有一个有用的most_common(n)方法直接给了你答案。这个在leetcode类似题目的别人的Solution中已经见到过
作为输入, Counter 对象可以接受任意的 hashable 序列对象。在底层实现上,一个 Counter 对象就是一个字典,将元素映射到它出现的次数上。
Counter 对象在几乎所有需要制表或者计数数据的场合是非常有用的工具。在解决这类问题的时候你应该优先选择它,而不是手动的利用字典去实现。
Counter对象重载了运算符，两个Counter对象是可以进行数学运算的。


### 13. 通过某个关键字排序一个字典列表
复杂结构的排序我们之前就见到过，然而使用itemgetter()方式会比lambda表达式运行的稍微快点。因此,如果你对性能要求比较高的话就使用itemgetter()方式。
sorted接受一个callable对象作为排序键参数，itemgetter()函数就是负责创建这个 callable 对象的。itemgetter接受一个结构类型，基本等价于中括号操作，实际上可以传给itemgetter一个字典键名称,一个整形值或者任何能够传入一个对象的 __getitem__() 方法的值。如果你传入多个索引参数给itemgetter() ,它生成的 callable 对象会返回一个包含所有元素值的元组。


### 14. 排序不支持原生比较的对象
和上面差不多，不过这里所谓“对象”，和上面的区别就在于上面的排序键是字典中的某个键对应的值，所以使用operator.itemgeeter代替__getitem__方法，这里以对象的某个属性为排序键，实际上就是使用“点”操作符，所以用operator.attrgetter代替__getattribute__方法。
类似于itemgetter，attrgetter可以接受多个键参数，返回一个可比较的键元组。


### 15. 通过某个字段将记录分组
使用itertools中的groupby
groupby() 函数扫描整个序列并且查找连续相同值(或者根据指定key函数返回值相同)的元素序列。在每次迭代的时候,它会返回一个值和一个迭代器对象,这个迭代器对象可以生成元素值全部等于上面那个值的组中所有对象。因此一个非常重要的准备步骤是要根据指定的字段将数据排序。因为 groupby() 仅仅检查连续的元素,如果事先并没有排序完成的话,分组函数将得不到想要的结果。

### 16. 过滤序列元素
方法1: 列表推导
方法2：生成器表达式
方法3：filter，该函数创建一个迭代器
方法4：itertools.compress，输入两个序列，前者是数据序列，后者是指示序列，指示序列元素为True时，yield出数据序列中对应的元素。

### 17. 从字典中提取子集
直接字典推导

### 18. 映射名称到序列元素
意义在于避免代码中的magic number，和前面提到过得将切片命名是一样的道理，即给下标命名。
collections.namedtuple() 函数通过使用一个普通的元组对象来帮你解决这个问题。这个函数实际上是一个返回Python中标准元组类型子类的一个**工厂方法**。你需要传递一个类型名和你需要的字段给它,然后它就会返回一个类,你可以初始化这个类,为你定义的字段传递值等。尽管namedtuple的实例看起来像一个普通的类实例,但是它跟元组类型是可交换的,支持所有的普通元组操作,比如索引和解压。
```python
Record = namedtuple("Person", ['name', 'age', 'gender','lover'])
p1 = Record("Zhang Yongtao",24,'m','Huang Ying')
print(p1[0])
print(p1.name)

# trick:参数的解压
r = ("Huang Ying",24,'f','Zhang Yongtao')
p2 = Record(*r)

r = dict(name="Sun Qi",age=23,gender='m',lover=None)
p3 = Record(**r)
```

命名元组另一个用途就是作为字典的替代,因为字典存储需要更多的内存空间。如果你需要构建一个非常大的包含字典的数据结构,那么使用命名元组会更加高效。但是需要注意的是,不像字典那样,一个命名元组是不可更改的。

如果你真的需要改变然后的属性,那么可以使用命名元组实例的 _replace() 方法, 它会创建一个全新的命名元组并将对应的字段用新的值取代。
最后要说的是,如果你的目标是定义一个需要更新很多实例属性的高效数据结构,那么命名元组并不是你的最佳选择。这时候你应该考虑定义一个包含 __slots__ 方法的类。
```python
p3 = p3._replace(lover="Chen Zhenguo") # 返回新的对象，因为nametuple不可变
```

### 19. 转化并同时计算数据
```python
nums = [1,2,3,4,5]
s = sum((x * x for x in nums))	# 显示的传递一个生成器表达式对象
s = sum(x * x for x in nums)	# 更加优雅的实现方式,省略了括号
s = sum([x * x for x in nums])	# 不好的方式：多一个步骤,先创建一个额外的列表。
```


### 20. 合并多个字典或映射
现在假设你必须在两个字典中执行查找操作(比如先从a中找,如果找不到再在b中找)。一个非常简单扼要解决方案就是使用collections模块中的ChainMap类。
```python
a = {'x': 1, 'z': 3}
b = {'y': 2, 'z': 4}

from collections import ChainMap
c = ChainMap(a,b)
print(c['x'])	# Outputs 1 (from a)
print(c['y'])	# Outputs 2 (from b)
print(c['z'])	# Outputs 3 (from a)
```

一个ChainMap接受多个字典并将它们在逻辑上变为一个字典。然后,这些字典并不是真的合并在一起了,ChainMap类只是在内部创建了一个容纳这些字典的列表并重新定义了一些常见的字典操作来遍历这个列表。大部分字典操作都是可以正常使用的。
因此，如果出现重复键,那么第一次出现的映射值会被返回。对于字典的更新或删除操作总是影响的是列表中第一个字典。

作为ChainMap的替代,你可能会考虑使用update()方法将两个字典合并。这样也能行得通,但是它需要你创建一个完全不同的字典对象(或者是破坏现有字典结构)。同时,如果原字典做了更新,这种改变不会反应到新的合并字典中去。ChianMap使用原来的字典,它自己不创建新的字典。







---

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
