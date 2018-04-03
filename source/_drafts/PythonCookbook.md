---
title: PythonCookbook 
category: 读书笔记 
tags:
---

## 第一章

1. 解压序列赋值给多个变量

基本用法很简单，注意的是这种解压赋值可以用在任何可迭代对象上面,而不仅仅是列表或者元组。 包括字符串, 文件对象, 迭代器和生成器。
```python
a, b, c = "abc"
x1, x2, x3 = range(3) # 我也不知道这有啥用
```

2. 解压可迭代对象赋值给多个变量

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

3. 保留最后n个元素
```
def search(lines,   pattern,    history=5):
    previous_lines  =   deque(maxlen=history)
    for li  in  lines:
        if  pattern in  li:
            yield   li, previous_lines
        previous_lines.append(li)

with    open(r'./cookbook/somefile.txt')    as  f:
    for line,   prevlines   in  search(f,   'python',   5):
        for pline   in  prevlines:
            print(pline,    end='')
        print(line, end='')
        print('-'   *   20)
```

我们在写查询元素的代码时,通常会使用包含yield表达式的生成器函数,也就是我们上面示例代码中的那样。这样可以将搜索过程代码和使用搜索结果代码解耦。
在队列两端插入或删除元素时间复杂度都是O(1),而在列表的开头插入或删除元素的时间复杂度为O(N)。


4. 查找最大或最小的n个元素

`import heapq`，使用heapq进行堆结构的相关操作。

复习一下堆：堆需要几个基本操作（上浮 shift_up、下沉 shift_down、插入 push、弹出 pop、取顶 top、堆排序 heap_sort），其中上浮在插入时用到，下沉在弹出时用到。通常只取出最大或最小的几个元素时，堆结构会用到。

5. 优先级队列

这里需要用到一个trick就是元组之间也是可以比较的，只要元组之间对应的元素均可以比较。
因此实现一个优先级队列需要维护一个最小堆，然后堆元素为(-priority, index, val)。index是一个自增1的序号，保证先插入的元素先弹出。

