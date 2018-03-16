---
title: DFS
category:
tags:
---


与回溯法的区别：
就目前做的 104 Max Depth of Binary Tree 和 690 Employee Importance 两道easy来看，DFS适用于求标量情况，写成从子节点向上规约的算法，代码及其简洁。而回溯法不受限于求标量，也可以枚举所有解等情况，这种时候回溯法更加适合，但是从代码上来看要较复杂一些，回溯法是一种自顶向下探索的方法。
用栈来代替的方式替代递归

涉及最短路径的时候，回溯法与BFS更有优势

题目（112. Path Sum）表现了DFS的另外一种可能性，Backtrack方案每一步都是试探性的，而DFS更有一种破釜沉舟的感觉，该节点不对之后直接划分为子问题，这个也许是更根本的区别，而自顶向下和自底而上的区别不那么明显了，自底向上其实也是干净利落的划分问题，父节点直接采用子节点返回的值。

## 实现中的python tips
1. （104. Maximum Depth of Binary Tree）使用`x is None`来判断x是不是None，==是判断值的，is是判断引用的，两个列表内容一致==就会返回True，而所有的None都是引用None常量。使用sys.getrefcount查看引用计数。假设x是一个有val属性的对象，但是x可能是None，print(x and x.val)能够在x存在时输出x的值，否则输出None。对于and表达式的规则，总结为：x or y 的值只可能是x或y.  x为真就是x, x为假就是y。x and y 的值只可能是x或y.  x为真就是y, x为假就是x
2. (111. minimum depth of binary  tree)最大正整数是啥
3. (112. Path Sum)当逻辑表达式中的元素可能为None时，在逻辑表达式后面放一个默认值，比如这道题中的`root.left and deeper(root.left, current_sum+root.left.val) or root.right and deeper(root.right, current_sum+root.right.val)`这个表达式，如果root的左节点存在但是递归返回False，右节点不存在，此时表达式直接被短路，返回None，因此一定要在后面加上一个or False作为默认值，但是假设逻辑表达式的各个元素一定是True或者False的话就没有关系。

