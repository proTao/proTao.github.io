---
layout: post
date: 2018-10-01
title: LeetCode刷题笔记——BinarySearch
category: 程序员的玩具
tags:
- algorithm
---

这部分在国庆前完成的，大师国庆这天才释放出来，给自己的假期增加一点工作量。。。

### 744. Find Smallest Letter Greater Than Target
这道题在面试中见到了，当时回答得可真是渣渣啊。这次结合了**循环不变量**的思路去做这道题，主要的思想就是搜索区间的循环不变量是**想要找的元素一定在区间内**。这就使得和正常的二分搜索出现了一些小的区别，当支点等于target时，我还要向右搜索，当支点大于target时，我要向左搜索，但是要把当前支点放在区间内，然后当区间元素个数为两个时可能区间不能在缩小，然后就自左向右顺序搜索区间，返回第一个比target大的元素，如果没有，就返回第一个元素。

然而Solution中给了格外Pythonic的代码：
```python
class Solution(object):
    def nextGreatestLetter(self, letters, target):
        index = bisect.bisect(letters, target)
        return letters[index % len(letters)]
```

<!-- more -->


### 852. Peak Index in a Mountain array
没啥的，题目设置的就是为了了BS准备的。

### 367. Valid Perfect Square
没啥，是使用二分查找实现开根号的简单版本。

### 441. Arranging Coins
这个我的思路是有一个隐含的数组f，f[i]表示i层硬币需要的硬币总数，比如f[1]是1，f[2]是3等等等等，那么这道题要做的就是在f数组中找到小于等于n的最大元素的下标，那思路就比较清晰了，不过注意的是我们不需要真的把f全部计算出来放到数组中，f是一个函数就可以。

然后这道题其实最简单的模拟法就可以高效地解决， 思路就是尝试摆一下，看看最多摆多少层。
```python
def Arrange(n):
    i = i
    while n >= i:
        n -= i
        i ++
    return i - 1
```
另外使用f的逆函数也可以解决。这道题就是开阔一下思路，明确二分查找不只只是用在数组中，后面的难一些的题中会有更多的这种使用方法。

### 374. Guess Number Higher or Lower
没啥

### 704. Binary Search
维持循环不变量是不管target在不在搜索区间内，target一定要大于等于区间的最左元素，小于等于区间的最右元素。这样的话，在开始和每次调整区间的时候要进行循环不变量的合法性检查，代码量要多一些可以可读性比较强。最基本的binarySearch是没有这种检查的：
```python
def search(nums, target):
    i = 0
    j = len(nums)
    while i<j:
        mid = (i+j)//2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            i = mid + 1
        else:
            j = mid
    return -1
```
这种写法的循环不变量其实就是“如果target在nums中，就一定在区间内”。

### 475. Heaters [bangbang]
这道题做着不像是easy的题啊......其实看了看Discussion中的接发还挺直观，先排序，然后找到每一个房子的左临近的heater和右临近的heater，这里可以使用BS。然后计算到左右heater的较小距离作为该房子的加热半径，然后计算所有房子的加热半径的最大值。时间复杂度嘛，假设houses的长度是m，heaters的长度是n，那么复杂度分析应该是$$$O(mlogm)+O(nlong)+O\big(m(logn+1)\big)$$$。

这个我没有实现，我的思路是比较奇怪的。认为r是一个被搜索的数值，搜索范围是0到加热器到房子的最远距离。这里可以使用二分搜索，我们要找的是满足覆盖需求的最小的r。这里判断是否满足覆盖需求需要一个valid函数，这个函数的作用就是判断当前的r能否足以让每个房子都被加热到。做法是找到某个加热器的最远能覆盖到的两个房子，并使用bs找到这两个房子的位置，然后判断所有的房子能否都被覆盖到。时间复杂度是：$$$O(mlogm)+O(nlong)+O\big(log(m+n)×(2logm+1)\big)$$$。其中，前两个复杂度依然是来自于排序，第三个复杂度来自于运行了多次valid函数，次数与heater与house的最远距离成对数关系，每个valid内部主要操作是运行了两次对house的二分查找，还有一些常数级别的操作。

### 240. Search a 2D Matrix II [bangbang]
从右上角开始进行搜索，被搜索的元素只可能存在于以当前位置为右上角的矩形范围内，当前位置上方的比当前元素小，右方的比当前元素大。如果到了某一个位置矩形内没有元素了，那说明search失败。可以线性查找，首先向下找找到比当前元素大的第一个元素，然后向左找找到比当前元素小的第一个元素，不断循环。这样的话是$$$O(mn)$$$，由于行内和列内有序，因此通过使用BS可以将时间复杂度可以降低为$$$O(logmlogn)$$$。

### 278. First Bad Version
没啥

### 528. Random Pick with Weight
离散分布采样，就是一个轮盘赌算法，在我的另一篇关于采样的文章中有所介绍，不过当时的实现不是基于二分搜索的，就是直接顺序搜索。还有就是像这种情况直接用`bisect`就好了，没有必要每次都自己写。

