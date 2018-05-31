---
layout: post
date: 2018-04-24
title: Python Cookbook3 (9)元编程
category: 读书笔记
tags:
- reading
- python
keywords:
description:
---

### 1. 在函数上添加装饰器

### 2. 创建装饰器时保留函数元信息


### 3. 解除一个装饰器
前面好好的看的话，装饰器这个内容现在已经算比较简单了。`@wraps` 有一个重要特征是它能让你通过属性` __wrapped__ `直接访问被包装函数。`__wrapped__` 属性还能让被装饰函数正确暴露底层的参数签名信息。直接访问未包装的原始函数在调试、内省和其他函数操作时是很有用的。但是我们这里的方案仅仅适用于在包装器中正确使用了 @wraps 或者直接设置了 `__wrapped__` 属性的情况。如果有多个包装器，那么访问 `__wrapped__` 属性的行为是不可预知的，应该避免这样做。在Python3.3中，它会略过所有的包装层（只有3.3）。最后要说的是，并不是所有的装饰器都使用了`@wraps` ，因此这里的方案并不全部适用。特别的，内置的装饰器 `@staticmethod` 和 `@classmethod` 就没有遵循这个约定(它们把原始函数存储在属性 `__func__` 中)。


<!-- more -->


```python
import time
from functools import wraps

def timethis(func):
    '''
    Decorator that reports the execution time.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("function <{}> use time : {} sec".format(func.__name__, end-start))
        return result
    return wrapper

@timethis
def add2(a : int, b : int) -> int:
    """some doc should display
    """
    return a + b * 2

print(add2.__name__)
print(add2.__doc__)
print(add2.__annotations__)

from inspect import signature
print("---")
print(print(signature(add2)))
print("---")

print(add2(1,2))

# 通过访问__wrapped__解除装饰器
add2 = add2.__wrapped__
```

### 4. 带参数的装饰器
```python
from functools import wraps
def logged(level):
    """
    Add logging to a function. level is the logging
    level, name is the logger name, and message is the
    log message. If name and message aren't specified,
    they default to the function's module and name.
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("[{}]:{}".format(level, func.__name__))
            return func(*args, **kwargs)
        return wrapper
    return decorate

# 默认最低输出级别是WARN
@logged("DEBUG")
def add(x, y):
    return x + y

@logged("ERROR")
def spam():
    return "SPAM"

add(1,2)
spam()
```

### 5. 可自定义属性的装饰器
```python
# 这一小节的代码很棒
# 偏函数的应用有点意思，利用偏函数给函数绑定函数属性
from functools import wraps, partial
import logging
import sys
# Utility decorator to attach a function as an attribute of obj
def attach_wrapper(obj, func=None):
    if func is None:
        # 通过偏函数，是这个装饰器的行为类似于带参数的两层装饰器
        # 使用时也是很想两层装饰器，因为要先传入一个参数
        return partial(attach_wrapper, obj)
    setattr(obj, func.__name__, func)
    return func

def logged(level, message=None):
    '''
    Add logging to a function. level is the logging
    level, name is the logger name, and message is the
    log message. If name and message aren't specified,
    they default to the function's module and name.
    '''
    def decorate(func):
        logger = logging.getLogger("MyLogger")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)

        logmsg = message if message else func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.log(level, logmsg)
            return func(*args, **kwargs)


        # 不使用装饰器的方式
        def set_level(newlevel):
            nonlocal level
            level = newlevel
        def set_message(newmsg):
            nonlocal logmsg
            logmsg = newmsg

        wrapper.set_level = set_level
        wrapper.set_message = set_message

        # 使用装饰器的方式
        """
        Attach setter functions
        @attach_wrapper(wrapper)
        def set_level(newlevel):
            nonlocal level
            level = newlevel

        @attach_wrapper(wrapper)
        def set_message(newmsg):
            nonlocal logmsg
            logmsg = newmsg
        """

        return wrapper

    return decorate

# Example use
@logged(logging.INFO)
def add(x, y):
    return x + y

add(1,2)

add.set_level(logging.CRITICAL)
add.set_message("0 + 0 is forbidden")
add(0, 0)
```


### 6. 带可选参数的装饰器
两个重点参数和被被装饰函数放在同一层，也就是说这是一个单层装饰器。但是让参数作为带默认值的关键字参数。不加参数使用装饰器时，这就是一个单层装饰器。加上参数使用装饰器时，通过偏函数把装饰器自身不完全返回达到双层装饰器的效果。

### 7. 利用装饰器强制函数上的类型检查
重点在于inspect包的使用
1. 对是否是模块，框架，函数等进行类型检查。
2. 获取源码
3. 获取类或函数的参数的信息
4. 解析堆栈


### 8. 将装饰器定义为类的一部分
### 9. 将装饰器定义为类
需要描述器，跳过

### 10. 为类和静态方法提供装饰器
给类或静态方法提供装饰器是很简单的，不过要确保装饰器在 @classmethod 或 @staticmethod 之前。
问题在于 @classmethod 和 @staticmethod 实际上并不会创建可直接调用的对象， 而是创建特殊的**描述器**对象(参考8.9小节)。

### 11. 装饰器为被包装函数增加参数
这部分代码可以用到leetcode中，可选的函数调试功能。这种实现方案之所以行得通，在于强制关键字参数很容易被添加到接受 `*args` 和 `**kwargs` 参数的函数中。通过使用强制关键字参数，它被作为一个特殊情况被挑选出来，并且接下来仅仅使用剩余的位置和关键字参数去调用这个函数时，这个特殊参数会被排除在外。也就是说，它并不会被纳入到 `**kwargs` 中去。

12. 使用装饰器扩充类的功能
你想通过反省或者重写类定义的某部分来修改它的行为，但是你又不希望使用继承或元类的方式。这种情况可能是类装饰器最好的使用场景了。类装饰器通常可以作为其他高级技术比如混入或元类的一种非常简洁的替代方案。继承方案也行得通，但是为了去理解它，你就必须知道方法调用顺序、super() 以及其它8.7小节介绍的继承知识。某种程度上来讲，类装饰器方案就显得更加直观，并且它不会引入新的继承体系。它的运行速度也更快一些，因为他并不依赖 super() 函数。如果你系想在一个类上面使用多个类装饰器，那么就需要注意下顺序问题。

```python
def log_getattribute(cls):
# Get the original implementation
    orig_getattribute = cls.__getattribute__

    # Make a new definition
    def new_getattribute(self, name):
        print('getting:', name)
        return orig_getattribute(self, name)

    # Attach to the class and return
    cls.__getattribute__ = new_getattribute
    return cls

# Example use
@log_getattribute
class A:
    def __init__(self,x):
        self.x = x

    def spam(self):
        pass

a1 = A(1)
a1.x

a2 = A(2)
a2.spam()
```

### 13. 使用元类控制实例的创建

```python
# 示例代码实现了一个单例模式，但是怎么析构啊？
import sys
class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)
        
    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            print("initial")
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            print("return")
            return self.__instance


# Example
class Spam(metaclass=Singleton):
    def __init__(self):
        print('Creating Spam')

a = Spam()
b = Spam()
print(a is b)
```

### 14. 捕获类的属性定义顺序
本节一个关键点就是OrderedMeta元类中定义的 `__prepare__()` 方法。这个方法会在开始定义类和它的父类的时候被执行。它必须返回一个映射对象以便在类定义体中被使用到。



(未完待续)






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
