---
layout: post
date: 2019-04-14
title: python中的字节码对象初探
category: python
tags: 
- python
keywords:
description:
---

![](/img/python_cover1.jpg)

## 一、虚拟机执行环境

在上一篇[关于字节码对象的文章](https://protao.github.io/2019/04/14/Python-2019-04-14-PyCodeObject/)中，展示了python源码被编译为字节码的结果。得到的`PyCodeObject`只是静态分析得到的对象。接下来，Python虚拟机会接管该对象并一次读取每一行字节码并在上下文环境中执行字节码序列。我们一直把“名字空间”和“上下文环境”挂在嘴边，这两者却不是完全等价的。名字空间是上下文环境中的关键数据，但却不是全部，在实现一个简单的解释器的[练手项目](https://github.com/proTao/toypreter)中的解释器基本就是围绕着名字空间完成的。但是我们知道名字空间是动态的叠加的，怎么叠加呢？就是通过维护环境栈帧的链表，因此，所谓上下文环境，最少还需要维护一个指针，指向上一个栈帧。这实际上是在模拟真实机器上的栈帧，在普通的x86机器上，当发生函数调用的时候，系统会在地址空间中创建新的栈帧并保存上一个栈帧的栈指针esp和帧指针ebp，这两个变量用于恢复上下文环境。

<!-- more -->

名字和值的绑定是属于动态信息，因为一个名字在不同的环境中可能有多个对应的值，比如函数中的变量`i`和函数外的变量`i`是不同的，这个信息需要动态的体现在上下文环境中。这个上下文环境，也就是栈帧，在python中表现为`PyFrameObject`对象。


```CPP
typedef struct _frame {
        PyObject_VAR_HEAD
        struct _frame *f_back;  /* previous frame, or NULL */
        PyCodeObject *f_code;   /* code segment */
        PyObject *f_builtins;   /* builtin symbol table (PyDictObject) */
        PyObject *f_globals;    /* global symbol table (PyDictObject) */
        PyObject *f_locals;     /* local symbol table (any mapping) */
        PyObject **f_valuestack;    /* points after the last local */
        PyObject **f_stacktop;
        PyObject *f_trace;      /* Trace function */
  
        PyObject *f_exc_type, *f_exc_value, *f_exc_traceback;

        PyThreadState *f_tstate;
        int f_lasti;        /* 上一条字节码指令在f_code中的偏移位置 */
   
        int f_lineno;       /* Current line number */
        int f_iblock;       /* index in f_blockstack */
        PyTryBlock f_blockstack[CO_MAXBLOCKS]; /* for try and loop blocks */
        PyObject *f_localsplus[1];  /* 一块动态内存，实际的运行时栈 */
} PyFrameObject;
```

在代码中可以发现python的frame中保存了LGB三个独立的名字空间，以及`f_back`这个用于构建环境链的属性。`f_code`还保存了编译好的静态信息。Frame中还维护了一段动态内存，这个是“物理上”的真正用于计算的栈，比如加法指令前会将两个操作数压栈，然后运行加法指令会将这两个数出栈计算再将结果压栈，这时操作的栈就是这段动态内存。其中`f_localsplus`就是使用一段动态内存作为栈，这个栈的大小存储在`f_stacksize`中。注意，这段动态内存虽然是一段连续的动态内存，但是实际上被分成了两块，一块用来存一个局部数据，一块用于计算（被字节码指令所操作）。前者就是从`f_localsplus`指向的位置开始的，而后者由`f_valuestack`和`f_stacktop`维护真正的运行时栈的栈底和栈顶。`f_localsplus`到`f_valuestack`之间的内存是用来存局部数据的，这一部分在函数部分的讲解中会看到是如何使用的。



类似于`code`对象，python也提供了这个`PyFrameObject`对象的python封装，可以通过`sys._getframe()`获取当前位置的栈帧对象。下面这个函数同样可以完成`sys._getframe()`的功能。

```python
import sys
def get_current_frame():
    try:
        1/0
    except Exception as e:
        type, value, traceback = sys.exc_info()
        return traceback.tb_frame.f_back
```


## 二、名字、作用域和名字空间

在python中，赋值语句会影响名字空间，赋值语句除了含有等于号的语句外，还有`def`、`import`、`class`等语句，以及函数的传参行为。一个赋值语句会创建一个名字与值的关联关系，这个关联关系就会存储在名字空间中。

一个module被加载到python中后，它在内存中以一个module对象的形式存在，module对象同样会维护一个名字空间（dict）。对象的名字空间中的所有名字都称为对象的属性，赋值语句就可以认为“拥有设置对象属性的行为”。而可同样有可以“访问对象的属性的行为”的语句，这类语句的行为被称为“**属性引用**”，属性引用就是访问另一个名字空间中的名字。一个module就是一个独立的名字空间引用另一个module中的名字就要使用属性引用的方式，如`modulename.a`来获得名字对应的对象。

一个module和另一个module分属不同的名字空间，划分比较清晰。而一个module内部可能会存在多个互相嵌套的名字空间。在一个module内部可能存在多个名字空间，每一个名字空间与一个作用域对应，一个约束起作用的程序正文范围称为这个约束的**作用域**，因此**作用域是一段文本代码**。我在文章中也屡次强调过，python的作用域是静态作用域，就是说，一个约束在程序正文中的某个位置是否起作用，是由该约束在代码中的位置唯一决定的。名字空间是与作用域对应的动态的东西，一个作用域在程序运行的时候就会体现为一个名字空间，具体的说就是一个dict对象。一个module的作用域就是`global`作用域。

位于一个作用域内的代码可以直接使用作用域内的名字而需要加上访问修饰符，即不需要使用“属性引用”的方式，此时的访问方式为“名字引用”。而作用域是嵌套的，这就使得名字空间也是嵌套的，一个赋值语句引入的名字在赋值语句所在的作用域内生效，在其内部嵌套的每个作用域内都生效。因此这就产生了“最内嵌套作用域规则”：查找名字的时候沿着作用域范围逐渐向外查找，在最先找到的名字空间内对应的值即为找到的值，直到到达最外嵌套层次。最外的作用域并不是module产生的global作用域，而是python自身定义的最顶层`buildin`作用域。

属性引用也是一种名字引用，但是属性引用实际上手动控制了查找的名字空间，则其不受LEGB规则的制约，这其实是一种更简单的名字查找方式。我们在类的`__init__`函数中通常就会同时使用属性引用与名字引用。我一说你就知道，就是这句话：`self.xxx = xxx`，前者是属性饮用，后者是名字引用。

## 三、python虚拟机的运行框架

python虚拟机的具体实现是一个叫做`PyEval_EvalFramEx`的巨大函数。这个函数负责创建栈帧。

## 四、尾递归优化

```python
# This program shows off a python decorator(
# which implements tail call optimization. It
# does this by throwing an exception if it is
# it's own grandparent, and catching such
# exceptions to recall the stack.
 
import sys
 
class TailRecurseException(Exception):
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs
 
def tail_call_optimized(g):
    """
    This function decorates a function with tail call
    optimization. It does this by throwing an exception
    if it is it's own grandparent, and catching such
    exceptions to fake the tail call optimization.
 
    This function fails if the decorated
    function recurses in a non-tail context.
    """
    def func(*args, **kwargs):
        f = sys._getframe()
        if f.f_back and f.f_back.f_back and f.f_back.f_back.f_code == f.f_code:
            raise TailRecurseException(args, kwargs)
        else:
            while 1:
                try:
                    return g(*args, **kwargs)
                except TailRecurseException as e:
                    args = e.args
                    kwargs = e.kwargs
    func.__doc__ = g.__doc__
    return func
 
@tail_call_optimized
def factorial(n, acc=1):
    "calculate a factorial"
    if n == 0:
        return acc
    return factorial(n-1, n*acc)
```

【TODO】


 * * *
## 参考
1. Python源码剖析（陈孺）
2. [Frame Hack](http://farmdev.com/src/secrets/framehack/)
3. [Python解释器简介（5）：深入主循环](http://python.jobbole.com/81660/)
4. [Frame Hacks](http://farmdev.com/src/secrets/framehack/)
