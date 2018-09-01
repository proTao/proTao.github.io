---
layout: post
date: 2018-06-02
title: python中的整数对象
category: python
tags: 
- python
keywords:
description:
---

## 1. 初识 PyIntObject 对象

```CPP
[intobject.h]
typedef struct {
	PyObject_HEAD
    long ob_ival;
} PyIntObject
```

首先，`PyIntObject`是一个不可变（immutable）对象。其次，Python内部也大量的使用整数对象，我们在自己的代码中也会有大量的创建销毁整型对象的操作，因此单独的维护整形对象并对其申请内存和释放内存是不现实的。Python给出的解决方案是将整形对象通过一定的结构连接在一起的**整数对象系统**：整数对象池，一个整形对象的缓冲池机制。

Python的实现中，对某些可能频繁执行的代码，都会提供函数和宏两个版本。**宏版本节省了一次函数调用的开销但是牺牲了类型安全。**对于`PyIntObject`的操作，像前面说的，定义在该类型对象的函数指针中。特别注意的是，`tp_as_number`指针存放的是`int_as_number`结构体的地址，在 python2.5 中，该结构体包含了39个`PyNumberMethods`要求的函数指针，但是不是每个指针都有定义，部分为`NULL`。

另一个有趣的元信息是对象的文档，这个元信息维护在`int_doc`域中，文档无缝集成在语言的实现中，这一点是Python相对其他语言的一大特点。


<!-- more -->

## 2. PyIntObject 对象的创建和维护

### 2.1 对象创建的三种途径
1. PyInt\_FromString
2. PyInt\_FromLong
3. PyInt\_FromUnicode

其中，后两种方法实际上是先转换成浮点数,然后再调用`PyInt_FromFloat`，这实际上是 Adaptor Pattern 的思想：对核心函数进行接口转换。

### 2.2 小整数对象
想一想 C 语言中的 for 循环,就可以了解这些小整数会有多么频繁的使用场合。在 Python 中,所有的对象都是存活在系统堆上。这样的操作不仅大大降低了运行效率,而且会在系统堆上造成内存碎片。

所以解决方法就是**对小整数使用对象池技术**，正是因为使用缓冲池，`PyIntObject`才是不可变对象。**想一下这是为什么？**

**原因在于：对象池中的每一个对象可以被安全的共享。**那么，多小才算小整数？默认的范围是-5到256，这个值不可以动态修改，要想修改只能修改源代码然后重新编译。

### 2.3 大整数对象
对于大整数对象，是一次申请一块内存，这块内存用`PyIntBlock`结构体管理，该结构体中中有一个`PyIntObject`数组（会链表形式维护）来供大整数对象使用，还有一个用于形成链表的指向下一个block的指针。如果这一整块内存都祸祸光了（默认一个block可以存放82个int对象），就再申请一个`PyIntBlock`，然后用一个**单向链表**维护所有的`PyIntBlock`，**这个链表就是大整数对象缓冲池两个重要变量其中之一**：`block_list`指针。

另一个是干啥的稍微一想就能想到：这个 block 链表维护的是一整块block，是block级别的，我要使用的是`PyIntObject`，每次使用的话总不能进到block去遍历数组去找到一个还没使用的`PyIntObject`吧，所以下一个大整数缓冲池至关重要的变量就是`free_list`指针，这个指向一个链表，链表中的所有元素是`PyIntObject`。注意这两个链表的元素不是一个级别。虚拟机刚启动时，两个指针均为空。

需要注意的是`PyIntObject`中没有预先定义的供链表使用的`next`指针，这里借用了`ob_type`作为链表指针，因为我们知道在这个链表中拿到的对象都是用于实例化 int 对象的。




### 2.4 添加和删除
插图配源码，效果一顶俩。

