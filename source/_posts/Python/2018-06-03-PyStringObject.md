---
layout: post
date: 2018-06-03
title: python中的字符串对象
category: python
tags: 
- python
keywords:
description:
---

## 1. PyStringObject 与 PyString_Type
```CPP
[stringobject.h]
typedef struct {
	PyObject_VAR_HEAD
	long ob_shash;
	int ob_sstate;
	char ob_sval[1];
} PyStringObject;
```
`PyStringObject`是变长对象中的不可变对象。当创建了一个`PyStringObject`对象之后,该对象内部维护的字符串就不能再被改变了。这一点特性使得 `PyStringObject` 对象能作为 `PyDictObject` 的键值,但同时也使得一些字符串操作的效率大大降低,比如多个字符串的连接操
作。

`ob_sval`是存放实际字符串的数组，数组长度是`ob_size+1`，因为里面存放的是原生C字符串，需要一个额外的结束符。但是注意，申请的时候令数组长度为1，实际上是为了要数组的首地址当做指针来用，`ob_sval` 作为首地址，在字符串申请函数中，申请的是一段长度为`ob_size+1`个字节的内存,而且必须满足 `ob_sval[ob_size] = "\0‟`。详见后面源码与图一。

![PyStringObject存储结构](/img/PyStringObject1.png)

`PyStringObject` 中的 `ob_shash` 变量其作用是缓存该对象的 HASH 值,这样可以避免每一次都重新计算该字符串对象的 HASH 值。如果一个 `PyStringObject`对象还没有被计算过 HASH 值,那么 `ob_shash` 的初始值是-1。`PyStringObject` 对象的 `ob_sstate` 变量该对象是否被 `Intern` 的标志。

需要注意的是,字符串类型对象的`tp_as_number`,`tp_as_sequence`,`tp_as_mapping`,
三个域都被设置了。这表示`PyStringObject`对数值操作,序列操作和映射操作都支持。

<!-- more -->


## 2. 创建 PyStringObject 对象
```CPP
[stringobject.c]
PyObject* PyString_FromString(const char *str)
{
	register size_t size;
	register PyStringObject *op;
	assert(str != NULL);
	/*判断字符串长度*/
	size = strlen(str);
	if (size > PY_SSIZE_T_MAX) {
		return NULL;
	}
	/*处理 null string 和单个字符， 注意没有增加引用计数，为什么？*/
	if (size == 0 && (op = nullstring) != NULL) {
    	Py_INCREF(op);
		return (PyObject *)op;
	}
	if (size == 1 && (op = characters[*str & UCHAR_MAX]) != NULL) {
    	Py_INCREF(op);
		return (PyObject *)op;
	}
	/* 创建新的 PyStringObject 对象,并初始化 */
	/* Inline PyObject_NewVar */
	op = (PyStringObject *)PyObject_MALLOC(sizeof(PyStringObject) + size);
	if (op == NULL) return PyErr_NoMemory();
	PyObject_INIT_VAR(op, &PyString_Type, size);
	op->ob_shash = -1;
	op->ob_sstate = SSTATE_NOT_INTERNED;
	memcpy(op->ob_sval, str, size+1);

	// 这一段现在不用看，到第三节再回来看
	/* Intern(共享)长度较短的 PyStringObject 对象 */
	if (size == 0) {
		PyObject *t = (PyObject *)op;
		PyString_InternInPlace(&t);
		op = (PyStringObject *)t;
		nullstring = op;
		Py_INCREF(op);
	}
    else if (size == 1) {
		PyObject *t = (PyObject *)op;
		PyString_InternInPlace(&t);
		op = (PyStringObject *)t;
		characters[*str & UCHAR_MAX] = op;
		Py_INCREF(op);
	}
	return (PyObject *) op;
}
```
解释一下上面的源码，有几个重要的逻辑。
1. 字符串长度如果过长，将不会创建并返回空。win32 平台下，该值是2147483647。
2. 空字符串会用特殊的对象`nullstring`保存。
3. 单个字符会有一个专用对象缓冲池维护，该缓冲池维护长度为1的`PyStringObject`。
4. 最后使用intern机制

除了`PyString_FromString`，还有`PyString_FromStringAndSize` 可以通过C的原生字符串创建python字符串对象。而后者的操作过程和 `PyString_FromString` 一般无二,只是
有一点,`PyString_FromString` 传入的参数必须是以 `\0` 结尾的字符数组的指
针，然后通过 C 函数`strlen`确定字符串长度。而 `PyString_FromStringAndSize` 不会有这样的要求,因为通过传入的 `size` 参数就可以确定需要拷贝的字符的个数。

