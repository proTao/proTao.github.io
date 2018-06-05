---
layout: post
date: 2018-06-05
title: python中的字典对象
category: python
tags: 
- python
keywords:
description:
---

## 1. 散列表概述
C++的 STL 中的 map 就是一种关联容器,map 的实现基于 RB-tree(红黑树)，理论上,其搜索的复杂度为 O(logN)。Python 中同样提供关联式容器,即 `PyDictObject` 对象。与 map 不同的是,`PyDictObject` 对搜索的效率要求及其苛刻,这也是因为 `PyDictObject` 在 Python 本身的实现中被大量地采用,比如会通过 `PyDictObject` 来建立符号表。因此,`PyDictObject` 采用了散列表(hashtable)。理论上,在最优情况下,散列表能提供 O(1)复杂度的搜索效率。
有很多种方法可以用来解决产生的散列冲突,比如说开链法,这是 SGI STL 中的 hash table 所采用的方法;而 Python 中所采用的是另一种方法,即开放定址法。当产生散列冲突时, Python 会通过一个二次探测函数,计算下一个候选位置,如果这个位置可用,则可将待插入元素放到这个位置，如果不行将继续探测。

## 2. PyDictObject

### 2.1 关联容器的enry

在此后的描述中,我们将把关联容器中的一个(键,值)元素对称为一个 `entry`。
```CPP
[dictobject.h]
typedef struct {
	long me_hash;
	 /* cached hash code of me_key */
	PyObject *me_key;
	PyObject *me_value;
} PyDictEntry;
```
`me_hash` 域中存储的是 `me_key` 的散列值,利用一个域来记录这个散列值可以避免每次查询的时候都要重新计算一遍散列值。

`me_key`和`me_key`没啥说的，就是键值对。除此之外，这两者的状态还隐含反映了当前桶的状态，即未使用、或已使用还是标记删除状态。用一张图来表示。

![Entry状态转换](/img/PyDictObject1.png)

其中`dummy`是一个特殊的静态对象，仅仅是用于标记。在第一个 dict 对象创建时会创建该`dummy`对象。
```CPP
dummy = PyString_FromString("<dummy key>");
```

### 2.2 关联容器的实现
```CPP
[dictobject.h]
#define PyDict_MINSIZE 8
typedef struct _dictobject PyDictObject;
struct _dictobject {
	PyObject_HEAD
	int ma_fill; /* # Active + # Dummy */
	int ma_used; /* # Active */
	int ma_mask;
	PyDictEntry *ma_table;
	PyDictEntry *(*ma_lookup)(PyDictObject *mp, PyObject *key, long hash);
	PyDictEntry ma_smalltable[PyDict_MINSIZE];
};
```
对于`PyDictObject`结构体，各个字段的含义是：
- PyObject_HEAD : 出乎意料的，dict竟然是定长对象。我觉得一部分的原因在于小量级的字典的确是用固定长度的数组`ma_smalltable`来存储的。
- ma_fill : active 加上 dummy 的 entry 数量。
- ma_used : active 的 entry 数量。
- ma_mask : 总的 entry 数-1，因为槽的数量始终是 2 的指数，所以这个数一定是一个所有位为 1 的变量，用于 key 的模数从而得到目标槽的索引。
- ma_table : 指向用户存储的`PyDictEntry`数组。
- ma_lookup : 哈希函数，有两种，默认是对字符串优化过的版本。
- ma_smalltable : 小型的字典直接使用这个静态申请大小的存储空间，可能也初始化时是固定大小，`PyDictObject`才用的定长对象。默认情况下就是把`ma_mask`设置为7。

![PyDictObject结构体](/img/PyDictObject2.png)

## 3. PyDictObject 的创建和维护

