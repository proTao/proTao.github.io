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

## 一.代码对象

每个初学python的人都会认为python是一种解释型语言，这个不能说错。但是python并不是真的对执行的python代码的每一行进行解释，虽然我们有一个所谓的“解释器”。实际上对于运行的文件，python会使用虚拟机对运行的文件编译成字节码，然后虚拟机会对产生的字节码进行解释。而编译语言则会编译出适用于x86、ARM等的指令2（作用于真正的机器）的语言。“解释性”语言不是根本就没有编译器，而只编译成一个中间表示，比如字节码。字节码的指令不是作用于任何硬件的，而是虚拟机。

其实更准确的说法应该是“python是一种动态语言”。而这种动态性也是难以优化Python的原因之一：在编译代码对象和生成字节码的时候，你并不知道会有怎样的结果。编译器根本不关心结果如何。由于不用声明类型信息，几乎每个指令都要像INVOKE_ARBITRARY_METHOD一样来执行。尽管“编译”和“解释”的定义在通常情况下是很难区分的，但是对于Python来说却很简单。编译工作就是生成代码对象，包括字节码。而翻译的工作就是翻译字节码，执行指令。Python保持“动态”特性的原因之一就是同样的字节码能够有不同的作用。更普遍的说法就是Python解释器的工作比编译器的多一些。

<!-- more -->

这个编译出的字节码是静态分析的结果，因此只要代码相同编译出的字节码就会相同，因此如果对于同样的字节码，重复编译是没有必要的，因此python会对符合一定规则的python文件（通常可以认为是被import的文件）编译出字节码并缓存下来，这个就是pyc文件。而pyc文件中存放的就是字节码，准确的说是编译出的`PyCodeObject`。

**python是的作用域规则是静态作用域**。这个一定要好好理解，所谓的静态作用域其实就是**词法作用域**，这个是作用域规则是导致闭包的根本原因，简单地说，静态作用域就是指变量的作用域只与其出现在代码的位置有关，是可以静态判断的，与运行时环境没有关系。体现在代码对象中，这个规则反映为每一个Code Block都会编译为一个`PyCodeObject`。

这里的疑问是，我们已经知道，python的for循环不会导致局部作用域的产生，控制流产生的代码块会产生单独的`PyCodeObject`吗？这个问题容易回答，控制流是不会导致局部作用域生成的，那么控制流也不会导致新的`PyCodeObject`的生成。只需要记住一个简单的规则，只有进入一个新的名字空间的时候，才算进入一个新的Code Block，才会导致一个`PyCodeObject`的生成。比如一个类或者一个函数，都会导致生成一个新的`PyCodeObject`。

而结合上面的说法，我们应该可以理解，所谓的一个作用域对应一个名字空间的说法。名字空间是符号的**上下文环境**，名字空间持有名字与值的绑定，而作用域是一块代码区域，代码区域引用名字、访问变量时，作用域与命名空间之间就有了联系。名字的作用域是指名字可以影响到的代码文本区域，名字空间的作用域就是这个名字空间可以影响到的代码文本区域。那么也存在这样一个代码文本区域，多个命名空间可以影响到它。作用域只是文本区域，其定义是静态的；而名字空间却是动态的，只有随着解释器的执行，命名空间才会产生。那么，在静态的作用域中访问动态命名空间中的名字，造成了作用域使用的动态性。在一定程度上，可以认为动态的作用域就是命名空间。

每一个Code Block都对应一个名字空间，并存在于一个`PyCodeObject`中。