## 3. Intern 机制
```CPP
[stringobjec.c]
void PyString_InternInPlace(PyObject **p)
{
	// 为什么要传指针的指针没有太想明白
	register PyStringObject *s = (PyStringObject *)(*p);
	PyObject *t;
	if (s == NULL || !PyString_Check(s))
	Py_FatalError("PyString_InternInPlace: strings only please!");
	/* If it's a string subclass, we don't really know what putting
	   it in the interned dict might do. */
	if (!PyString_CheckExact(s))
		return;
	if (PyString_CHECK_INTERNED(s))
		return;
	if (interned == NULL) {
		interned = PyDict_New();
	}

	t = PyDict_GetItem(interned, (PyObject *)s);
	if (t) {
    	// 注意这里对引用计数的调整，新创建出来的对象引用计数是1，DEC后直接可以垃圾回收了
		Py_INCREF(t);
		Py_DECREF(*p);
		*p = t;
		return;
	}

	// 这个字典的键和值都是这个字符串对象
	PyDict_SetItem(interned, (PyObject *)s, (PyObject *)s) < 0)

	/* The two references in interned are not counted by refcnt.
	   The string deallocator will take care of this */
	s->ob_refcnt -= 2;
	PyString_CHECK_INTERNED(s) = SSTATE_INTERNED_MORTAL;
}
```
整个代码的流程：
1. 类型检查：不是str就不能应用intern机制，甚至派生类对象系统也不行。
2. 已经应用过intern机制的直接返回，确保不会对同一个`PyStringObject`进行一次以上的intern操作。
3. 如果还没有使用过intern，新建interned字典结构。
4. 如果interned中由当前字符串，让当前`PyStringObject`指针和`interned`中指针指向同一位置，然后改变引用计数。
5. 将字典中键和值都设为改字符串对象**指针**。
6. 注意对于被 `Intern` 的 `PyStringObject` 对象,Python 采用了特殊的引用计数机制。**在将一个 `PyStringObject` 对象 A 的 `PyObject` 指针作为 Key 和 Value 添加到 `interned`中时，`PyDictObject` 对象会通过这两个指针对 A 的引用计数进行两次加 1 操作。**但是 Python 的设计者规定在 interned 中 A 的指针不能被视为对象 A 的有效引用。否则 `interned` 中对`PyStringObject`的两个引用，将导致`interned`中的对象永远不能被回收。

![intern机制](/img/PyStringObject2.png)

为了对`PyStringObject`正常的垃圾回收，对`interned`使用了特殊的引用计数规则，那么在销毁对象的时候，也要对`interned`中存放的对象进行特殊处理。
```CPP
[stringobject.c]
static void string_dealloc(PyObject *op)
{
	switch (PyString_CHECK_INTERNED(op)) {
		case SSTATE_NOT_INTERNED:
			break;
            
		case SSTATE_INTERNED_MORTAL:
			/* revive dead object temporarily for DelItem */
            // 这里设置为3应该是又加上了开始时去掉的两个引用计数
			op->ob_refcnt = 3;
			if (PyDict_DelItem(interned, op) != 0)
				Py_FatalError("deletion of interned string failed");
			break;
            
		case SSTATE_INTERNED_IMMORTAL:
			Py_FatalError("Immortal interned string died.");
            
		default:
			Py_FatalError("Inconsistent interned string state.");
	}
	op->ob_type->tp_free(op);
}
```

说了这么多，用人话表述该机制就是：
> 该机制规定：当两个或以上的字符串变量它们的值相同且仅由数字字母下划线构成而且长度在20个字符以内，或者值仅含有一个字符时，内存空间中只创建一个对象来让这些变量都指向该内存地址。当字符串不满足该条件时，相同值的字符串变量在创建时都会申请一个新的内存地址来保存值。
> 
> 另外，并非全部的字符串都会采用intern机制。仅仅包括下划线、数字、字母的字符串才会被intern。也就是说。仅仅对那些看起来像是python标识符的进行intern。