### 3.1 PyDictObject对象创建
```CPP
[dictobject.c]
typedef PyDictEntry dictentry;
typedef PyDictObject dictobject;

// 缓冲池相关
#define MAXFREEDICTS 80
static PyDictObject *free_dicts[MAXFREEDICTS];
static int num_free_dicts = 0;

#define INIT_NONZERO_DICT_SLOTS(mp) do { \
	(mp)->ma_table = (mp)->ma_smalltable; \
	(mp)->ma_mask = PyDict_MINSIZE - 1; \
} while(0)

# 初始化 PyDictObject
#define EMPTY_TO_MINSIZE(mp) do { \
	memset((mp)->ma_smalltable, 0,sizeof((mp)->ma_smalltable)); \
	(mp)->ma_used = (mp)->ma_fill = 0; \
	INIT_NONZERO_DICT_SLOTS(mp); \
} while(0)

PyObject* PyDict_New(void)
{
	register dictobject *mp;
	if (dummy == NULL) {
    	/* Auto-initialize dummy */
		dummy = PyString_FromString("<dummy key>");
		if (dummy == NULL)
			return NULL;
		}
		if (num_free_dicts)
		{
			if (num_free_dicts) {
				mp = free_dicts[--num_free_dicts];
				_Py_NewReference((PyObject *)mp);
                if (mp->ma_fill) {
					EMPTY_TO_MINSIZE(mp);
				}
            }
		}
        else {
			mp = PyObject_GC_New(dictobject, &PyDict_Type);
			if (mp == NULL)
				return NULL;
			EMPTY_TO_MINSIZE(mp);
		}
		mp->ma_lookup = lookdict_string;
		_PyObject_GC_TRACK(mp);
		return (PyObject *)mp;
	}
}
```

### **3.2 PyDicyObject中的元素搜索**

**这部分很重要，是理解dict的要点。**
```CPP
[dictobject.c]
static dictentry* lookdict_string(dictobject *mp, PyObject *key, register long hash)
{
	register int i;
	register unsigned int perturb;
	register dictentry *freeslot;
	register unsigned int mask = mp->ma_mask;
	dictentry *ep0 = mp->ma_table;
	register dictentry *ep;
    
    // 选择搜索策略
	if (!PyString_CheckExact(key)) {
		mp->ma_lookup = lookdict;
		return lookdict(mp, key, hash);
	}
	//[1] 首次寻址
	i = hash & mask;
	ep = &ep0[i];
	// if NULL or interned
    // 本来没明白为啥要直接比较指针的值，看到这个注释有些明白了，是为了判断该对象是不是被intern了，那么两个对象肯定指向同一个对象，因此指针的值相同。
	if (ep->me_key == NULL || ep->me_key == key)
		return ep;
	//[3] 搜索失败时返回搜索序列上的第一个dummy态的entry，由于本次是首次寻址，如果遇到了dummy，那肯定是第一个dummy，直接设置就行，但是注意后面开放寻址步骤就要判断一下之前遇没遇到dummy了。
	if (ep->me_key == dummy)
		freeslot = ep;
	else {
		//[4] 到这里了肯定是active态了，
		if (ep->me_hash == hash && _PyString_Eq(ep->me_key, key))
			return ep;
		freeslot = NULL;
	}
    # 开放寻址
	/* In the loop, me_key == dummy is by far (factor of 100s) the least likely outcome, so test for that last. */
	for (perturb = hash; ; perturb >>= PERTURB_SHIFT) {
		i = (i << 2) + i + perturb + 1;
		ep = &ep0[i & mask];
		if (ep->me_key == NULL)
			return freeslot == NULL ? ep : freeslot;
		if (ep->me_key == key || (ep->me_hash == hash && ep->me_key != dummy && _PyString_Eq(ep->me_key, key)))
			return ep;
		if (ep->me_key == dummy && freeslot == NULL)
			freeslot = ep;
	}
}
```


* * *
参考：
1. Python源码剖析（陈孺）
2. [关于python字典类型最疯狂的表达方式](https://vimiix.com/post/2017/12/28/python-mystery-dict-expression/)
