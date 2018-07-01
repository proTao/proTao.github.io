---
layout: post
date: 2018-06-24
title: python中的“一切皆为对象”
category: python
tags: 
- python
keywords:
description:
---

想要理解Python新式类就要先区分旧类和新类的区别。Python2.2是旧类

![Python对象之间的关系](/img/PythonNewStyleClass1.png)

在 Python 中，任何一个对象都有一个 type ，可以通过对象的 \_\_class\_\_ 属性获得。任何一个 instance 对象的 type 都是一个class对象，而任何一个 class 对象的 type 都是 metaclass 对象。在大多数情况下这个 metaclass 都是 &lt; type 'type' &gt;，而在 Python 内部，他实际上对应的是 PyType\_Type。
在 Python 中，任何一个 class 对象都直接或间接的与 &lt; type 'object' &gt; 对象之间存在*继承*关系，**包括 &lt; type 'type' &gt;**。在 Python 内部，&lt; type 'object' &gt;**对应的是 PyBaseObject\_Type**。

`tp_dict`是python2.2升级后在`PyTypeObject`中新增的一个字段，这个字段正是旧类向新式类转变的关键。`tp_dict`在运行时会指向一个 dict 对象，这个 dict 对象必须在运行时动态构建。

```python
[classA.py]
class A(object):
    value = "python"
    def __init__(self):
        print("A::init")
    def f(self):
        print("A::f")
    def g(self, a):
        self.value = a
        print("A::g -> ", self.value)

a=A()
a.f()
a.g(1)
```
在命令行中`compile`得到`PyCodeObject`对象进行探索。如果想查看编译后的字节码，使用`dis`，比如`dis.dis("i=1")`。
```python
with open("class.py",'r') as f:
    co = compile(f.read(), "class.py", 'exec')
```


字节码解释：


`TOP()` (stack\_pointer[-1])
`SECOND()` 类似的从栈中取元素
`THIRD()`
`FOURTH()`
`SET_TOP(v)` (stack\_pointer[-1] = (v))
`SET_SECOND(v)` 类似的设置栈中元素
`SET_THIRD(v)`
`SET_FOURTH(v)`
`LOAD_CONST()`:从`PyCodeObject`中的co\_const元组（常量表）中读取指定索引的元素，增加其引用计数并压栈。
`STORE_NAME()`:从`PyCodeObject`的name元素中取指定索引的元素w，然后出栈栈顶元素v，把w:v加入当前帧的`local`字典（局部变量表）中。
`BUILD_MAP`：创建一个dict，并按照参数（表示dict中元素个数）出栈并赋值，最后将新建的dict压栈。
`BUILD_LIST()`：创建一个空list，并按照参数的数量连续出栈并对list赋值，然后将该list压栈。
`DUP_TOP`:将当前栈顶元素再次压栈并增加其引用计数。
`ROT_TWO`：将当前站定两个元素进行对调。
`LOAD_NAME`:首先根据参数在co\_names表中得到变量名，然后依次尝试在栈帧的f\_locals，f\_globals，f\_buildins中查找是否有该变量，只要遇到就返回压栈并增加引用计数，否则抛出异常。在这里实现了变量作用域的LGB规则，但是闭包在哪里实现的现在还不知道，等知道了再回来更新。注意该指令和`STORE_NAME`的关系，后者只是存储在local内，而前者不止在local内搜索。
`BINARY_ADD`:加法导致的指令，先出栈，然后与当前栈顶元素相加。该指令比较复杂，会对整型加法和字符串加法进行优化，有专用的快速通道。最后，必要的，将参与加法的元素出栈并减少引用计数，将和压栈并增加引用计数。

()[https://www.cnblogs.com/itrena/p/7434097.html]
