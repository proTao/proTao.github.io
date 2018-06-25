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


![Python对象之间的关系](/img/PythonNewStyleClass1.png)

在 Python 中，任何一个对象都有一个 type ，可以通过对象的 \_\_class\_\_ 属性获得。任何一个 instance 对象的 type 都是一个class对象，而任何一个 class 对象的 type 都是 metaclass 对象。在大多数情况下这个 metaclass 都是 &lt; type 'type' &gt;，而在 Python 内部，他实际上对应的是 PyType\_Type。
在 Python 中，任何一个 class 对象都直接或间接的与 &lt; type 'object' &gt; 对象之间存在*继承*关系，**包括 &lt; type 'type' &gt;**。在 Python 内部，&lt; type 'object' &gt;**对应的是 PyBaseObject\_Type**。