上面的这个表述经过在 python 终端中的尝试，应该是正确无误的，但是我在Python源码中没有发现对大于一个字符的字符串的 intern 处理代码。而作者在对读者的回信中提到：
> 从 `PyStringObject` 对象的源码来看,在创建 `PyStringObject` 对象的时候,确实只对字符和 `nullstring` 进行了 Intern 操作。实际上在别的使用 `PyStringObject` 对象的地方,会在创建了对象后,调用 `Intern` 机制。比如在 `dict` 中,当你设置一个`(key, value)`的对时,就会用到这个 Intern 机制。

```CPP
int
PyDict_SetItemString(PyObject *v, const char *key, PyObject *item)
{
    PyObject *kv;
    int err;
    kv = PyString_FromString(key);
    if (kv == NULL)
        return -1;
    PyString_InternInPlace(&kv); /* XXX Should we really? */
    err = PyDict_SetItem(v, kv, item);
    Py_DECREF(kv);
    return err;
}
```


## 4. 字符缓冲池
类似于先对所创建的字符串(字符)对象进行 Intern 操作,再将 Intern 的结果缓存到字符缓冲池 `characters` 中。不同的是，在 Python 的整数对象体系中,小整数的缓冲池是在 Python runtime 初始化时被创建的,而字符串对象体系中的字符缓冲池则是“按需使用”。在 Python runtime 初始化完成之后,缓冲池中的所有 `PyStringObject` 指针都为空。

注意第二节创建 `PyStringObject` 部分的源码，对于单个字符实际上是按照这样的流程处理：

1. 创建 PyStringObject 对象”P”
2. 对对象”P”进行 Intern 操作
3. 将对象”P”缓存至字符缓冲池中



![字符缓冲池](/img/PyStringObject3.png)

## 5. 字符串连接效率问题
Python 中通过“+”进行字符串连接的方法效率及其低下,其根源在于 Python 中的 `PyStringObject` 对象是一个不可变对象。这就意味着当进行字符串连接时,实际上是必须要创建一个新的 `PyStringObject` 对象。这样,如果要连接 N 个 `PyStringObject` 对象,那么就必须进行 N-1 次的内存申请及内存搬运的工作。

而`join`操作只需要分配一次内存,执行效率将大大提高。
```CPP
[stringobject.c]
static PyObject* string_join(PyStringObject *self, PyObject *orig)
{
	char *sep = PyString_AS_STRING(self);
	const int seplen = PyString_GET_SIZE(self);
	PyObject *res = NULL;
	char *p;
	int seqlen = 0;
	size_t sz = 0;
	int i;
	PyObject *seq, *item;
	......
    //获得 list 中 PyStringObject 对象的个数,保存在 seqlen 中
	for (i = 0; i < seqlen; i++)
	{
		const size_t old_sz = sz;
		item = PySequence_Fast_GET_ITEM(seq, i);
		sz += PyString_GET_SIZE(item);
		if (i != 0)
			sz += seplen;
	}
	/* 申请内存空间 */
	res = PyString_FromStringAndSize((char*)NULL, (int)sz);
	/* 连接 list 中的每一个 PyStringObject 对象*/
	p = PyString_AS_STRING(res);
	for (i = 0; i < seqlen; ++i)
	{
		size_t n;
		/* 获得 list 中的一个 PyStringObject 对象*/
		item = PySequence_Fast_GET_ITEM(seq, i);
		n = PyString_GET_SIZE(item);
		memcpy(p, PyString_AS_STRING(item), n);
		p += n;
		if (i < seqlen - 1)
		{
			memcpy(p, sep, seplen);
			p += seplen;
		}
	}
	Py_DECREF(seq);
	return res;
}
```


## 6. Hack PyStringObject
```python
a="asd";b="asd"
print(a is b) # True

a="asd!";b="asd!"
print(a is b) # False

a="a"+"_";b="a_"
print(a is b) # True

a="a";b="ab"
print(a+"b" is b) # False

import sys
a="apple"
print(sys.getrefcount(a))
b="apple"
print(sys.getrefcount(a)) # 多了1

a="apple@"
print(sys.getrefcount(a))
b="apple@"
print(sys.getrefcount(a)) # 不变
```


（略略略）

* * *
参考：
1. Python源码剖析（陈孺）
2. [什么是string interning(字符串驻留)以及python中字符串的intern机制](https://www.cnblogs.com/brucemengbm/p/6952822.html)
3. [Python字符串的intern机制和大小整数对象池](https://my.oschina.net/u/3723649/blog/1815000)
4. [tring interning Wiki](https://en.wikipedia.org/wiki/String_interning)
