---
layout: post
date: 2018-06-30
title: Why Python is Slow:Looking Under the Hood
category: python
tags:
- python
- translation
---

**翻译自[Why Python is Slow: Looking Under the Hood](https://jakevdp.github.io/blog/2014/05/09/why-python-is-slow/)**

我们以前都听说过 : Python很慢。

当我在Python上讲授关于科学计算的课程时，我在课程的早期就提出了这个观点，并告诉学生们为什么:它归结为Python是一种动态类型的解释语言，它的值不是存储在密集的缓冲区中，而是存储在分散的对象中。然后我将讨论如何通过使用NumPy、SciPy和相关工具对操作进行矢量化并调用到编译后的代码，然后继续。

但最近我意识到一些事情:尽管上面的陈述相对准确，“动态类型-解释-缓存-向量-编译”这个词对参加入门编程研讨会的人来说可能没什么意义。可以说，这些术语并不能让人们了解“幕后”到底在发生什么。

所以我决定写这篇文章，深入研究我经常忽略的细节。在此过程中，我们将研究如何使用Python的标准库来反思CPython本身的问题。因此，无论您是新手还是经验丰富的程序员，我希望您能从下面的探索中学到一些东西。

<!-- more -->

Why Python is Slow[¶](#Why-Python-is-Slow)
------------------------------------------

由于各种原因，Python比Fortran和C慢:

### 1\. **Python is Dynamically Typed rather than Statically Typed**.[¶](#1.-Python-is-Dynamically-Typed-rather-than-Statically-Typed.)

这意味着在程序执行时，解释器不知道所定义的变量的类型。C变量(我使用C作为编译语言的替代)和Python变量之间的区别如下图所示:

![cint vs pyint](http://jakevdp.github.io/images/cint_vs_pyint.png)

对于C中的一个变量，编译器通过它的定义知道类型。对于Python中的一个变量，当程序执行时，您只知道它是某种Python对象。

如果你用C来写:

```CPP
int a = 1;
int b = 2;
int c = a + b;
```

C编译器从一开始就知道`a`和`b`是整数:它们不可能是别的东西!有了这些知识，它就可以调用增加两个整数的例程，返回内存中的一个简单值的另一个整数。作为一个粗略的示意图，事件的顺序如下:

#### C Addition[¶](#C-Addition)

1.  Assign `<int> 1` to `a`
2.  Assign `<int> 2` to `b`
3.  call `binary_add<int, int>(a, b)`
4.  Assign the result to c


Python中的等效代码如下:
```python
a = 1
b = 2
c = a + b
```

在这里，解释器只知道`1`和`2`是对象，而不知道它们是什么类型的对象。因此，解释器必须检查每个变量的`PyObject_HEAD`以查找类型信息，然后为这两种类型调用适当的求和例程。最后，它必须创建并初始化一个新的Python对象来保存返回值。事件的顺序大致如下:

#### Python Addition[¶](#Python-Addition)

1.  Assign `1` to `a`
    
    *   **1a.** Set `a->PyObject_HEAD->typecode` to integer
    *   **1b.** Set `a->val = 1`
2.  Assign `2` to `b`
    
    *   **2a.** Set `b->PyObject_HEAD->typecode` to integer
    *   **2b.** Set `b->val = 2`
3.  call `binary_add(a, b)`
    
    *   **3a.** find typecode in `a->PyObject_HEAD`
    *   **3b.** `a` is an integer; value is `a->val`
    *   **3c.** find typecode in `b->PyObject_HEAD`
    *   **3d.** `b` is an integer; value is `b->val`
    *   **3e.** call `binary_add<int, int>(a->val, b->val)`
    *   **3f.** result of this is `result`, and is an integer.
4.  Create a Python object `c`
    
    *   **4a.** set `c->PyObject_HEAD->typecode` to integer
    *   **4b.** set `c->val` to `result`

动态类型意味着与任何操作相关的步骤要多得多。这是Python在对数值数据进行操作时比C慢的主要原因。


### 2\. Python is interpreted rather than compiled.[¶](#2.-Python-is-interpreted-rather-than-compiled.)

上面我们看到了解释代码和编译代码之间的一个区别。一个聪明的编译器可以预测和优化重复或不需要的操作，这会导致加速。编译器优化是它自己的野兽，我个人没有资格说太多，所以我就讲到这里。关于这方面的一些实际例子，您可以查看我在Numba和Cython上的[之前的文章](http://jakevdp.github.io/blog3/06/15 / Numba -vs- Cython -take-2/)。

### 3\. Python's object model can lead to inefficient memory access[¶](#3.-Python's-object-model-can-lead-to-inefficient-memory-access)

我们在上面看到了从C整数转移到Python整数的额外类型信息层。现在假设有许多这样的整数，并希望对它们执行某种批处理操作。在Python中，您可能使用标准的“List”对象，而在C中，您可能使用某种基于缓冲的数组。

以最简单的形式表示的NumPy数组是围绕C数组构建的Python对象。也就是说，它有一个指向_contiguous_data值缓冲区的指针。另一方面，Python列表有一个指向指针的连续缓冲区的指针，每个指针指向一个Python对象，而这个对象又引用了它的数据(在本例中是整数)。这是两幅图的示意图

![数组和列表](http://jakevdp.github.io/images/array_vs_list.png)

很容易看出，如果您正在执行按顺序处理数据的操作，那么numpy布局在存储成本和访问成本方面将比Python布局高效得多。

### So Why Use Python?[¶](#So-Why-Use-Python?)

考虑到这种固有的低效率，我们为什么还要考虑使用Python呢?好吧，它可以归结为:动态类型使Python比C**更容易使用**，它非常**灵活和宽容**，这种灵活性导致了**高效地使用开发时间**，在那些您确实需要优化C或Fortran的情况下，**Python提供了编译库**的简单挂钩。这就是为什么Python在许多科学社区中的使用一直在不断增长。结合所有这些，Python最终成为一种非常高效的语言，用于完成使用代码进行科学研究的总体任务。

Python meta-hacking: Don't take my word for it[¶](#Python-meta-hacking:-Don't-take-my-word-for-it)
--------------------------------------------------------------------------------------------------

上面我已经讨论了一些内部结构，这些结构使得Python能够正常工作，但是我不想就此打住。在整理上述总结时，我开始深入研究Python语言的内部原理，并发现该过程本身非常具有启发性。

在接下来的几节中，我将通过使用Python本身来公开Python对象来验证上述信息的正确性。请注意，以下内容都是使用**Python 3.4**编写的。早期的Python版本具有稍微不同的内部对象结构，而后来的版本可能会进一步调整这种结构。请务必使用正确的版本!此外，下面的大多数代码都假设有一个64位CPU。如果您在一个32位的平台上，下面的一些C类型将不得不进行调整以解释这种差异。


```python
import sys
print("Python version =", sys.version[:5]) # Python version = 3.4.0
```

### Digging into Python Integers[¶](#Digging-into-Python-Integers)

Integers in Python are easy to create and use:

```python
x = 42
print(x) # 42
```

但是这个接口的简单性掩盖了在后台发生的事情的复杂性。我们简要地讨论了上面Python整数的内存布局。在这里，我们将使用Python的内置“ctypes”模块从Python解释器本身内省出Python的整数类型。但是首先我们需要知道Python整数在C API级别上的样子。

CPython中的实际“x”变量存储在CPython源代码中定义的结构中，在[Include/longintrepr.h](http://hg.python.org/cpython/file/3.4/Include/longintrepr.h/#l89)

```CPP
struct _longobject {
    PyObject_VAR_HEAD
    digit ob_digit[1];
};
```


``PyObject_VAR_HEAD``是一个宏，它以以下结构启动对象，在[Include/object.h](http://hg.python.org/cpython/file/3.4/Include/object.h#l111)中定义:

```CPP
typedef struct {
    PyObject ob_base;
    Py_ssize_t ob_size; /* Number of items in variable part */
} PyVarObject;
```


…这里又包含一个`PyObject`元素，它也在[Include/object.h](http://hg.python.org/cpython/file/3.4 include/object.h l105)中定义:

```CPP
typedef struct _object {
    _PyObject_HEAD_EXTRA
    Py_ssize_t ob_refcnt;
    struct _typeobject *ob_type;
} PyObject;
```


这里的`_PyObject_HEAD_EXTRA`是一个宏，在Python构建中通常不使用这个宏。

将所有这些组合在一起，并没有混淆typedefs/macros，我们的integer对象就会得到如下结构:


struct _longobject {
    long ob_refcnt;
    PyTypeObject *ob_type;
    size_t ob_size;
    long ob_digit[1];
};

`ob_refcnt`变量是对象的引用计数，`ob_type`变量是指向包含对象的所有类型信息和方法定义的结构的指针，`ob_digit`包含实际的数值。

有了这些知识，我们将使用`ctypes`模块开始研究实际的对象结构并提取上面的一些信息。

我们首先定义C结构的Python表示形式:

```python
import ctypes
class IntStruct(ctypes.Structure):
    _fields_ = [("ob_refcnt", ctypes.c_long),
                ("ob_type", ctypes.c_void_p),
                ("ob_size", ctypes.c_ulong),
                ("ob_digit", ctypes.c_long)]
    
    def __repr__(self):
        return ("IntStruct(ob_digit={self.ob_digit}, "
                "refcount={self.ob_refcnt})").format(self=self)
```


现在我们来看看某个数的内部表示，比如42。我们将使用在CPython中，`id`函数给出对象的内存位置:

```python
num = 42
IntStruct.from_address(id(42)) # IntStruct(ob_digit=42, refcount=35)
```

“ob_digit”属性指向内存中的正确位置!

但是“refcount”呢?我们只创建了一个值:为什么引用计数要比1大得多?

原来Python中大量使用小整数。如果为每一个整数创建一个新的`PyObject`，将需要大量内存。正因为如此，Python实现了公共整数对象缓冲池，里面的对象实现了`单例模式`:也就是说，内存中只有这些数字的一个副本。换句话说，每当您在这个范围内创建一个新的Python整数时，您只是创建一个具有该值的单例对象的引用:

```python
x = 42
y = 42
id(x) == id(y) # True
```

两个变量都是指向相同内存地址的指针。当您得到更大的整数(在Python 3.4中大于255)时，这就不再成立:

```python
x = 1234
y = 1234
id(x) == id(y) # False
```

只要启动Python解释器，就会创建许多整型对象;看看每个对象有多少引用计数是很有趣的:

```python
%matplotlib inline
import matplotlib.pyplot as plt
import sys
plt.loglog(range(1000), \[sys.getrefcount(i) for i in range(1000)\])
plt.xlabel('integer value')
plt.ylabel('reference count')
```

![](../img/why_python_is_slow3.png)

我们看到，0被引用了数千次，正如您所期望的，引用的频率通常随着整数的值的增加而降低。

为了进一步确保这是我们所期望的，让我们确保`ob_digit`字段保持正确的值:

```python
all(i == IntStruct.from_address(id(i)).ob_digit
    for i in range(256)) #True
```

如果再深入一点，您可能会注意到，这不适用于大于256的数字:事实证明，某些位移操作会在[Objects/longobject.c](https://hg.python.org/cpython/file/3.4/Objects/longobject.c#l232)中执行，这些改变了大整数在内存中的表示方式。

我不能说我完全理解为什么会发生这种情况，但我认为这与Python能够有效地处理超过长int数据类型溢出限制的整数有关，正如我们在这里看到的:

```python
2 ** 100 # 1267650600228229401496703205376
# 2 ** 100
```

这个数字太长以至于不能成为一个`long`,只能持有价值64位的值。

### Digging into Python Lists[¶](#Digging-into-Python-Lists)

让我们将上面的想法应用到更复杂的类型:Python列表。与整数类似，我们在[Include/listobject.h](http://hg.python.org/cpython/file/3.4/Include/listobject.h#l23)中找到列表对象本身的定义:
```CPP
typedef struct {
    PyObject\_VAR\_HEAD
    PyObject **ob_item;
    Py\_ssize\_t allocated;
} PyListObject;
```

同样，我们可以扩展宏并消除类型的混淆，以确保结构有效地如下所示:

```CPP
typedef struct {
    long ob_refcnt;
    PyTypeObject *ob_type;
    Py\_ssize\_t ob_size;
    PyObject **ob_item;
    long allocated;
} PyListObject;
```

这里的``PyObject **ob_item`指向列表的内容，`ob_size`值告诉我们列表中有多少项。

```python
class ListStruct(ctypes.Structure):
    _fields_ = [("ob_refcnt", ctypes.c_long),
                ("ob_type", ctypes.c_void_p),
                ("ob_size", ctypes.c_ulong),
                ("ob_item", ctypes.c_long),  # PyObject** pointer cast to long
                ("allocated", ctypes.c_ulong)]
    
    def __repr__(self):
        return ("ListStruct(len={self.ob_size}, "
                "refcount={self.ob_refcnt})").format(self=self)


```
让我们试一下：

```python
L = \[1,2,3,4,5\]
ListStruct.from_address(id(L)) # ListStruct(len=5, refcount=1)
```

为了确保我们已经正确地完成了任务，让我们在列表中创建一些额外的引用，并查看它如何影响引用计数:

```python
tup = \[L, L\]  \# two more references to L
ListStruct.from_address(id(L)) # ListStruct(len=5, refcount=3)
```

现在让我们看看如何在列表中找到实际的元素。

正如我们上面看到的，元素是通过`PyObject`指针的连续数组存储的。使用`ctypes`，我们实际上可以创建一个复合结构，其中包含我们以前的`IntStruct`对象:

```python
# get a raw pointer to our list
Lstruct = ListStruct.from_address(id(L))

# create a type which is an array of integer pointers the same length as L
PtrArray = Lstruct.ob_size * ctypes.POINTER(IntStruct)

# instantiate this type using the ob_item pointer
L_values = PtrArray.from_address(Lstruct.ob_item)
```

现在让我们看一下列表中每个元素的值。

```python
[ptr[0] for ptr in L_values]  # ptr[0] dereferences the pointer

# out
#[IntStruct(ob_digit=1, refcount=5296),
# IntStruct(ob_digit=2, refcount=2887),
# IntStruct(ob_digit=3, refcount=932),
# IntStruct(ob_digit=4, refcount=1049),
# IntStruct(ob_digit=5, refcount=808)]
```

我们已经在列表中恢复了`PyObject` 整形! 您可能希望花点时间来回顾上面的列表内存布局的示意图，并确保您理解了这些`ctypes`操作是如何映射到该图表上的。

### Digging into NumPy arrays[¶](#Digging-into-NumPy-arrays)

现在，为了进行比较，让我们对numpy数组进行同样的自省。我将跳过NumPy C-API数组定义的详细介绍;如果您想查看它，可以在[numpy/core/include/numpy/ndarraytypes.h](https://github.com/numpy/numpy/blob/maintenance/1.8.x/numpy/core/include/numpy/ndarraytypes.h#L646)中找到它

注意，这里使用的是NumPy version 1.8;这些内部特性可能在不同版本之间发生了变化，尽管我不确定是否如此。

```python
import numpy as np
np.__version__ # '1.8.1'
```

让我们首先创建一个表示numpy数组本身的结构。这应该开始看起来很熟悉了……

我们还将添加一些自定义属性来访问Python版本的形状和步骤:

```python


class NumpyStruct(ctypes.Structure):
    _fields_ = [("ob_refcnt", ctypes.c_long),
                ("ob_type", ctypes.c_void_p),
                ("ob_data", ctypes.c_long),  # char* pointer cast to long
                ("ob_ndim", ctypes.c_int),
                ("ob_shape", ctypes.c_voidp),
                ("ob_strides", ctypes.c_voidp)]
    
    @property
    def shape(self):
        return tuple((self.ob_ndim * ctypes.c_int64).from_address(self.ob_shape))
    
    @property
    def strides(self):
        return tuple((self.ob_ndim * ctypes.c_int64).from_address(self.ob_strides))
    
    def __repr__(self):
        return ("NumpyStruct(shape={self.shape}, "
                "refcount={self.ob_refcnt})").format(self=self)


```
现在我们来试试:
```python
x = np.random.random((10, 20))
xstruct = NumpyStruct.from_address(id(x))
xstruct # NumpyStruct(shape=(10, 20), refcount=1)
```

我们看到了正确的形状信息。让我们确保参考数是正确的:

```python
L = [x,x,x]  # add three more references to x
xstruct # NumpyStruct(shape=(10, 20), refcount=4)
```

现在我们可以把数据缓冲区取出来。为了简单起见，我们将忽略这个步骤，假设它是一个c连续数组;这可以通过一些工作来推广。

```python
x = np.arange(10)
xstruct = NumpyStruct.from_address(id(x))
size = np.prod(xstruct.shape)

# assume an array of integers
arraytype = size * ctypes.c_long
data = arraytype.from_address(xstruct.ob_data)

[d for d in data]  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

`data`变量现在是NumPy数组中定义的连续内存块的视图!为了显示这一点，我们将修改数组中的一个值……
```python
x[4] = 555
[d for d in data] # [0, 1, 2, 3, 555, 5, 6, 7, 8, 9]
```

…观察数据视图也在变化。`x`和`data`都指向相同的连续内存块。

通过比较Python列表和NumPy ndarray的内部结构，很明显，NumPy的数组对于表示相同类型数据的列表来说要**简单得多**。这一事实与使编译器能够更有效地处理有关。

Just for fun: a few "never use these" hacks[¶](#Just-for-fun:-a-few-"never-use-these"-hacks)
--------------------------------------------------------------------------------------------

使用“ctype”将c级数据封装在Python对象后面，可以做一些非常有趣的事情。如果我的朋友詹姆斯·鲍威尔(James Powell)说得对，我会在这里说:[说真的，不要使用这段代码](http://seriously.dontusethiscode.com/)。虽然下面的内容实际上不应该使用(曾经使用过)，但我仍然觉得非常有趣!

### Modifying the Value of an Integer[¶](#Modifying-the-Value-of-an-Integer)

受到[Reddit文章](http://www.reddit.com/r/Python/comments/2441cv/can_you_change_the_value_of_1/)的启发，我们实际上可以修改整型对象的数值!如果我们使用“0”或“1”这样的公共数字，很可能会导致Python内核崩溃。但如果我们用不太重要的数字来做，我们就能侥幸过关，至少是短暂的。

注意，这是一个非常非常糟糕的想法。特别是，如果您在IPython笔记本上运行这个程序，您可能会破坏IPython内核的运行能力(因为您在其运行时处理变量)。不过，我们还是祈祷一下:

```python
# WARNNG: never do this!
id113 = id(113)
iptr = IntStruct.from_address(id113)
iptr.ob_digit = 4  # now Python's 113 contains a 4!

113 == 4 # True
```


但是请注意，现在我们不能以简单的方式设置值，因为在Python中不再存在真正的值“113”!

```python
113 # 4
112 + 1 # 4


恢复的一种方法是直接操作字节。我们知道$$$113 = 7 \times 16^1 + 1 * 16^0$$$,所以在低位优先的64位系统上运行Python 3.4,运行以下代码:

```python
ctypes.cast(id113, ctypes.POINTER(ctypes.c_char))[3 * 8] = b'\x71'
112 + 1 # 113
```

然后我们恢复了！

再次强调一边:**永远不要这样做**。


### In-place Modification of List Contents[¶](#In-place-Modification-of-List-Contents)

上面我们对numpy数组中的值进行了就地修改。这很简单，因为numpy数组只是一个数据缓冲区。但是我们是否可以对列表做同样的事情呢?这有点棘手，因为列表存储_references_为值，而不是值本身。而且，为了不使Python本身崩溃，您需要非常小心地跟踪这些引用计数。以下是如何做到这一点:

```python
# WARNING: never do this!
L = [42]
Lwrapper = ListStruct.from_address(id(L))
item_address = ctypes.c_long.from_address(Lwrapper.ob_item)
print("before:", L) # before: [42]

# change the c-pointer of the list item
item_address.value = id(6)

# we need to update reference counts by hand
IntStruct.from_address(id(42)).ob_refcnt -= 1
IntStruct.from_address(id(6)).ob_refcnt += 1

print("after: ", L) # after:  [6]
```


就像我说的，你不应该用这个，我真的想不出你为什么要用这个。但是它可以让您了解解释器在修改列表内容时必须执行的操作类型。将它与上面的NumPy示例进行比较，您将看到Python列表比Python数组有更多开销的一个原因。

### Meta Goes Meta: a self-wrapping Python object[¶](#Meta-Goes-Meta:-a-self-wrapping-Python-object)

使用上述方法，我们可以开始变得更奇怪。`ctypes`中的`Structure`类本身就是一个Python对象，可以在[Modules/_ctypes/ctypes.h](https://hg.python.org/cpython/file/3.4/Modules/_ctypes/ctypes.h#l46)中看到。就像我们对int和list进行封装一样，我们也可以对结构本身进行封装，如下所示:

```python
class CStructStruct(ctypes.Structure):
    _fields_ = [("ob_refcnt", ctypes.c_long),
                ("ob_type", ctypes.c_void_p),
                ("ob_ptr", ctypes.c_long),  # char* pointer cast to long
                    ]
    
    def __repr__(self):
        return ("CStructStruct(ptr=0x{self.ob_ptr:x}, "
                "refcnt={self.ob_refcnt})").format(self=self)
```

现在我们将尝试创建一个封装自身的结构。我们不能直接这样做，因为我们不知道在内存中会创建什么地址。但是我们可以做的是创建一个_second_结构包装第一个，并使用它来修改它的内容。

我们先做一个临时的元结构，然后包装它:

```python
tmp = IntStruct.from_address(id(0))
meta = CStructStruct.from_address(id(tmp))

print(repr(meta))

CStructStruct(ptr=0x10023ef00, refcnt=1)
```
现在我们添加第三个结构，并使用它来就地修改第二个的内存值:

```python
meta_wrapper = CStructStruct.from_address(id(meta))
meta_wrapper.ob_ptr = id(meta)

print(meta.ob_ptr == id(meta)) # True
print(repr(meta)) # CStructStruct(ptr=0x106d828c8, refcnt=7)
```
我们现在有了一个自封装的Python结构!

再说一遍，我想不出你为什么要这么做。请记住，在Python中，这种类型的自我引用是具有开创性的——由于它的动态类型，在不直接入侵内存的情况下，这样做是非常直接的:



```python
L = []
L.append(L)
print(L) # [[...]]
```

Conclusion[¶](#Conclusion)
--------------------------

Python是缓慢的。正如我们所看到的，这其中的一个重要原因是引擎盖下的间接类型，它使Python变得快速、简单、有趣。正如我们所看到的，Python本身提供了可以用来攻击Python对象本身的工具。

我希望通过对不同对象之间的差异的探索，以及对CPython本身内部的一些自由主义的胡乱操作，可以使这一点更加清晰。这个练习对我非常有启发，我希望对你也一样……黑客快乐!

这篇博文完全是在IPython笔记本上写的。完整的笔记本可以在这里[下载](http://jakevdp.github.io/downloads/notebooks/WhyPythonIsSlow.ipynb)，或者静态地在这里[查看](http://nbviewer.ipython.org/url/jakevdp.github.io/downloads/notebooks/WhyPythonIsSlow.ipynb)
