---
layout: post
title: 基于CFG的句法分析算法
date: 2017-7-4
category: 自然语言处理
tags: 
- nlp
- algorithm
keywords: 条件随机场
description:
---

## 基于CFG的句法分析

### 线图分析法

### 线图分析法

先直观的感受这个算法，其实这是一个非常naive的方法，如果直接让大家用一个带词性标注的句子和一套CFG规则去解析出句法树，这个方法应该就是最直接的解法。
假设有这样的的句子和CFG规则：
> 带标注的句子：the(Det) boy(N) hits(V) the(Det) dog(N) with(Prep) a(Det) rod(N)

CFG规则:
> - S -> NP VP
> - NP -> Det N
> - VP -> VP PP
> - VP -> V NP
> - PP -> Prep NP

主要的思想就是每处理一个节点都回头看看，新加上的这个节点能不能和之前的节点再次利用CFG规则合并。进行自底向上的合并成为一棵句法树。
首先把Det放入树叶节点，然后添加N叶节点，此时回头看发现可以把Det和N合并为NP，所以添加NP作为Det和N的父节点。NP节点再往前看没了，然后往后看，把V加入线图。此时树是这样的：