```CPP
/* Bytecode object */
typedef struct {
    PyObject_HEAD
    int co_argcount;        /* #arguments, except *args */
    int co_nlocals;     /* #local variables */
    int co_stacksize;       /* #entries needed for evaluation stack */
    int co_flags;       /* CO_..., see below */
    PyObject *co_code;      /* 字节码指令序列 */
    PyObject *co_consts;    /* Code Block中的所有常量元组 */
    PyObject *co_names;     /* Code Block中的所有符号元组 */
    PyObject *co_varnames;  /* 局部变量名集合 */
    PyObject *co_freevars;  /* tuple of strings (free variable names) */
    PyObject *co_cellvars;      /* 内部嵌套函数引用的局部变量名集合 */
    /* The rest doesn't count for hash/cmp */
    PyObject *co_filename;  /* py文件的路径 */
    PyObject *co_name;      /* Code Block的名字，通常是函数名或者类名 */
    int co_firstlineno;     /* 在对应的py文件中的起始行号 */
    PyObject *co_lnotab;    /* 字节码指令与py文件中的源码行号之间的关系 */
    void *co_zombieframe;     /* for optimization only (see frameobject.c) */
    PyObject *co_weakreflist;   /* to support weakrefs to code objects */
} PyCodeObject;

```

PyCodeObject是C级别的对象，对该对象也提供了python实现级别的对象，可以使用如下方式使用。

```python
filename = "xxx.py"
with open(filename) as f:
    source = f.read()
co = compile(source, filename, "exec")
type(co)
dir(co)

import dis
dis.dis(co) # 编译为字节码
```

上述代码展示了如果在python解释器中获取指定文件编译出的字节码对象。一个源码文件中通常会定义多个函数，前面我们提到一个函数会产生一个新的`PyCodeObject`，但是上述代码显示我们只拿到了一个`PyCodeObject`对象，那么这个Python文件中的函数对应的其他`PyCodeObject`对象在哪？我们很容易想到`PyCodeObject`对象是一个嵌套结构，因为代码的Code Block本身就是嵌套结构的，而子`PyCodeObject`对象就嵌套在父`PyCodeObject`的`co_consts`属性中。此时的`PyCodeObject`中并没有存储名字和值的对应，因为这种对应是属于“动态信息”。在`co_consts`和`co_names`中存储的都是名字和常量构成的元组。

假设我们有一个文件真的叫`xxx.py`，文件的内容如下：
```python
# xxx.py
class A():
    pass


def func():
    a = 5
    b = 2
    print('hello', a, b)


a = A()
func()
```

对这一段代码运行上述生成`PyCodeObject`与编译的代码片，可以得到结果如下。要知道的是`dis`模块是反汇编工具，这个工具是python自己用不到的，因为反汇编是面向程序员的，机器只需要读取字节码的字节表示的数字就可以，程序员才需要将其转换为可读的指令名称。在下面展示的结果中，第一列是源码对应的行号，第二列是字节码的偏移量，然后是字节指令的名称。第四列是参数本身，举例来说，下面代码中的第一个`LOAD_CONST`会在当前字节码对象的`co_consts`表中搜索第0个元素，然后读取到的结果展示在后面的括号中，是一个code对象，然后这个LOAD指令会将读取到的内容压栈。

```bash
  1           0 LOAD_BUILD_CLASS
              1 LOAD_CONST               0 (<code object A at 0x7fae201a7300, file "test.py", line 1>)
              4 LOAD_CONST               1 ('A')
              7 MAKE_FUNCTION            0
             10 LOAD_CONST               1 ('A')
             13 CALL_FUNCTION            2 (2 positional, 0 keyword pair)
             16 STORE_NAME               0 (A)

  5          19 LOAD_CONST               2 (<code object func at 0x7fae201a7150, file "test.py", line 5>)
             22 LOAD_CONST               3 ('func')
             25 MAKE_FUNCTION            0
             28 STORE_NAME               1 (func)

 11          31 LOAD_NAME                0 (A)
             34 CALL_FUNCTION            0 (0 positional, 0 keyword pair)
             37 STORE_NAME               2 (a)

 12          40 LOAD_NAME                1 (func)
             43 CALL_FUNCTION            0 (0 positional, 0 keyword pair)
             46 POP_TOP
             47 LOAD_CONST               4 (None)
             50 RETURN_VALUE

```

可以发现对于`class A`和`def func`这两行代码生成的字节码，都是在最后通过`STORE_NAME`将类名或者函数名进行存储。


 * * *
## 参考
1. Python源码剖析（陈孺）
