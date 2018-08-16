---
layout: post
date: 2018-08-16 19:55:33
title: 从优先队列到贪心算法
category: 程序员的玩具
tags: algorithm
---


---

## 优先队列

### 需求

在算法设计中，我们常有求一个容器中的最小值或最大值的需求。比如求一个有100万(后面用N表示总元素数目)的元素的数组中的最大值，我们会只维护当前最大值，然后遍历数组中的每一个元素并更新最大值。那么，如果需要求前K大元素或者第K大元素，（为了方便思考，可以简单的假设K=10）。如果用排序的方法解决该问题就会显得太过臃肿，O(nlogn)的时间复杂度暂且不提，如果使用内部排序，更要付出能存下整个数组的存储代价。那么简单的扩展求最大值的方法，只维护K个变量，然后从头遍历数组，每次拿到一个新的元素就更新当前的K个变量。如果用数组存放这k个元素，此时的时间复杂度是O(KN)。这时我们实际上是一直保持这K个元素有序的，再次放宽限制，如果只需要知道前K个元素是哪K个的话，每次只需要用最小的元素和新来的元素比就行，比最小的元素大的话就有了被我们维护的资格，把它加入容器并踢出最小元素就可以了。

<!-- more -->


除了这种简单的情况，比如后面的一些常用的贪心算法，或者操作系统内部进行任务调度的时候经常遇到需要拿到最小元素的需求。通常来说，满足该需求的该数据结构至少需要有添加，取最小值，删除最小值的操作接口。最简单的实现方法无非就是前面说的用一个数组。但是数组是不能避免某一项操作是O(n)的时间复杂度的，无论是让数组有序还是无序。

维护一个树形结构是一个可行的思路。堆的基本概念就不具体展开了。对于堆实际上还有很多的优化，比如对于合并操作继续优化的话，可以得到二项式堆。各自操作的时间效率如下表。

![](/img/PQ1.png)

### 最大堆的基本操作
假设堆的存储结构由数组实现，因为堆的树形结构满足紧凑的完全二叉树，

- push：将元素加入数组尾，然后上浮。
- pop：将堆顶元素与数组尾元素交换，pop数组尾元素进临时变量，将堆顶元素下沉，然后返回临时变量。
- minElement：O(1)，直接返回堆顶。
- up：O(logn), 将下层的较大元素与其父节点进行交换
- down：O(logn), 将上层的较小元素与其较大的孩子节点进行交换


### 建堆 

### 堆排序
有了上面的优先队列的思想后，可以想到，堆排序其实是选择排序的简单扩展。只需要将数组初始化为堆，然后把不断的执行选择最小元素即可。注意的是把选出的元素放到堆的数组尾部，然后让堆不再维护该部分即可。


### 例题：LC215. Kth Largest Element in an Array
见另一篇博客。


### 高级结构

#### Binomial Heap（二项堆）
未完待续


#### 斐波那契堆
未完待续

#### IndexMinHeap

```python
class MinHeap:
    def __init__(self):
        self.N = 0
        self.pq = [None]

    def isEmpty(self):
        return self.N == 0

    def size(size):
        return self.N

    def insert(self, key):
        print("IndexMinHeap Insert", index)
        self.N += 1
        self.pq.append(key)
        self._swim(self.N)

    def delMin(self):
        self._exch(1, self.N)
        self.N -= 1
        res = self.pq.pop()
        self._sink(1)
        return res

    def _comp(self, i, j):
        return self.pq[i] > self.pq[j]

    def _exch(self, i, j):
        self.pq[i], self.pq[j] = self.pq[j], self.pq[i]

    def _swim(self, k):
        while k > 1 and self._comp(k>>1, k):
            self._exch(k>>1 , k)
            k = k>>1

    def _sink(self, k):
        while k << 1 <= self.N:
            j = k << 1
            if j < self.N and self._comp(j, j+1):
                j += 1
            if not self._comp(k, j):
                break
            self._exch(k, j)
            k = j

    def __str__(self):
        return str(self.pq[1:])

class IndexMinHeap(MinHeap):
    def __init__(self):
        self.keys = {}
        self.qp = {}
        MinHeap.__init__(self)


    def contains(self, index):
        return index in qp

    def insert(self, index, key):
        """
        index: name or index
        key: weight, the value used to compare in the heap
        """
        print("IndexMinHeap Insert", index, "with weight", key)
        self.N += 1
        self.pq.append(index)    # position -> index
        self.qp[index] = self.N  # index -> position
        self.keys[index] = key # index -> weight
        self._swim(self.N)

    def delMin(self):
        self._exch(1, self.N)
        indexOfMin = self.pq.pop()
        self.N -= 1
        self._sink(1)
        del self.keys[indexOfMin]
        del self.qp[indexOfMin]
        return indexOfMin

    def change(self, index, key):
        self.keys[index] = key
        self._swim(self.qp[index])
        self._sink(self.qp[index])


    def keyOf(self, index):
        return self.keys[index]

    def delete(self, index):
        i = self.qp[index];
        self.n -= 1
        self._exch(i, self.n);
        self._swim(i);
        self._sink(i);
        self.keys[index] = null;
        self.qp[index] = -1;

    def show(self):
        print("最近节点", a.minIndex())
        print("最近距离", a.minWeight())
        print([(i, self.keys[i]) for i in self.pq[1:]])
        print("pq", self.pq)
        print("qp", self.qp)


    def _comp(self, i, j):
        return self.keys[self.pq[i]] > self.keys[self.pq[j]]

    def _exch(self, i, j):
        self.pq[i], self.pq[j] = self.pq[j], self.pq[i]
        self.qp[self.pq[i]] = i
        self.qp[self.pq[j]] = j;



    def minWeight(self):
        return self.keys[self.pq[1]]

    def minIndex(self):
        return self.pq[1]

if __name__ == "__main__":
    a = IndexMinHeap()
    a.insert('a', 5)
    a.insert('b', 3)
    a.insert('c', 6)
    a.insert('d', 2)
    a.show()
    print(a.keyOf('a'))



    a.change('a', 1)
    a.show()
    print(a.keyOf('a'))

    print("delete the nearlest node")
    print(a.delMin())

```


### 与算法的结合

#### Prim算法

#### Dijkstra算法



* * *
参考：
1. [java 实现的索引最小堆](https://algs4.cs.princeton.edu/24pq/IndexMinPQ.java.html)
2. 《算法（第四版）》
3. 《算法十八讲》卜东波
