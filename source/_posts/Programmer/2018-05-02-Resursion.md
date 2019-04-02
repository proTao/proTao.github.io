---
title: 递归
date: 2018-05-02
category: 程序员的玩具
tags:
- algorithm
- maths
---


## Leetcode

### 344. Reverse String
注意的是要求常数空间的限制，要使用递归就会有递归栈导致的额外空间，递归栈的空间我们可以通过尾递归来消除，但是传参和返回值的部分需要额外处理。因此不能传入字符串的拷贝，只能传入指针（在python中就是不要用切片）。而且不能有返回值，要原地处理。


### 24. Swap Nodes in Pairs
递归思路很简单，注意一个小技巧是不改变节点的指针，而是通过交换节点的值完成交换。

### 118. Pascal's Triangle
在小三角形的基础上生成大三角形。

### 119. Pascal's Triangle
在已有的行的基础上生成更大的行。

### 206. Reverse Linked List
没啥

### 779. K-th Symbol in Grammar
没啥，子问题直接被规约到上一层

### 95. Unique Binary Search Trees II
子问题是生成节点数少一个的树的列表，不过为了区别在左子树和在右子树时的情况，在构造树的函数中加上一个base参数，表示从几开始构造树。

## Memorization技巧
在python中可以用`lru_cache`装饰器轻松搞定，其他的语言应该也可以用装饰器实现。注意这里的两个题，一个是`Fibonacci Number`，一个是`Climbing Stairs`，其实都有了动态规划的影子。

另外补充，在java中，LRU其实就是LinkedHashmap，即使就是一个双向链表加上HashMap。



## 主定理 Master Theorem

> 如果递归算法的递推关系符合如下形式：
> $$ T(n)=aT(\frac nb)+f(n) $$
> 其中，$$$a\ge1,b>1$$$，且f是单调递增函数。
> 那么，根据$$$f(n)$$$和$$$n^{log_ba}$$$的关系，有三种可能性：
>
> 1. 如果$$$f(n)$$$的渐进复杂度多项式级别的低于$$$O(n^{log_ba})$$$，即$$$f(n)=O(n^{log_ba-\epsilon})$$$，其中$$$\epsilon$$$是一个大于0的常数，则$$$T(n)=\Theta(n^{log_ba})$$$。
>
> 2. 如果$$$f(n)$$$的渐进复杂度多项式级别的低于$$$O(n^{log_ba})$$$，即$$$f(n)=O(n^{log_ba+\epsilon})$$$，其中$$$\epsilon$$$是一个大于0的常数，且存在$$$c<1$$$满足$$$af(n/b)≤cf(n)$$$，则$$$T(n)=\Theta(f(n))$$$。
>
> 3. 如果$$$f(n)=O(n^{log_ba}lg^kn)$$$，则$$$T(n)=\Theta(n^{log_ba}lg^{k+1}n)$$$

## 证明
![](/img/MasterTheorem1.png)
![](/img/MasterTheorem2.png)
![](/img/MasterTheorem3.png)
![](/img/MasterTheorem4.png)

## 例题




