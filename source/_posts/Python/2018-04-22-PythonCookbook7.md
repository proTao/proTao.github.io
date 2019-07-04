---
layout: post
date: 2018-04-22
title: Python Cookbook3 (7)函数
category: 读书笔记
tags:
- reading
- python
keywords:
description:
---

![](/img/cover/python3_cookbook_cover.png)

### 1. 任意数量的位置参数和关键字参数

关键字参数必须全部在位置参数后面
```python
def anyargs(*args, **kwargs):
    print(args) # A tuple
    print(kwargs) # A dict
```

### 2. 强制使用关键字参数
```python
def recv(maxsize, *, block):
    'Receives a message'
    pass

recv(1024, True) # TypeError
recv(1024, block=True) # Ok
```

<!-- more -->

### 3. 给函数增加元信息

```python
def add(x:int, y:int) -> int:
    return x + y

# 函数注解只存储在函数的__annotations__属性中。
add.__annotations__
```

### 4. 返回多个值的函数

```python
# 这里重点就想记一下python中逗号是产生元组的原因
a = 1, 2
print(a)

# 还有就是单个元组的生成
b = (1)
print(b)

# 还有就是python的编码规范要求尽可能的少使用括号，除非用于改变优先级
```

### 5. 定义有默认参数的函数
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

### 6. 定义匿名或内联函数

### 7. 匿名函数捕获变量值
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

### 8. 减少可调用对象的参数个数
**敲黑板：偏函数。** 使用functools.partial()固定一个函数的部分函数值。partial() 固定某些参数并返回一个新的 callable 对象。这个新的 callable接受未赋值的参数,然后跟之前已经赋值过的参数合并起来,最后将所有参数传递给原始函数。

在工作中的意义是让原本不兼容的代码一起工作。
```python
points = [ (1, 2), (3, 4), (5, 6), (7, 8) ]

import math
def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.hypot(x2 - x1, y2 - y1)

pt = (4,3)
points.sort(key=partial(distance,pt))
print(points)

```
很多时候 partial() 能实现的效果,lambda 表达式也能实现。这样写也能实现同样的效果,不过相比而已会显得比较臃肿,对于阅读代码的人来讲也更加难懂。这时候使用 partial() 可以更加直观的表达你的意图 (给某些参数预先赋值)。

### 9. 将单方法的类转换为函数
任何时候只要你碰到需要给某个函数增加额外的状态信息的问题,都可以考虑使用闭包。相比将你的函数转换成一个类而言,闭包通常是一种更加简洁和优雅的方案。简单来讲,一个闭包就是一个函数,只不过在函数内部带上了一个额外的变量环境。闭包关键特点就是它会记住自己被定义时的环境。
```python
def printTemplate(template):
    def inner(**kwargs):
        print(template.format_map(kwargs))
    return inner

f = printTemplate("我叫{name},我今年{age}岁了")
f(name="张勇涛",age="24")

```

### 10. 带额外状态信息的回调函数
其实就是闭包的应用，通过闭包保存状态。


### 11. 内联回调函数
没太看懂

### 12. 访问闭包中定义的变量
通常来讲,闭包的内部变量对于外界来讲是完全隐藏的。但是,你可以通过编写访问函数并将其作为函数属性绑定到闭包上来实现这个目的。
```python
def sample():
    n = 0

    # Closure function
    def func():
        print('n=', n)

    # Accessor methods for n
    def get_n():
        return n

    def set_n(value):
        nonlocal n
        n = value
        # Attach as function attributes
        
    func.get_n = get_n
    func.set_n = set_n

    return func
```
nonlocal 声明可以让我们编写函数来修改内部变量的值。其次,函数属性允许我们用一种很简单的方式将访问方法绑定到闭包函数上,这个跟实例方法很像 (尽管并没有定义任何类)。

```python
import sys
class ClosureInstance:
    def __init__(self, locals=None):
        if locals is None:
            locals = sys._getframe(1).f_locals
            # Update instance dictionary with callables
            self.__dict__.update((key,value) for key, value in locals.items() if callable(value))
            
        # Redirect special methods
        def __len__(self):
            return self.__dict__['__len__']()
            
# Example use
def Stack():
    items = []
    def push(item):
        items.append(item)
    def pop():
        return items.pop()
    def __len__():
        return len(items)
              
    return ClosureInstance()
```
闭包的方案运行起来要快大概 8%,大部分原因是因为对实例变量的简化访问,闭包更快是因为不会涉及到额外的 self 变量。


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
