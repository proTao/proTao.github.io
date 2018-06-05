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
	long ma_hash;
	 /* cached hash code of ma_key */
	PyObject *ma_key;
	PyObject *ma_value;
} PyDictEntry;
```
`ma_hash` 域中存储的是 `ma_key` 的散列值,利用一个域来记录这个散列值可以避免每次查询的时候都要重新计算一遍散列值。

`ma_key`和`ma_key`没啥说的，就是键值对。除此之外，这两者的状态还隐含反映了当前桶的状态，即未使用、或已使用还是标记删除状态。用一张图来表示。

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

// 初始化 PyDictObject
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
	if (ep->ma_key == NULL || ep->ma_key == key)
		return ep;
	//[3] 搜索失败时返回搜索序列上的第一个dummy态的entry，由于本次是首次寻址，如果遇到了dummy，那肯定是第一个dummy，直接设置就行，但是注意后面开放寻址步骤就要判断一下之前遇没遇到dummy了。
	if (ep->ma_key == dummy)
		freeslot = ep;
	else {
		//[4] 到这里了肯定是active态了，
		if (ep->ma_hash == hash && _PyString_Eq(ep->ma_key, key))
			return ep;
		freeslot = NULL;
	}
    // 开放寻址
	/* In the loop, ma_key == dummy is by far (factor of 100s) the least likely outcome, so test for that last. */
	for (perturb = hash; ; perturb >>= PERTURB_SHIFT) {
		i = (i << 2) + i + perturb + 1;
		ep = &ep0[i & mask];
		if (ep->ma_key == NULL)
			return freeslot == NULL ? ep : freeslot;
		if (ep->ma_key == key || (ep->ma_hash == hash && ep->ma_key != dummy && _PyString_Eq(ep->ma_key, key)))
			return ep;
		if (ep->ma_key == dummy && freeslot == NULL)
			freeslot = ep;
	}
}
```
有几点说明：
1. lookdict 永远都不会返回 NULL,如果在 PyDictObject 中搜索不到待查找的元素,同样会返回一个 entry，且`entry`处于可用状态，要么是空要么是dummy，**马上就可以被python使用**。
2. python采用的是开放寻址的方法，因此代码中也是分为两部分。第一次寻址的哈希函数，用的就是hash值对mask取余，这也是该变量被命名为`mask`的原因。注意到这里的hash是作为函数参数存在的，即在外部计算，因此**该函数不是PyObject接口层**。第二次的哈希寻址（待更新，参考源码中的Objects/dictnotes.txt）
3. 在开始时会选择搜索策略，如果是被搜索对象是字符串（而且仅仅对被搜索对象的类型有要求），就应用这个方法，否则应用`lookdict`这个普适版本。两者的区别在于普适版本内部有大量的捕获并处理错误的代码，还有就是对于对象的比较，字符串专用版本使用的是`_PyString_Eq`，而普适版本使用的是`PyObject_RichCompareBool`，前者仅仅比较了两个`PyStringObject`的长度和内容是否一致（使用strcmp的C函数），后者则会对不同的类型进行大量的处理。这使得两者的效率产生差异。为什么只对字符串版本有优化呢？原因在于 Python 自身也大量使用了 `PyDictObject` 对象,用来维护一个作用域中变量名和变量值之间的对应关系,或是用来在为函数传递参数时维护参数名与参数值的对应关系。这些对象几乎都是用 `PyStringObject` 对象作为 `entry` 中的 `key`，所以 `lookdict_string` 的意义就显得非常重要了。

在dictobject.c的源码文件的开头包含了对探测机理的详细介绍，我这里就有道翻译了一下然后把句子整理通顺直接贴上来。。。
> 最重要的细节是:大多数哈希方案依赖于一个“良好”的哈希函数，在模拟随机性的意义上。Python没有:它最重要的散列函数(用于字符串和int)在常见情况下是非常常规的.
> \>>>map(hash, ("namea", "nameb", "namec", "named"))
> out[1] : [-1658398457, -1658398460, -1658398459, -1658398462]
> 这并不一定是坏事!相反，在大小为2^i的表中，以低阶i位作为初始表索引的速度非常快，并且对于由连续ints范围索引的dicts完全没有冲突。当键是“连续的”字符串时，这几乎是正确的。所以这在一般情况下比随机行为更好，这是非常可取的。
> 另一方面，当发生冲突时，填充哈希表的连续片的倾向使得良好的冲突解决策略至关重要。只取哈希代码的最后一个i位也是很容易出错的:例如，将`[i << 16 for i in range(20000)]`视为一组键。由于int值就是它们自己的哈希值，这符合大小为2^15的命令，所以每个哈希码的最后15位都是0:它们都映射到相同的表索引。
> 但是迎合不寻常的情况不应该减慢通常的情况，所以我们还是取最后一点。剩下的由冲突解决方案决定。如果我们通常在第一次尝试时找到我们要找的键(结果是，我们通常是这样做的——表负载因数保持在2/3，所以概率是很稳定的)，那么保持初始的索引计算非常便宜是很有意义的。
> 但是为了解决不寻常的情况的同时不应该减慢通常的情况，所以我们还是取最后几位比特位作为首次探索函数。剩下的由冲突解决方案决定。如果我们通常在第一次探索时就能找到我们要找的键(结果证明，我们通常可以这样的——表负载因数保持在2/3，所以概率是很稳定的)，那么保持初始的索引计算非常简单是很有意义的。
> 然后二次探测函数用的是这个：`j = ((5*j) + 1) mod 2**i`，这里还没有考虑代码中`perturb`的影响，j 是新的索引，i 是mask的位数。
> 新的方法能确保探测到全部位置吗？

* * *
参考：
1. Python源码剖析（陈孺）
2. [关于python字典类型最疯狂的表达方式](https://vimiix.com/post/2017/12/28/python-mystery-dict-expression/)
3. [深入 Python 字典的内部实现](http://python.jobbole.com/85040/)