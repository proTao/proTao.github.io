---
title: Python 奇技淫巧 
category: 读书笔记
tags:
---

### format_map函数
print("我叫{name},我今年{age}岁了".format_map(dict(name="张勇涛",age=15)))

### print函数参数
sep=""
end="\n"
file=sys.stdout
flush=False(对文件有用，默认在文件关闭时flush)

### reversed
输入一个sequence，返回一个反向迭代器
```python
for i in reversed(range(10)):
    print(i)
```

### 协程
暂时可能不会用到这个吧。。。

### python的字典
a={True:'a',1:'b',1.0:'c'}

Python字典中的键 是否相同（只有相同才会覆盖）取决于两个条件：

1、两者的值是否相等（比较__eq__方法）。
2、比较两者的哈希值是否相同（比较__hash__方法）。

字典表达式计算结果为 {true：'c'}，是因为键true，1和1.0都是相等的，并且它们都有相同的哈希值。

### operator模块
参考[python operator模块学习](https://www.jianshu.com/p/1a3a2ae01c06)
operator模块是python中内置的操作符函数接口，它定义了一些算术和比较内置操作的函数。operator模块是用c实现的，所以执行速度比python代码快。
位操作：

    and_ 按位与
    invert 取反
    lshift(c,d) 左移位
    or_(c,d) 按位或
    rshift(d,c) 右移位
    xor(c,d) 异或

operator模块中的函数通过相应操作的标准Python接口（比如类的魔术方法）完成工作，所以它们不仅适用于内置类型，还适用于用户自定义类型。

属性和元素的getter方法

通过函数名执行对象的方法
```
class Student(object):
    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name

stu1 = Student("tom")
```

执行stu1实例的getName方法有这么几种方式：
1. stu1.getName()
2. Student.getName(stu1)
3. f = operator.methodcaller("getName");f(stu1) # f是一个无参函数执行器，接受stu对象，执行对象成员函数
4. f = operator.methodcaller("getName", Student("tom"));f(Student); # f是一个有参函数执行器，参数是一个对象实例，接受一个类，执行类成员函数
5. getattr(stu1, "getName") #得到对象的方法，直接执行就行 


### scipy.stats
统计模块
目前我用到的就是scipy.stats.binom.pmf，用来计算PMF，参数是（k，n，p）,都可以接受array-like的参数，对参数进行广播。


### bisect有序列表

### copy拷贝对象

### 区分函数作用于与闭包
参考[Python五个知识点搞定作用域](python.jobbole.com/86465)
```python
a = 1
def f1():
    print(a)

def f2():
    a = 2
    f1()

f2() # output:1
```

关键是函数在未执行之前，作用域已经形成了，作用域链也生成了。
