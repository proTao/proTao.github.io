---
layout: post
date: 2018-06-04
title: python中的列表对象
category: python
tags: 
- python
keywords:
description:
---

## 1. PyListObject对象
`PyListObject` 对象可以有效地支持插入,添加,删除等操作,在 Python 的列表中,无一例外地存放的都是 `PyObject` 的指针。所以实际上,你可以这样看待 Python 中的列表: `vector<PyObject*>`。

## 2. PyListObject 的创建与维护


### 2.1 创建对象

### 2.2 设置元素

### 2.3 插入元素

### 2.4 删除元素

## 3. PyListObject 对象缓冲池

## 4. Hack PyListObject




<!-- more -->


## 6. Hack PyStringObject
（略略略）

* * *
参考：
1. Python源码剖析（陈孺）
