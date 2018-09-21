---
layout: post
date: 2018-09-21
title: 快速平方根倒数计算
category: 数学
tags:
- maths
- algorithm
keywords:
description:
---

对于计算机中的数值计算来说，很多情况我们认为简单的运算对于计算机来说可能并没有那么简单。对于计算机体系结构和底层的实现，我了解的非常浅薄，这里只是为了引出Q\_rsqrt算法谈谈自己的理解。首先可以知道的是，目前来说，对于加法和移位，计算机可以高效的完成，因为这两种操作对于CPU的计算单元会有高效的硬件实现。对于减法同样可以以和加法差不多的指令周期内完成，因为数值在计算机内以补码形式形式存放，加法和减法的操作具有高度一致性。对于乘法来说，就要比加法慢上很多，因为乘法在计算机内是通过多次移位与相加组合完成的。而除法是最慢的一种基本操作，迭代的次数与惩罚差不多，但是由于额外的判断操作，其需要的指令周期数可能要是乘法的两倍甚至更多。

> (引用自[果壳网的讨论](https://www.guokr.com/question/504855/))：除法一般都是减法和移位的综合体，就像你用竖式算的一样。里面每一位要进行的判断，时间也就用得多。...... 在没有除法指令的CPU上，也是用类似的程式进行，那就慢得更加多了。在某些优化的情况下，除法可以用乘法代替，但还是比乘法慢。 ...... 因为很多处理器没有硬件除法单元。就算有硬件除法单元，也比普通运算慢。因为在硬件上除法使用的是类似CORDIC的方法（与开方、三角函数的CORDIC算法很相似，所以一般都一起共用一个单元，称为SFU），为了达到精度一般要迭代几十次的，花费数十个周期很正常。

对于通过组合四则运算与符合运算，可以进行六种基本初等函数的计算，对于幂运算可以使用快速幂算法将其计算复杂度做到O(logn)，类似的斐波那契数列也可以通过引入矩阵乘法，在对数时间复杂度内计算完毕。而对于$$$e^x$$$，常规做法是使用泰勒展开式$$$1+\frac{x}{1!}+\frac{x^2}{2!}+\frac{x^3}{3!}+...$$$进行逼近。





## 牛顿法
对于数值计算，我没有太多的研究。但是牛顿法是数值计算与优化领域一个至关重要的算法，可以用来求解极值，也可以用于求解方程的解。第一次听到这个算法是本科在《具体数学》一书中看到的，第二次是在吴恩达的CS229课程中了解到，第三次是在吴立德老师的《数值优化》课程中学习到。比如说求解$$$\sqrt{x}$$$，就可以用牛顿法来解，将问题转化为$$$x^2-a=0$$$的求解，a是给定的数值。

![](/img/Q_rsqrt1.jpg)

这道题是Leetcode中的[一道题](https://leetcode.com/problems/sqrtx/description/)，可以直接使用上面的思路来解决。
```python
from math import floor
class Solution:
    def mySqrt(self, x):
        """
        :type x: int
        :rtype: int
        """
        threshold = 1e-6
        r = x
        while r*r > x:
            new_r = (r + x/r) / 2
            if abs(new_r-r) < threshold:
                break
            r = new_r
        return floor(r)
```

对于求解平方根的倒数这个问题，同样可以使用上述牛顿法，只不过代理函数为$$$f(x)=\frac{1}{x^2}-a$$$，用牛顿法迭代的解该函数的零值即可。注意代理函数不止一个，使用这个代理函数的优势在于迭代公式有效地避免了除法的计算。
$$x_{n+1}=x_n*(1.5-\frac{a*x_n^2}{2})$$


## 快速解法
对于牛顿法需要不停迭代直到误差收敛，而Quake Engine的作者显然不想这么干。图形引擎中由于需要计算方向向量，需要对一个向量除以自身的模，因此底层需要大量的平方根倒数的运算，在Quake Engine中出现了下面这种高效的优化的代码，能够不需要迭代的计算该函数。
```cpp
float Q_rsqrt( float number )
{
    long i;
    float x2, y;
    const float threehalfs = 1.5F;

    x2 = number * 0.5F;
    y  = number;
    i  = * ( long * ) &y;                       // evil floating point bit level hacking
    i  = 0x5f3759df - ( i >> 1 );               // what the fuck?
    y  = * ( float * ) &i;
    y  = y * ( threehalfs - ( x2 * y * y ) );   // 1st iteration
//    y  = y * ( threehalfs - ( x2 * y * y ) );   // 2nd iteration, this can be removed

    return y;
}
```
注意到其中最后两行代码就是按照牛顿法的迭代方式计算的，但是为什么之计算了一次？原因在于初值给的好...上面那条你一上来肯定看不懂的代码，就是作者的骚操作，通过这个骚操作，初值就已经是答案的粗略逼近了，之后使用牛顿法就可以高速收敛，源码中甚至将第二次的迭代都给注释掉了。

[揭秘·变态的平方根倒数算法](https://segmentfault.com/a/1190000006170378)这篇文章已经解释的非常好了，我在加上一些自己的思考。

首先注意` i  = * ( long * ) &y;`这个步骤是按位赋值，其实就是将一个float的32位比特解释为int。懒得码字了，后面的推导我就写在草稿纸上了。

![](https://upload.wikimedia.org/wikipedia/commons/0/0d/Float_w_significand_2.svg)

![](/img/Q_rsqrt2.png)
![](/img/Q_rsqrt3.jpg)

在推导 2 中我写了计算的流程图，右下角的那个式子就是对$$$log\frac{1}{\sqrt x}$$$的估计值，将其带入到$$$I_r$$$的表达式中，大量的项可以合并，最后得到：
$$I_r=3×(127-\epsilon)×2^{22}-\frac{I}{2}$$

其中 $$$\epsilon$$$ 是在用 $$$B+\epsilon$$$ 估计 $$$log(1+B)$$$ 引入的，为了使估计的误差最小，可以得到 $$$\epsilon$$$ 的最优值为0.043035，将其带入，可以直接得到 $$$I_r$$$ 与 $$$I$$$的对应关系为：
$$I_r = 0x5f3759df - \frac{I}{2} $$
然后直接把 $$$I_r$$$ 用 float 类型解释就可以得到结果的粗略估计了。还有一些补充内容看参考文章就可以了，我在这里给出我用Python的模拟代码，效率肯定是不高的，就是为了帮助理解。

```python
class Float32:
    """
    sign bin : 1 bit and aways 0
    expo bins : 8 bits
    base bins : 23 bits
    """
    def __init__(self, x=1):
        assert x > 0
        self.val = x
        self.expo = 0
        self.base = None
        while not 1 <= x < 2:
            if x >= 2:
                x /= 2
                self.expo += 1
            else:
                x *= 2
                self.expo -= 1
        self.expo = "{:0>8}".format(bin(127+self.expo)[2:][-8:])
        self.base = "{:0<23}".format(self._dec2bin(x))

    def _setBits(self, bits):
        assert len(bits) == 32
        self.expo = bits[1:9]
        self.base = bits[9:]
        self.val = 2**(int(self.expo,2)-127)*(1+1/int(self.base[::-1], 2))


    def __str__(self):
        return "Float32: {} [0 {} {}]".format(self.val, self.expo, self.base)

    def _dec2bin(self, x):
        x -= int(x)
        bins = []
        while x:
            x *= 2
            bins.append('1' if x>=1.0 else '0')
            x -= int(x)
        return "".join(bins)

    def toInt32(self):
        i = Int32()
        i._setBits('0' + self.expo + self.base)
        return i

    def __mul__(self, x):
        if type(x) in (Float32, Int32):
            return Float32(self.val * x.val)
        else:
            return Float32(self.val * x)

    def __add__(self, x):
        if type(x) in (Float32, Int32):
            return Float32(self.val + x.val)
        else:
            return Float32(self.val + x)

    def __sub__(self, x):
        if type(x) in (Float32, Int32):
            return Float32(self.val - x.val)
        else:
            return Float32(self.val - x)

class Int32:
    def __init__(self, x=1):
        self.bits = "{:0>32}".format(bin(x)[2:])

    def _setBits(self, bits):
        self.bits = bits


    @property
    def val(self):
        return int(self.bits, base=2)

    @val.setter
    def val(self, _val):
        self.bits = "{:0>32}".format(bin(_val)[2:])

    def toFloat32(self):
        f = Float32()
        f._setBits(self.bits)
        return f

    def __str__(self):
        return "Int32: {}, [{} {} {}]".format(self.val,\
                                        self.bits[0],\
                                        self.bits[1:9],\
                                        self.bits[9:])
    def __rshift__(self, x):
        i = Int32()
        i._setBits('0' + self.bits[:-1])
        return i

    def __sub__(self, x):
        if type(x) in (Float32, Int32):
            return Int32(self.val - x.val)
        else:
            return Int32(self.val - x)

    def __add__(self, x):
        if type(x) in (Float32, Int32):
            return Int32(self.val + x.val)
        else:
            return Int32(self.val + x)

    def __mul__(self, x):
        if type(x) in (Float32, Int32):
            return Int32(self.val * x.val)
        else:
            return Int32(self.val * x)


def Q_rsqrt(number):
    number = Float32(number)
    x2 = number * 0.5
    y  = number
    i  = y.toInt32()                # evil floating point bit level hacking

    i  = Int32(0x5f375a86) - ( i >> 1 )               # what the fuck?
    y  = i.toFloat32()
    for i in range(3):
        y  = y * ( Float32(1.5) - ( x2 * y * y ) )   # 1st iteration
        # y  = y * ( Float32(1.5) - ( x2 * y * y ) )   # 2nd iteration, this can be removed
    return y.val

x = 0.15625
print(Q_rsqrt(x))
print(1/x**0.5)

```


### 参考
1. [Methods of computing square roots](https://en.wikipedia.org/wiki/Methods_of_computing_square_roots)
2. [Fast inverse square root](https://en.wikipedia.org/wiki/Fast_inverse_square_root)
3. [计算机对加减乘除的计算时间的对比](https://blog.csdn.net/weixin_39752599/article/details/78852033)
4. [揭秘·变态的平方根倒数算法](https://segmentfault.com/a/1190000006170378)