```
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

6. 字典中的键映射多个值
没啥，就是以容器作为键。
有几个对于字典的小技巧，设置取值失败或设置初值的简易函数，比如setdefault和get，使用defaultdict代码会很简单，但是普通的访问会使得defaultdict新增数据。比如假设d = defaultdict(list)中没有键1，访问d[1]后会导致在d中创建一个{1: []}。

7. 字典排序
使用collections模块中的OrderedDict类，在迭代操作的时候它会保持元素被插入时的顺序,当你想要构建一个将来需要序列化或编码成其他格式的映射的时候,OrderedDict是非常有用的。比如,你想精确控制以JSON编码后字段的顺序,你可以先使用OrderedDict来构建这样的数据。

OrderedDict内部维护着一个根据键插入顺序排序的双向链表。每次当一个新的元素插入进来的时候,它会被放到链表的尾部。对于一个已经存在的键的重复赋值不会改变键的顺序。需要注意的是,一个OrderedDict的大小是一个普通字典的两倍,因为它内部维护着另外一个链表。

8. 字典的运算
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

9. 查找两字典的相同键

为了寻找两个字典的相同点,可以简单的在两字典的keys()或者items()方法返回结果上执行集合操作。直接通过`-`,`&`等操作符。keys方法返回字典键的一个视图，键视图的一个很少被了解的特性就是它们也支持集合操作,比如集合并、交、差运算。所以,如果你想对集合的键执行一些普通的集合操作,可以直接使用键视图对象而不用先将它们转换成一个set。字典的items()方法返回一个包含(键,值)对的元素视图对象。这个对象同样也支持集合操作,并且可以被用来查找两个字典有哪些相同的键值对。


10. 删除序列相同元素并保持顺序
这个其实就是leetcode中很常见的数组题，需要注意的是，如果写一个函数，可以用生成器来写，即用yield代替return

11. 命名切片
一般来讲,代码中如果出现大量的硬编码下标值会使得可读性和可维护性大大降低。比如,如果你回过来看看一年前你写的代码,你会摸着脑袋想那时候自己到底想干嘛啊。这里的解决方案是一个很简单的方法让你更加清晰的表达代码到底要做什么。内置的slice(start, stop, step)函数创建了一个切片对象(具有start，stop， step属性),可以被用在任何切片允许使用的地方。
可以使用切片对象的indices方法调整切片对象避免索引溢出。
```python
a = slice(5,50,2)
s = "helloworld"
s[a.indices(len(s))] # 'w','r','d'
```

12. 序列中出现最多的元素
collections.Counter类就是专门为这类问题而设计的,它甚至有一个有用的most_common(n)方法直接给了你答案。这个在leetcode类似题目的别人的Solution中已经见到过
作为输入, Counter 对象可以接受任意的 hashable 序列对象。在底层实现上,一个 Counter 对象就是一个字典,将元素映射到它出现的次数上。
Counter 对象在几乎所有需要制表或者计数数据的场合是非常有用的工具。在解决这类问题的时候你应该优先选择它,而不是手动的利用字典去实现。
Counter对象重载了运算符，两个Counter对象是可以进行数学运算的。


13. 通过某个关键字排序一个字典列表
复杂结构的排序我们之前就见到过，然而使用itemgetter()方式会比lambda表达式运行的稍微快点。因此,如果你对性能要求比较高的话就使用itemgetter()方式。
sorted接受一个callable对象作为排序键参数，itemgetter()函数就是负责创建这个 callable 对象的。itemgetter接受一个结构类型，基本等价于中括号操作，实际上可以传给itemgetter一个字典键名称,一个整形值或者任何能够传入一个对象的 __getitem__() 方法的值。如果你传入多个索引参数给itemgetter() ,它生成的 callable 对象会返回一个包含所有元素值的元组。


14. 排序不支持原生比较的对象
和上面差不多，不过这里所谓“对象”，和上面的区别就在于上面的排序键是字典中的某个键对应的值，所以使用operator.itemgeeter代替__getitem__方法，这里以对象的某个属性为排序键，实际上就是使用“点”操作符，所以用operator.attrgetter代替__getattribute__方法。
类似于itemgetter，attrgetter可以接受多个键参数，返回一个可比较的键元组。


15. 通过某个字段将记录分组
使用itertools中的groupby
groupby() 函数扫描整个序列并且查找连续相同值(或者根据指定key函数返回值相同)的元素序列。在每次迭代的时候,它会返回一个值和一个迭代器对象,这个迭代器对象可以生成元素值全部等于上面那个值的组中所有对象。因此一个非常重要的准备步骤是要根据指定的字段将数据排序。因为 groupby() 仅仅检查连续的元素,如果事先并没有排序完成的话,分组函数将得不到想要的结果。

16. 过滤序列元素
方法1: 列表推导
方法2：生成器表达式
方法3：filter，该函数创建一个迭代器
方法4：itertools.compress，输入两个序列，前者是数据序列，后者是指示序列，指示序列元素为True时，yield出数据序列中对应的元素。

17. 从字典中提取子集
直接字典推导

18. 映射名称到序列元素
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

19. 转化并同时计算数据
```python
nums = [1,2,3,4,5]
s = sum((x * x for x in nums))	# 显示的传递一个生成器表达式对象
s = sum(x * x for x in nums)	# 更加优雅的实现方式,省略了括号
s = sum([x * x for x in nums])	# 不好的方式：多一个步骤,先创建一个额外的列表。
```


20. 合并多个字典或映射
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

## 第四章 迭代器与生成器

### 章前tips

这一章有关迭代器。这里一定要区分迭代器和可迭代对象。range是惰性可迭代对象（当然了，迭代器也是惰性的），却不是迭代器。`iter(range(n))`才能获得range对象的迭代器，实际上使用iter可以从任何可迭代对象中获得迭代器，迭代器唯一能做的就是next直到StopIteration。所有的迭代器都是可迭代对象，意思是你可以从一个迭代器中得到一个迭代器，因此你可以遍历一个迭代器。
```
a = [1,2,3]
it1 = iter(a)
it2 = iter(it1)

# 其实it1和it2是同一个对象的两个引用

```
enumerate、zip、reversed和其他一些内置函数会返回迭代器。生成器（无论来自生成器函数还是生成器表达式）是一种创建迭代器的简单方法。注意下面的代码中，a不是一个元组，a是一个生成器对象。
```
a = (for i in range(10))
```

而range本身不是迭代器，因为无法对于range调用next函数。与迭代器不同的是，我们可以遍历一个 range 对象而不「消耗」它。range 对象在某种意义上是「惰性的」，因为它不会生成创建时包含的每个数字，相反，当我们在循环中需要的时候，它才将这些数字返回给我们。不像生成器，range 对象有长度，并且可以被索引。如果你想要一个 range 对象的描述，可以称它们为懒序列，range 是序列（如列表，元组和字符串），但并不包含任何内存中的内容，而是通过计算来回答问题。
```
a = range(10)

# 这一段代码可以多次执行
for i in a:
    print(a)
```
你可以询问他们是否包含某元素而不改变他们的状态。迭代器的特点是，当遍历它时，这些元素将从迭代器中被消耗掉，有时候这个特性可以派上用场（以特殊的方式处理迭代器）。
```
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