### 875. Koko Eating Bananas [bangbang]
这道题就是在函数空间内进行二分搜索，找到符合“条件”的最小的数，对于“条件”我们可以简单的编写一个lambda表达式就行，此时这道题其实就变成了278了。为了使用上bisect包，我把lambda表达式封装成了一个类，并且重写了这个类的`__len__`和`__getitem__`方法，这样的话可以使用bisect了，但是注意，bisect只能在升序的列表中进行二分查找。

### 74. Search a 2D Matrix
这个2D的矩阵按行主序摊平就是一个有序数组，那么我要做的就是写一个映射，将一维的索引映射为2维的索引，然后通过这个索引变换函数像一维数组一样访问二维数组。有了这个之后就只需要一个简单的常规的BinarySearch就可以了。

### 162. Find Peak Element
尽管是medium，但是感觉和easy的852没有区别。

### 436. Find Right Interval
其实每个interval的end，就是一个要被搜索的值，我们要做的是在一大堆start中找到一个大于等于end的最小的start。沥青这个思路，那么把start排序二分搜索就行了。但是排序过程中为了保留住位置信息，直到那个被选中的interval是第几个interval，我把position和start打包成一个tuple，start在前，因为题目中说了没有两个一样的start，因此直接用tuple的比较规则就好，只不过这样要花二倍的比较时间，每次要多做一个比较，也可以打包排序后再把位置信息拆出来。

### 275. H-Index II
找到满足条件的最大的数，把条件定义出来，然后BS就行。一开始是对数组进行filter，然后这样超时了，现在变成先用Counter处理一下，之后对Counter得到的字典进行filter就快了。

但是看别人的提交中，直接的线性搜索更快：
```python
class Solution:
    def hIndex(self, citations):
        """
        :type citations: List[int]
        :rtype: int
        """
        h =0
        if not citations:
            return 0
        for i in range(len(citations)-1,-1,-1):
            if citations[i]> h:
                h +=1
            else:
                return h
        return h
```

然后发现我的想法太多拘泥于在函数空间内进行二分搜索这个思路了，不能手中有了锤子，看什么都像钉子。这个是更简洁也是更直接的BS解法，条件就是判断是否`citations[mid]>=len(citations)-mid`，不等号左侧是引用量，右侧是大于等于这个引用量的文章数。能这么做是因为数组已经有序。
```python
class Solution:
    def hIndex(self, citations):
        start,end=0,len(citations)-1
        while start<=end:
            mid=(start+end)//2
            if citations[mid]>=len(citations)-mid:
                end=mid-1
            else:
                start=mid+1
        return len(citations)-start
```
### 658. Find K Closest Elements
这道题需要的输出是一个长度为Ｋ的区间，我的思路是使用BS找到最近的那个点，作为Ｋ区间的右端点，然后令该点左边相邻的点作为K区间的左端点，然后不断向外扩张直到长度为K。这么做也行也能过但是效率不高，因为时间复杂度中多了一个O(K)。
在别人的方法中看到一个思路，就是一开始就有一个长度为K的区间，这个区间的长度一直都是K我们使用二分搜索调整它的位置。
```python
def findClosestElements(arr, k, x):
    left, right = 0, len(arr)-k
    while left + 1 < right:
        mid = (left+right)//2
        if abs(x-arr[mid]) > abs(arr[mid+k]-x):
            left = mid
        else:
            right = mid
    if left < right:
        if abs(x-arr[left]) > abs(arr[left+k]-x):
            left += 1
    return arr[left:left+k]
```

### 33. Search in Rotated Sorted Array
这道题是之前做的，旧的思路是找到最大值，也就意味着找到了旋转支点，然后判断在左边还是在右边，用常规的ＢＳ就可以。然后这次看到这道题觉得可以一遍BS就找到，就是区间左值一定比右值大，否则直接就用常规BS,然后根据target和mid的关系就可以判断往左还是往右，但是没有实现，只是一个可能的思路。

### 081. Search in Rotated Sorted Array II
TODO

### 29. Divide Two Integers
我的思路就比较常规，正常的二分搜素。在别人的提交中找到了一个表较好的解法：
```python
class Solution:
    def divide(self, dividend, divisor):
        """
        :type dividend: int
        :type divisor: int
        :rtype: int
        """
    a = dividend
    b = divisor
    if not b:
        return []
    if not a:
        return 0
    if (a == -2147483648) and (b == -1):
        return 2147483647
    s1, s2 = 1, 1
    if a < 0:
        a, s1 = -a, -1
    if b < 0:
        b, s2 = -b, -1
    count = 0
    while b <= a:
        temp = b
        mul = 1
        while (temp + temp) < a:
            temp = temp + temp
            mul = mul + mul
        count = count + mul
        a = a - temp
    if s1 != s2:
        count = -count
    return count
```
这个其实是用一堆2的指数解除法问题，比如15除以2，其实是可以拆解为8/2+4/2+2/2+1/2=4+2+1。这样的话时间复杂度应该是$$$\sqrt n$$$。


### 497. Random Point in Non-overlapping Rectangles
没啥，在一个混合生成式模型中采样，只需要单独进行先验概率和条件概率的采样就行。


### 410. Split Array Largest Sum [bangbang]
https://blog.csdn.net/MebiuW/article/details/52724293