```CPP
[intobject.c]
PyObject* PyInt_FromLong(long ival)
{
	register PyIntObject *v;
#if NSMALLNEGINTS + NSMALLPOSINTS > 0
	//尝试使用小整数池
	if (-NSMALLNEGINTS <= ival && ival < NSMALLPOSINTS) {
		v = small_ints[ival + NSMALLNEGINTS];
		Py_INCREF(v);
		return (PyObject *) v;
	}
#endif
	// 如果必要，申请block
	if (free_list == NULL) {
		if ((free_list = fill_free_list()) == NULL)
			return NULL;
	}
	// 初始化
	v = free_list;
	free_list = (PyIntObject *)v->ob_type;
	PyObject_INIT(v, &PyInt_Type);
	v->ob_ival = ival;
	return (PyObject *) v;
}

[intobject.c]
static PyIntObject* fill_free_list(void)
{
	PyIntObject *p, *q;
    // malloc空间
	p = (PyIntObject *) PyMem_MALLOC(sizeof(PyIntBlock));
	if (p == NULL)
		return (PyIntObject *) PyErr_NoMemory();
    // 链接block_list
	((PyIntBlock *)p)->next = block_list;
	block_list = (PyIntBlock *)p;
    // （自后向前）链接free_list
	p = &((PyIntBlock *)p)->objects[0];
	q = p + N_INTOBJECTS;
	while (--q > p)
		q->ob_type = (struct _typeobject *)(q-1);
	q->ob_type = NULL;
	return p + N_INTOBJECTS - 1;
}
```

因此，结合源码，申请`PyIntObject`的完整流程是：
1. 如果是小整数，直接返回小整数对象，增加引用计数，返回。
2. 如果没有可用空间，申请block，初始化block，把block中的对象数组链接到`free_list`中。
3. 当必要的空间被申请之后,将会把当前可用的 Block 中的内存空间划出一块,将在这块内存上创建我们需要的 `PyIntObject` 对象,同时,还会调整完成必要的初始化工作,以及调整 `free_list` 指针,使其指向下一块还没有被占用的内存。
![block结构体](/img/PyIntObject1.png)
![block初始化后](/img/PyIntObject2.png)
注意，新申请的 block 在链表头，这样做的原因是考虑到链表的插入效率。
![block链表](/img/PyIntObject3.png)

如果操作系统学得不错，对于管理存储空间比较熟悉，立刻就会发现还有一点没有实现，就是内存的释放与回收。既然`free_list`管理所有可用的`PyIntObject`，那么在对象回收的时候，应该将其链接回`free_list`。

```CPP
[intobject.c]
static void int_dealloc(PyIntObject *v)
{
	if (PyInt_CheckExact(v)) {
    	// 链到free_list头
		v->ob_type = (struct _typeobject *)free_list;
		free_list = v;
	}
	else
    	// 如果删除的是int派生类的对象，调用其类型对象的方法
        // (可能在free函数中实现一些自定义功能)
		v->ob_type->tp_free((PyObject *)v);
}
```
![创建与回收](/img/PyIntObject4.png)

这样一来，本来在各个 block 中的隔断的对象数组也会在回收阶段被`free_list`连接起来。

![block空闲内存的互联](/img/PyIntObject5.png)
一个小小的内存问题是，这些 block 在本次执行结束前，不会交还给系统堆。一个`PyIntObject`对象的大小是12字节，需要89478486个对象就可以消耗1G内存。

### 2.5 小整数对象池的初始化
从前面为`PyIntObject`申请空间的源码中可以看到，`small_ints`就是小整数池，其实一个数组，维护着所有小整数的指针。小整数池的初始化，在Python初始化的时候会自动调用，而其使用的空间也是`PyIntBlock`中的对象数组。
```CPP
[intobject.c]
int _PyInt_Init(void)
{
	PyIntObject *v;
	int ival;
	#if NSMALLNEGINTS + NSMALLPOSINTS > 0
	for (ival = -NSMALLNEGINTS; ival < NSMALLPOSINTS; ival++)
	{
		if (!free_list && (free_list = fill_free_list()) == NULL)
			return 0;
		/* PyObject_New is inlined */
		v = free_list;
		free_list = (PyIntObject *)v->ob_type;
		PyObject_INIT(v, &PyInt_Type);
		v->ob_ival = ival;
		small_ints[ival + NSMALLNEGINTS] = v;
}
#endif
return 1;
}
```
![小整数池的存储结构](/img/PyIntObject6.png)

综上所述，Python 中的`PyIntObject`构成了一个整数系统，其下有两个“部门”，一个是静态对象池，一个是动态缓冲池，两个池的管理使用两个不同级别的指针`block_list`和`free_list`来统一管理，内存使用的基本单元是`PyIntObject`。

## Hack PyIntObject
![](/img/PyIntObject7.png)
![](/img/PyIntObject8.png)
![](/img/PyIntObject9.png)
![](/img/PyIntObject10.png)



（略略略）

* * *
参考：
1. Python源码剖析（陈孺）
