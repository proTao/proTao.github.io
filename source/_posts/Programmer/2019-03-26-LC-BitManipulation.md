---
layout: post
date: 2019-03-26
title: LeetCode刷题笔记——Bit Manipulation
category: 程序员的玩具
tags:
- algorithm
---

## 136. Single Number *(bangbang)*
利用的思路是通过异或操作来区分出现偶数次和奇数次的元素。使用一个同类型的元素，不停地对它进行异或，剩下的就是奇数次的，这道题中只有一个元素出现一次，因此剩下的就是他了。


## 137. Single Number II
这道题和上面的136的题设基本一样，唯一不同的地方是出了一个元素出现一次，剩下的元素都出现三次。这点小小的区别使得只靠奇偶性的位操作方法不能解决了，使用hashmap可以解决，但是如果想要不使用额外空间则需要另辟蹊径。这个我自己师妹想出来，看讨论区第一的思路，屌屌的。我不知道他是怎么想出来的，但是大概的想法是利用位运算的周期性吧？
上一题的核心是：
```python
a = 0
def f(x):
    global x
    a = a ^ x
```

那么相同的操作数会使得外部变量的值在0、1之间以2为周期摆动。
这道题的操作是：
```python
a = b = 0
def f(x):
    global a, b
    a = (a ^ x) & ~b
    b = (b ^ x) & ~a
```
对于同样的操作数会使得a和b两个变量总体以00->10->01->00的规律，做周期为三的变化。[An General Way to Handle All this sort of questions.](https://leetcode.com/problems/single-number-ii/discuss/43296/An-General-Way-to-Handle-All-this-sort-of-questions.)给出了一种较通用的思路解决这类问题，本质可以认为这是在做电路设计，把期望的输入和输出列出来，然后按位处理。

## 202. Happy Number
这道题之前复习C++的时候做了，使用的方法也是用set，一个小技巧是把set声明为静态变量，python中就是全局变量，这样后面的测试用例可以利用前面的计算结果。

## 001. Two Sum
是使用hashset的常规思路，建立hashmap后再遍历一遍的思路十分好像。另外，更好一点的方法是使用单边遍历结合哈希表的方法。


## 387. First Unique Character in a String
我的思路很直接，建一个Counter对象，然后顺序看字符串中的每个字符的计数，返回第一个计数为1的。但是这个时间效率和字符串长度成正比。最快的方法是常数时间的，不是遍历字符串，而是遍历字母表。要记住，对于这种元素的变化范围有限或者较小的题，针对整个元素范围做可能更好，比如桶排序。
