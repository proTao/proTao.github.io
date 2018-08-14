### 662. Maximum Width of Binary Tree *bangbang*
一上来的思路就是层次遍历，一开始用的是`deque`，这样的话就要自己往里面加分隔符，确定宽度。还有就是遇到空节点也不能停，要接着向队列里面压入两个空节点，然后每一层结束时判断最左非空节点和最右非空节点之间的节点数。
然后超时了。。。看了一下调用栈，就是空节点太多了，然后转回溯法试了一下，还是没能解决空节点的问题。注意的是每一层最左非空节点的左边的节点都不用考虑，右边的同理，然后用了两个数组进行层次遍历，然后加了一些小trick，每层最左最右的空节点直接跳过，勉勉强强的AC了，代码最后也是很丑陋。
然后看了top1的代码。。。思路真的很巧妙。。一开始我也往这边想了，就是贴着两边找，但是不知道怎么确定位置。位置这点怎么能没想到呢，刚刷完堆的题，对于完全二叉树，每个节点的紧凑表示后的位置是确定的啊！那然后给每个节点一个编号，然后随意遍历这棵树，看同一层中的编号的差值就好了。
现在觉得棒棒，多刷刷可能就好了。树的核心思想就是那几个遍历，这道题其实没有脱离框架的。


### 637. Average of Levels in Binary Tree
做完662看到了669然后没有思路，然后觉得这道题好欺负就做这道题了。层次遍历，双数组，挺简单的。需要区分层次的时候感觉双数组加上一个指示变量这种方法挺好的，要是用一个队列的话需要处理层次的问题。用两个数组加上指示变量，每次换层次的时候的代价是指示变量变一下，current模拟指针改变指向，然后当前层数组clear一下，应该是常数级别的操作还不需要额外空间。
要是有更好的方法会更新这个方法的，目前来看就先用这个吧。

### 669. Trim a Binary Search Tree
昨天晚上困了看了这道题没思路，今天一早做这道题，仔细一琢磨倒是不难，就是递归。但是我用递归做完之后发现效率好低，琢磨有没有优化的方法。
捉摸了一下没想出来，看了top1的代码，思路没有大问题，又跑了一次，就打败100%了。。

### 226. Invert Binary Tree
典型题。

### 559. Maximum Depth of N-ary Tree
数据结构不能用leetcode自带的辅助函数初始化了，算法倒是不难。用backtrack，实际上是DFS，在对象里保存最大深度即可。

### 653. Two Sum IV
结合前面几种Two Sum问题，原始的问题在官方Solution中给了三种解法，可以两次遍历，可以使用HashTable加上Two Pass，更好的就是HashTable加上One Pass。另外一种问题的变形是有序的输入求解TwoSum问题，那可以用双指针来解决。这道题考虑能使用哪种方法，双指针的不行，因为树不能没有代价的从孩子节点找到父节点，那就使用OnePass加上HashTable解决，然后用基于循环的dfs进行遍历。

### 606. Construct String from Binary Tree
明显是一个先序遍历，没什么算法上的难度，就是逻辑理清了就行，主要看右节点有没有。右节点中存在，左节点一定加括号。右节点为空时，左节点非空时加括号。

### 590. N-ary Tree Postorder Traversal
没啥

### 404. Sum of Left Leaves
没啥。

### 538. Convert BST to Greater Tree
题目没啥，倒着中序遍历就行。用非递归的中序遍历来做可能更好，顺便用这道题复习非递归的中序遍历。然后还看到了一种**Morris遍历法**，不需要额外空间，下一题实现一下。

### 563. Binary Tree Tilt
后序遍历，用递归法是没有啥问题的，我想尝试用迭代的方法做这道题，没做出来。直接用迭代方式实现了一些树的迭代器在treetools中。

### 429. N-ary Tree Level Order Traversal
没啥

### 700. Search in a Binary Search Tree
没啥

### 543. Diameter of Binary Tree
没啥

### 589. N-ary Tree Preorder Traversal
没啥

### 107. Binary Tree Level Order Traversal II
没啥

### 671. Second Minimum Node In a Binary Tree
没啥

### 437. Path Sum III *bangbang*
关键是弄出了一个函数，计算以当前点为起点的解。

### 572. Subtree of Another Tree
我的思路是，两个树根节点一样就看看是不是一棵树，不一样就进s的左子树和t比，或者进s的右子树。

### 235. Lowest Common Ancestor of a Binary Search Tree
深度遍历，找到节点时保存各自的路径，然后返回最后一个相同的节点。但是注意是BST，直接可以选择进哪个节点。

### 501. Find Mode in Binary Search Tree
中序遍历得到非严格单增序列。

### 687. Longest Univalue Path
没啥