1. 手动遍历迭代器

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

2. 代理迭代
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

3. 使用生成器创建新的迭代模式
一个函数中需要有一个 yield 语句即可将其转换为一个生成器。跟普通函数不同的是,生成器只能用于迭代操作。为了使用这个函数,你可以用 for 循环迭代它或者使用其他接受一个可迭代对象的函数 (比如 sum() , list() 等)。
```python
def myrange(start, stop, increment):
    x = start
    while x < stop:
        yield x
        x += increment
```

4. 实现迭代器协议



5. 反向迭代
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

## 第七章 函数

1. 任意数量的位置参数和关键字参数

关键字参数必须全部在位置参数后面
```python
def anyargs(*args, **kwargs):
    print(args) # A tuple
    print(kwargs) # A dict
```

2. 强制使用关键字参数

```python
def recv(maxsize, *, block):
    'Receives a message'
    pass

recv(1024, True) # TypeError
recv(1024, block=True) # Ok
```

3. 给函数增加元信息

```python
def add(x:int, y:int) -> int:
    return x + y

# 函数注解只存储在函数的__annotations__属性中。
add.__annotations__
```

4. 返回多个值的函数

```python
# 这里重点就想记一下python中逗号是产生元组的原因
a = 1, 2
print(a)

# 还有就是单个元组的生成
b = (1)
print(b)

# 还有就是python的编码规范要求尽可能的少使用括号，除非用于改变优先级
```

5. 定义有默认参数的函数
默认参数要在参数列表的最后
```python
# 如果不想传递默认参数，只想查看参数是否传递进来
_no_value = object()
def spam(a, b=_no_value):
    if b is _no_value:
        print('No b value supplied')

```
**注意1：默认参数的值仅仅在函数定义的时候赋值一次。**
```python
x = 1
def fun(a, b=x):
    print(a+b)
fun(1)
x = 2
fun(2)
```

**注意2：默认参数尽量设置为不可变对象**

6. 定义匿名或内联函数

7. 匿名函数捕获变量值
lambda 表达式中的 x 是一个自由变量,在运行时绑定值,而不是定义时就绑定,这跟函数的默认值参数定义是不同的。因此,在调用这个 lambda 表达式的时候,x 的值是执行时的值。
```python
x = 10
f1 = lambda y: x+y

x = 20
f2 = lambda y: x+y

print(f1(1))
print(f2(2))
```

结合上面的知识，如果你想让某个匿名函数在定义时就捕获到值,可以将那个参数值定义成默认参数即可：

```python
x = 10
f1 = lambda y,x=x: x+y

x = 20
f1 = lambda y,x=x: x+y

print(f1(1))
print(f2(2))
```

**综合练习**
```python
funcs = [lambda x: x+n for n in range(5)]
for f in funcs:
    print(f(0))

funcs = [lambda x, n=n: x+n for n in range(5)]
for i in funcs:
    print(f(0))
```

8. 减少可调用对象的参数个数
**敲黑板：偏函数。** 使用functools.partial()固定一个函数的部分函数值。partial() 固定某些参数并返回一个新的 callable 对象。这个新的 callable接受未赋值的参数,然后跟之前已经赋值过的参数合并起来,最后将所有参数传递给原始函数。

在工作中的意义是让原本不兼容的代码一起工作。
```python
points = [ (1, 2), (3, 4), (5, 6), (7, 8) ]

import mat
def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.hypot(x2 - x1, y2 - y1)

pt = (4,3)
points.sort(key=partial(distance,pt))
print(points)

```
很多时候 partial() 能实现的效果,lambda 表达式也能实现。这样写也能实现同样的效果,不过相比而已会显得比较臃肿,对于阅读代码的人来讲也更加难懂。这时候使用 partial() 可以更加直观的表达你的意图 (给某些参数预先赋值)。

9. 将单方法的类转换为函数
任何时候只要你碰到需要给某个函数增加额外的状态信息的问题,都可以考虑使用闭包。相比将你的函数转换成一个类而言,闭包通常是一种更加简洁和优雅的方案。简单来讲,一个闭包就是一个函数,只不过在函数内部带上了一个额外的变量环境。闭包关键特点就是它会记住自己被定义时的环境。
```python
def printTemplate(template):
    def inner(**kwargs):
        print(template.format_map(kwargs))
    return inner

f = printTemplate("我叫{name},我今年{age}岁了")
f(name="张勇涛",age="24")

```

10. 带额外状态信息的回调函数



11. 内联回调函数


12. 访问闭包中定义的变量
