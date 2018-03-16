---
title: DFS
category:
tags:
---


与回溯法的区别：
就目前做的 104 Max Depth of Binary Tree 和 690 Employee Importance 两道easy来看，DFS适用于求标量情况，写成从子节点向上规约的算法，代码及其简洁。而回溯法不受限于求标量，也可以枚举所有解等情况，这种时候回溯法更加适合，但是从代码上来看要较复杂一些，回溯法是一种自顶向下探索的方法。


## 实现中的python tips
1. （104. Maximum Depth of Binary Tree）使用`x is None`来判断x是不是None，==是判断值的，is是判断引用的，两个列表内容一致==就会返回True，而所有的None都是引用None常量。使用sys.getrefcount查看引用计数。假设x是一个有val属性的对象，但是x可能是None，print(x and x.val)能够在x存在时输出x的值，否则输出None。对于and表达式的规则，总结为：x or y 的值只可能是x或y.  x为真就是x, x为假就是y。x and y 的值只可能是x或y.  x为真就是y, x为假就是x

