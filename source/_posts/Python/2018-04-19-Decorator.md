---
layout: post
date: 2018-04-19
title: python中的装饰器
category: python
tags: 
- python
keywords:
description:
---


## 原理：开头总要先说几句废话
装饰器是一种对**闭包**的使用方式。通过查看它的 func_closure 属性可以看出函数闭包特性。
真正理解装饰器有这么几个东西一定要透彻理解：
1. **变量作用域LEGB**
2. 函数是顶级对象

## 开始升级

### level 1：有用没用，先搞它出来一个
```python
def decorator(fn):
    def inner(n):
        return fn(n) + 1
    return inner

# the "@" statement is same as f = decorator(f)
@decorator
def f(n):
    return n + 1
```

## level 2: 使用装饰器，帅气的输出信息
```python
def wrap_with_prints(fn):
    # This will only happen when a function decorated
    # with @wrap_with_prints is defined
    print('print this when you decorate a function')
    def wrapped():
        # This will happen each time just before
        # the decorated function is called
        print('prepare to run %s' % fn.__name__)
        # Here is where the wrapper calls the decorated function
        fn()
        # This will happen each time just after
        # the decorated function is called
        print('done running %s' % fn.__name__)

    return wrapped

@wrap_with_prints
def func_to_decorate():
    print('some be wrapped')

func_to_decorate()
```

## level 3 : 哎呀被装饰的函数参数不一样我可怎么办呀
```python
def log_calls(fn):
    ''' Wraps fn in a function named "inner" that writes
    the arguments and return value to logfile.log '''
    def inner(*args, **kwargs):
        # Call the function with the received arguments and
        # keyword arguments, storing the return value

        out = fn(*args, **kwargs)

        # Write a line with the function name, its
        # arguments, and its return value to the log file
        print('{} called with args {} and kwargs {}, returning {}\n'.format(fn.__name__,  args, kwargs, out))

        # Return the return value
        return out
    return inner

@log_calls
def add(a,b):
    return a+b
add(1,2)
```


## level 4：装饰一个还不够，要装饰两次才最好
装饰器可以链式使用，但是一定要注意使用顺序
```python
def b(fn):
    return lambda s: '<b>{}</b>'.format(fn(s))

def em(fn):
    return lambda s: '<em>{}</em>'.format(fn(s))

@b
@em
def greet(name):
    return('Hello, {}!'.format(name))

print(greet("zyt"))
```




## level 5：装饰器也想要个属于人家自己的小参数嘛～
```python
def add_log_out(log_level):
    def wrapper(f):
        def return_f(*real_para):
            """inner doc
            """
            print("[{}]: {} with parameter {}".format(log_level, f.__name__, real_para))
            return f(*real_para)

        return return_f
    return wrapper

# same as "add = add_log_out("INFO")(add)"
@add_log_out("INFO")
def add(a,b):
    """return a + b
    """
    return a+b

print(add(1,2))
print(add.__name__)
print(add.__doc__)
```

## level 6：男人有了钱会变坏，函数有了装饰器却不会
```python
from functools import wraps
def add_log_out(log_level):
    def wrapper(f):
        @wraps(f)
        def return_f(*real_para):
            """inner doc
            """
            print("[{}]: {} with parameter {}".format(log_level, f.__name__, real_para))
            return f(*real_para)

        return return_f
    return wrapper

# same as "add = add_log_out("INFO")(add)"
@add_log_out("INFO")
def add(a,b):
    """return a + b
    """
    return a+b

print(add(1,2))
print(add.__name__)
print(add.__doc__)
```
## 参考：
1. [Python Decorators Overview](https://www.pythoncentral.io/python-decorators-overview/)
2. [简单 12 步理解 Python 装饰器](http://python.jobbole.com/85056/)
