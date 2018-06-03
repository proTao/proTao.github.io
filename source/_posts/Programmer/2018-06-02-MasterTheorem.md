---
title: 时间复杂度分析的主定理
date: 2018-06-02
category: 程序员的玩具
tags:
- algorithm
- math
---

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




