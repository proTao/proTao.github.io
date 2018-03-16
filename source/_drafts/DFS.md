---
title: DFS
category:
tags:
---


## 实现中的python tips
1. （104. Maximum Depth of Binary Tree）使用`x is None`来判断x是不是None，==是判断值的，is是判断引用的，两个列表内容一致==就会返回True，而所有的None都是引用None常量。使用sys.getrefcount查看引用计数。假设x是一个有val属性的对象，但是x可能是None，print(x and x.val)能够在x存在时输出x的值，否则输出None。对于and表达式的规则，总结为：x or y 的值只可能是x或y.  x为真就是x, x为假就是y。x and y 的值只可能是x或y.  x为真就是y, x为假就是x
