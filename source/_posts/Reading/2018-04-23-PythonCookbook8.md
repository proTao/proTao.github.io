---
layout: post
date: 2018-04-23
title: Python Cookbook3 (8)类与对象
category: 读书笔记
tags:
- reading
- python
keywords:
description:
---




### 1. 改变对象的字符串显示
自定义`__repr__()` 和`__str__()`通常是很好的习惯,因为它能简化调试和实例输出。例如,如果仅仅只是打印输出或日志输出某个实例,那么程序员会看到实例更加详细与有用的信息。
__repr__()生成的文本字符串标准做法是需要让eval(repr(x))==x为真。
如果__str__()没有被定义,那么就会使用__repr__()来代替输出。

### 2. 自定义字符串的格式化
如果format时传入对象，会默认执行对象的__format__方法，如果在__format__函数中提供参数，那么在格式化字符串时可以通过冒号传入参数


```python
class A:
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return str(self.val)

    def __str__(self):
        return "this is my class A"

    def __format__(self,par):
        return "A({}) with parameter {}".format(self.val,par)

print("{:hello}".format(A(1)))
```


<!-- more -->


### 3. 让对象支持上下文管理协议
为了让一个对象兼容`with`语句,你需要实现`__enter__`和`__exit__`方法。
编写上下文管理器的主要原理是你的代码会放到`with`语句块中执行。 当出现 with 语句的时候，对象的`__enter__()`方法被触发，它返回的值(如果有的话)会被赋值给`as`声明的变量。然后，`with`语句块里面的代码开始执行。最后，`__exit__()`方法被触发进行清理工作。
在需要管理一些资源比如文件、网络连接和锁的编程环境中，使用上下文管理器是很普遍的。 这些资源的一个主要特征是它们必须被手动的关闭或释放来确保程序的正确运行。 
若果想要支持迭代的with语句，在自定义类中维护一个列表，用该列表存放当前“进入”的对象

### 4. 创建大量对象时节省内存方法
对于主要是用来当成简单的数据结构的类而言，你可以通过给类添加`__slots__`属性来极大的减少实例所占的内存。当你定义`__slots__`后，Python就会为实例使用一种更加紧凑的内部表示。实例通过一个很小的固定大小的数组来构建，而不是为每个实例定义一个字典，这跟元组或列表很类似。`在`__slots__`中列出的属性名在内部被映射到这个数组的指定小标上。
尽管slots看上去是一个很有用的特性，很多时候你还是得减少对它的使用冲动。Python的很多特性都依赖于普通的基于字典的实现。另外，定义了slots后的类不再支持一些普通类特性了，比如多继承。大多数情况下，你应该只在那些经常被使用到的用作数据结构的类上定义`slots`(如在程序中需要创建某个类的几百万个实例对象)。
关于`__slots__`的一个常见误区是它可以作为一个封装工具来防止用户给实例增加新的属性。
尽管使用slots可以达到这样的目的，但是这个并不是它的初衷。`__slots__`更多的是用来作为一个内存优化工具。

### 5. 在类中封装属性名
第一个约定是任何以单下划线_开头的名字都应该是内部实现。类似的，模块级别函数比如`sys._getframe()`在使用的时候就得加倍小心了。
使用双下划线开始会导致访问名称变成其他形式。这样重命名的目的是就是继承:这种属性通过继承是无法被覆盖的。
大多数而言，你应该让你的非公共名称以单下划线开头。但是，如果你清楚你的代码会涉及到子类， 并且有些内部属性应该在子类中隐藏起来，那么才考虑使用双下划线方案。
还有一点要注意的是，有时候你定义的一个变量和某个保留关键字冲突，这时候可以使用单下划线作为后缀。

### 6. 创建可管理的属性

```python
class Person:
    def __init__(self, first_name):
    	# 这里直接调用first_name的setter方法了
        self.first_name = first_name

    # 将first_name注册为property，并声明下面的函数是getter方法
    @property
    def first_name(self):
        return self._first_name

    # 对已注册的属性设置setter方法
    @first_name.setter
    def first_name(self, value):
        if not isinstance(value, str):
            raise TypeError('Expected a string')
        self._first_name = value

    # 对已注册的属性设置del方法
    @first_name.deleter
    def first_name(self):
        raise AttributeError("Can't delete attribute")

# 另一种方式
```
一个property属性其实就是一系列相关绑定方法的集合。如果你去查看拥有property的类， 就会发现property本身的fget、fset和fdel属性就是类里面的普通方法。
只有当你确实需要对attribute执行其他额外的操作的时候才应该使用到property。比如上面的例子就是再删除的时候禁止删除，在setter的时候进行类型检查。不要写这种没有做任何其他额外操作的property。 首先，它会让你的代码变得很臃肿，并且还会迷惑阅读者。 其次，它还会让你的程序运行起来变慢很多。 最后，这样的设计并没有带来任何的好处。

Properties还是一种定义动态计算attribute的方法。 这种类型的attributes并不会被实际的存储，而是在需要的时候计算出来。

```python
import math
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return math.pi * self.radius ** 2

    @property
    def diameter(self):
        return self.radius * 2

    @property
    def perimeter(self):
        return 2 * math.pi * self.radius
