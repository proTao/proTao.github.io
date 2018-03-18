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

实际上可以认为回溯法是一种启发式的贪心算法，启发规则是DFS的试探前进，而DFS的方法目前刷题来看常用的是先序和后序，先序的话是一种分治的思想，后续也是分治，但是更突出归并的特点。但是就像前面说的分治法在递归公式的拆分下问题划分的斩钉截铁，而回溯法则是小心翼翼一直为自己保留退路。这么看的话利用公式的组合数那道题其实是后序DFS解法

从编程上看，我习惯的回溯法不需要返回值，只是需要在deeper函数中传递当前状态，解保存在外部变量中，而后序DFS常常需要定义返回值，通过逻辑表达式和if/else三目运算符可以使代码非常简练，但是可读性会一定程度的变差



## 实现中的python tips
1. （104. Maximum Depth of Binary Tree）使用`x is None`来判断x是不是None，==是判断值的，is是判断引用的，两个列表内容一致==就会返回True，而所有的None都是引用None常量。使用sys.getrefcount查看引用计数。假设x是一个有val属性的对象，但是x可能是None，print(x and x.val)能够在x存在时输出x的值，否则输出None。对于and表达式的规则，总结为：x or y 的值只可能是x或y.  x为真就是x, x为假就是y。x and y 的值只可能是x或y.  x为真就是y, x为假就是x
2. (111. minimum depth of binary  tree) 最大正整数是啥
3. (112. Path Sum) 当逻辑表达式中的元素可能为None时，在逻辑表达式后面放一个默认值，比如这道题中的`root.left and deeper(root.left, current_sum+root.left.val) or root.right and deeper(root.right, current_sum+root.right.val)`这个表达式，如果root的左节点存在但是递归返回False，右节点不存在，此时表达式直接被短路，返回None，因此一定要在后面加上一个or False作为默认值，但是假设逻辑表达式的各个元素一定是True或者False的话就没有关系。
4. (513. Find Bottom Left Tree Value) 注意最后的return表达式，在and/or的逻辑表达式中，注意运算优先级，if/else三目运算符的优先级更高，所以要加上括号。
5. (756. Pyramid Transition Matrix) 在[永远别写for循环](http://python.jobbole.com/87832/)一文中，提到的很多替代for循环的方法，当然Python代码的风格不是为了简练而简练，核心要义是**优美胜过丑陋，显式胜过隐式**，还有**扁平胜过嵌套**，因此如果写出了一层一层的for循环还有if、else语句，真的很不python。这道题中，需要通过for循环对一个列表中的符合条件的每个元素进行处理，这种时候可以使用带if的列表生成式来代替。
6. (105. Construct Binary Tree from Preorder and Inorder Traversal) 在之前的Backtrack的题目中大部分我都是直接在path的基础上切片或用加法操作生成一个新数组进行传参，这道题的话一个加速的手段就是把inorder中的值和下标建立索引，然而如果每次生成新的子列表的话，这个索引就不能用了，所以改为传递新的子数组在原数组中的左右界，这样减小了每次传参时建立新数组的开销，也能重复利用下表索引，这个技巧对于C程序员应该是驾轻就熟的。
