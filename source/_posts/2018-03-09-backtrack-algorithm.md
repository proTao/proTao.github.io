---
title: backtrack-algorithm
date: 2018-03-09 16:57:25
category: Programmer
tags: algroithm
---

在程序设计中，有相当一类求一组解，或求全部解或求最优解的问题，例如读者熟悉的八皇后问题，不是根据某种特定的计算法则，而是利用试探和回溯的搜索技术求解。回溯法也是设计递归过程的一种重要方法，它的求解过程实质上是一个先序遍历一棵"状态树"的过程,只是这棵树不是遍历前预先建立的,而是隐含在遍历过程中。

---《数据结构》(严蔚敏)

关键思想: 不满足条件就不进入分支
关键变量: path,用path很简洁，但是一个影响思路的地方就是“回溯在哪里”这个问题变得模糊了，因为回溯出现在下层函数返回上层函数过程中，局部变量作为函数环境的自动恢复，如果把path设置为全局变量，那么就需要在进入函数前和返回函数后手动改变全局变量，那样的话思路就会清晰

beautiful arrange中用到了cache

题目进阶：
permutation
letterpermutaion
permutation2



77 Combination 使用递归的数学公式更快，使用备忘录技巧还能更快

备忘录技巧：
77 Combinations
526 BeautifulArrange
22 Generate Parentheses（在这里备忘录技巧没有特别突出的改进，只是提供一种思路）
```
In [1]: from timeit import timeit

# 然后把两个函数定义出来

In [16]: def test(x,n):
    ...:     print("not use cache:",timeit(setup="from __main__ import generateParenthesis",stmt="generateParenthesis("+str(x)+")", number=n)/n)
    ...:     print("use cache", timeit(setup="from __main__ import generateParenthesis2",stmt="generateParenthesis2("+str(x)+")", number=n)/n)
    ...:     
    ...:     

In [17]: test(12,50)
not use cache: 0.22083879192000042
use cache 0.20065379500000063

```

指数题目：
89 GrayCode
784 LetterCasePermutation
78 Subsets

启发式规则
93 Restore IP Addresses
212 Word Search 2（本来应该用trie的结构，然而使用了一些启发式规则，在最后的提交结果中运行时间还是很短，然而这是根据测试用例针对性的提出的）
401 binary watch (不要过度剪枝，规则复杂，不易维护)


排序冗余路径（路径上的元素无序）：
39 Combinaion Sum
77 Combinations

路径上元素重复，但是有使用次数
40 combination sum II
47 Permutation II(这道题还不错，考虑到重复元素，以及不重复的解)



**357 Count Numbers with Unique Digits 这道题做的很丑陋**


# 问题
为什么全局变量是数组，deeper可以找到，可是全局变量是int时找不到