```

没有setter方法，所以无法被重新赋值。

### 7. 调用父类方法
假设B的父类是A，使用super().method()要比使用A.method()更优雅一些，另外避免了多继承的时候的重复调用父类方法。
对于你定义的每一个类，Python会计算出一个所谓的方法解析顺序(MRO)列表(通过对象的__mro__方法查看)。 这个MRO列表就是一个简单的所有基类的线性顺序表。而这个MRO列表的构造是通过一个*C3线性化算法*来实现的。当你使用 super() 函数时，Python会在MRO列表上继续搜索下一个类。 只要每个重定义的方法统一使用 super() 并只调用它一次， 那么控制流最终会遍历完整个MRO列表，每个方法也只会被调用一次。
```python
# 想重现一下super方法，但是失败了
class Base(object):
    def __init__(self):
        print("enter Base")
        print(self.su())
        print("leave Base")
    def su(self):
        print("object is {}, class is {}, mro is {}".format(self.__class__.__name__, self.__classname() ,self.__class__.mro()))
        
    def __classname(self):
        return "BASE"

class A(Base):
    def __init__(self):
        print("enter A")
        print(self.su())
        super().__init__()
        print("leave A")
    def __classname(self):
        return "A"
    def su(self):
        print("object is {}, class is {}, mro is {}".format(self.__class__.__name__, self.__classname() ,self.__class__.mro()))
   
    
class B(Base):
    def __init__(self):
        print("enter B")
        print(self.su())
        super().__init__()
        print("leave B")
    def __classname(self):
        return "B"
    def su(self):
        print("object is {}, class is {}, mro is {}".format(self.__class__.__name__, self.__classname() ,self.__class__.mro()))
  

class C(A, B):
    def __init__(self):
        print("enter C")
        print(self.su())
        super().__init__()
        print("leave C")
    def __classname(self):
        return "C"

    def su(self):
        print("object is {}, class is {}, mro is {}".format(self.__class__.__name__, self.__classname() ,self.__class__.mro()))
```

### 8. 子类中扩展property
super方法那里没有看明白

### 9. 创建新的类或实例属性
使用描述器，后续详细研究

### 10. 使用延迟计算属性
使用描述器类，后续详细研究

### 11. 简化数据结构的初始化
在一个基类中写一个公用的init函数
```python
class Structure1:
    # Class variable that specifies expected fields
    _fields = []

    def __init__(self, *args):
        if len(args) != len(self._fields):
            raise TypeError('Expected {} arguments'.format(len(self._fields)))
        # Set the arguments
        for name, value in zip(self._fields, args):
            setattr(self, name, value)
```
在上面的实现中我们使用了 setattr() 函数类设置属性值， 你可能不想用这种方式，而是想直接更新实例字典。尽管这也可以正常工作，但是当定义子类的时候问题就来了。 当一个子类定义了 __slots__ 或者通过property(或描述器)来包装某个属性， 那么直接访问实例字典就不起作用了。我们上面使用 setattr() 会显得更通用些，因为它也适用于子类情况。
缺点是在IDE中显示帮助函数不友好，因为看init函数只知道参数是args和kwargs，完全没有其他的信息，这一点在后面9.16节得到解决。

### 12. 定义接口或者抽象基类
抽象基类的一个主要用途是在代码中检查某些类是否为特定类型，实现了特定接口。
```python
from abc import ABCMeta, abstractmethod
class IStream(metaclass=ABCMeta):
    @abstractmethod
    def read(self, maxbytes=-1):
        pass

    @abstractmethod
    def write(self, data):
        pass
```
标准库中有很多用到抽象基类的地方。collections 模块定义了很多跟容器和迭代器(序列、映射、集合等)有关的抽象基类。 numbers 库定义了跟数字对象(整数、浮点数、有理数等)有关的基类。io 库定义了很多跟I/O操作相关的基类。

### 13. 实现数据模型的类型约束
使用描述器，跳过

### 14. 实现自定义容器
你想实现一个自定义的类来**模拟内置的容器类**功能，比如列表和字典。但是你不确定到底要实现哪些方法。collections 定义了很多抽象基类，当你想自定义容器类的时候它们会非常有用。 比如你想让你的类支持迭代，那就让你的类继承 collections.Iterable 即可。
这个接着12小节“定义接口或者抽象基类”的内容，




### 15. 属性的代理访问
需要注意的是，__getattr__() 对于大部分以双下划线(__)开始和结尾的属性并不适用。
有些细节需要注意。首先，__getattr__() 实际是一个后备方法，只有在属性不存在时才会调用。因此，如果代理类实例本身有这个属性的话，那么不会触发这个方法的。另外，__setattr__() 和 __delattr__() 需要额外的魔法来区分代理实例和被代理实例 _obj 的属性。一个通常的约定是只代理那些不以下划线 _ 开头的属性(代理类只暴露被代理类的公共属性)。
代理类有时候可以作为继承的替代方案。(为什么要做这种替代？)

```python
# A proxy class that wraps around another object, but
# exposes its public attributes
class Proxy:
    def __init__(self, obj):
        self._obj = obj

    # Delegate attribute lookup to internal obj
    def __getattr__(self, name):
        print('proxy getattr:', name)
        return getattr(self._obj, name)

    # Delegate attribute assignment
    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            print('setattr:', name, value)
            setattr(self._obj, name, value)

    # Delegate attribute deletion
    def __delattr__(self, name):
        if name.startswith('_'):
            super().__delattr__(name)
        else:
            print('delattr:', name)
            delattr(self._obj, name)

class Student:
    def __init__(self, name):
        self.name = name

    @property
    def name(self):
        print("Student name getter")
        return self._name

    @name.setter
    def name(self, name):
        print("Student name setter")
        self._name = name

    @name.deleter
    def name(self):
        print("Student name deleter")
        del self._name

    def show(self):
        print("my name is {}".format(self.name))


    pstu = Proxy(Student("gege"))
    print(pstu.name)
    pstu.show()
```

### 16. 实用类方法作为额外的对象构造器
```python
import time

class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    # Alternate constructor
    @classmethod
    def today(cls):
        t = time.localtime()
        return cls(t.tm_year, t.tm_mon, t.tm_mday)

    def __str__(self):
        return "{0[y]}-{0[m]}-{0[d]}".format({"d":self.day,"y":self.year,"m":self.month})

date = Date(1994,11,11)
today = Date.today()
print(date)

print(today)
```

### 17. 创建不调用init方法的实例
```python
"""暂时应该用不到。。。
"""
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

d1 = Date.__new__(Date)
d2 = Date(1000,10,10)
print(d1.__dict__)
print(d2.__dict__)
```python

### 8. 利用Mixins扩展类功能
复杂，跳过了

### 19. 实现状态对象或者状态机
```python
# 设计模式中有一种模式叫状态模式，这一小节算是一个初步入门！
class Connection:
    """普通方案，好多个判断语句，效率低下~~"""
    def __init__(self):
        self.state = 'CLOSED'

    def read(self):
        if self.state != 'OPEN':
            raise RuntimeError('Not open')
        print('reading')

    def write(self, data):
        if self.state != 'OPEN':
            raise RuntimeError('Not open')
        print('writing')

    def open(self):
        if self.state == 'OPEN':
            raise RuntimeError('Already open')
        self.state = 'OPEN'

    def close(self):
        if self.state == 'CLOSED':
            raise RuntimeError('Already closed')
        self.state = 'CLOSED'
```
这样写有很多缺点，首先是代码太复杂了，好多的条件判断。其次是执行效率变低，因为一些常见的操作比如read()、write()每次执行前都需要执行检查。
如果代码中出现太多的条件判断语句的话，代码就会变得难以维护和阅读。
这里的解决方案是将每个状态抽取出来定义成一个类。
每个状态对象都只有静态方法，并没有存储任何的实例属性数据。
实际上，所有状态信息都只存储在 Connection 实例中。
在基类中定义的 NotImplementedError 是为了确保子类实现了相应的方法。而真正的动作定义在了状态类中。

### 20. 通过字符串调用对象方法
通过方法名称字符串来调用方法通常出现在需要模拟 case 语句或实现访问者模式的时候。
方法一：getattr
方法二：methodcaller

### 21. 实现访问者模式
涉及到设计模式。。也先跳过吧

### 22. 不用递归实现访问者模式
跳过

### 23. 循环引用数据结构的内存管理
使用weakref包
本质来讲，弱引用就是一个对象指针，它不会增加它的引用计数。
```python
class Data:
    def __init__(self, name):
        self.name = name
    def __del__(self):
        print('Data.__del__:{}'.format(self.name))

# Node class involving a cycle
class Node:
    def __init__(self, name):
        self.data = Data(name)
        self.parent = None
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

a = Data("a")
del a

a = Node("parent")
a.add_child(Node("child"))
del a

print("end")
```
发现Node出现循环技术，是在程序结束时才会清除，即del无法清除内存
当然可以手动使用gc.collect()进行垃圾回收    

### 24. 让类支持比较操作
需要实现几个比较操作的魔术方法，这个没啥的但是每个都写一遍就很困难
装饰器 functools.total_ordering 就是用来简化这个处理的。
使用它来装饰一个类，你只需定义一个 __eq__() 方法，外加其他方法(lt, le, gt, or ge)中的一个即可。
然后装饰器会自动为你填充其它比较方法。


### 25. 创建缓存实例
```python
import weakref
class CachedSpamManager:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()

    def get_spam(self, name):
        if name not in self._cache:
            temp = Spam._new(name)  # Modified creation
            self._cache[name] = temp
        else:
            temp = self._cache[name]
        return temp

    def clear(self):
            self._cache.clear()

class Spam:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("Can't instantiate directly")

    # Alternate constructor
    @classmethod
    def _new(cls, name):
        self = cls.__new__(cls)
        self.name = name
        return self

manager = CachedSpamManager()
spam1 = manager.get_spam('a')
spam2 = manager.get_spam('b')
spam3 = manager.get_spam('a')
print(spam1 is spam3)
print(list(manager._cache))
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
