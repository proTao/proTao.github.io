---
layout: post
date: 2019-04-17
title: Python Cookbook3 (12) 并发编程
category: 读书笔记
tags:
- reading
- python
keywords:
description:
---

![](/img/python3_cookbook_cover.png)

并行计算环境中的正确性有两个标准。第一个是,结果应该总是相同。第二个是,结果应该和串行执行的结果一致。当一个进程在程序的临界区影响另一个进程时,并行计算中就会出现问题。这些都是需要执行的代码部分,它们看似是单一的指令,但实际上由较小的语句组成。一个程序会以一系列原子硬件指令执行,由于处理器的设计,这些是不能被打断或分割为更小单元的指令。为了在并行的情况下表现正确,程序代码的临界区需要具有原子性,保证他们不会被任何其他代码中断。

为了强制程序临界区在并发下的原子性,需要能够在重要的时刻将进程序列化或彼此同步。序列化意味着同一时间只运行一个进程：这一瞬间就好像串行执行一样。同步有两种形式。首先是**互斥**,进程轮流访问一个变量。其次是**条件同步**,在满足条件(例如其他进程完成了它们的任务)之前进程一直等待,之后继续执行。这样,当一个程序即将进入临界区时,其他进程可以一直等待到它完成,然后安全地执行。

在本节中讨论的所有同步和序列化方法都使用相同的基本思想。它们在共享状态中将变量用作信号,所有过程都会理解并遵守它。这是一个相同的理念,允许分布式系统中的计算机协同工作：它们通过传递消息相互协调,根据每一个参与者都理解和遵守的一个协议。这些机制不是为了保护共享状态而出现的物理障碍。相反,他们是建立相互理解的基础上。和出现在十字路口的各种方向的车辆能够安全通行一样,是同一种相互理解。这里没有物理的墙壁阻止汽车相撞,只有遵守规则。同样,没有什么可以保护这些共享变量,除非当一个特定的信号表明轮到某个进程了,进程才会访问它们。

**锁**,也被称为互斥体(mutex),是共享对象,常用于发射共享状态被读取或修改的信号。对于一把保护一组特定的变量的锁,所有的进程都需要编程来遵循一个规则:一个进程不拥有特定的锁就不能访问相应的变量。在python中，这个可以用`threading`中的`Lock`对象实现。

**信号量**是用于维持有限资源访问的信号。它们和锁类似,除了它们可以允许某个限制下的多个访问。它就像电梯一样只能够容纳几个人。一旦达到了限制,想要使用资源的进程就必须等待。其它进程释放了信号量之后,它才可以获得。在python中，这个可以用`threading`中的`Semaphore`对象实现。

## 1. 启动与停止线程
```python
# Code to execute in an independent thread
import time
def countdown(n):
    while n > 0:
        print('T-minus', n)
        n -= 1
        time.sleep(1)

# Create and launch a thread
from threading import Thread
t = Thread(target=countdown, args=(10,))
t.start()
```

首先要先了解Python中的线程。Python 中的线程会在一个单独的系统级线程中执行(比如说一个POSIX 线程或者一个 Windows 线程),这些线程将由操作系统来全权管理。线程一旦启动,将独立执行直到目标函数返回。由于全局解释锁(GIL)的原因,Python 的线程被限制到同一时刻只允许一个线程执行。所以,Python 的线程更适用于处理 I/O 和其他需要并发执行的阻塞操作(比如等待 I/O、等待从数据库获取数据等等),而不是需要多处理器并行的计算密集型任务。

将线程daemon属性设为True，那么表示这是一个后台线程，进程退出时不会等到该线程结束，主线程结束就立刻杀死deamon线程。而如果对子线程调用`join`方法后，主线程就会等待该子线程结束后才结束。`join`函数有一个`timeout`参数，当设置守护线程时，含义是主线程对于子线程等待timeout的时间将会杀死该子线程，最后退出程序。所以说，如果有10个子线程，全部的等待时间就是每个timeout的累加和。

参考[Python多线程与多线程中join()的用法](https://www.cnblogs.com/cnkai/p/7504980.html)

```python
import threading
import time


def run():
    print(threading.current_thread().name, "start")
    time.sleep(1)
    print(threading.current_thread().name, "end")


if __name__ == '__main__':

    start_time = time.time()

    print('这是主线程：', threading.current_thread().name)
    thread_list = []
    for i in range(5):
        t = threading.Thread(target=run)
        thread_list.append(t)

    for t in thread_list:
        t.setDaemon(True) # 1
        t.start()

    """
    for t in thread_list:
        t.join(timeout=0.1) # 2
    """
    
    print('主线程结束了！', threading.current_thread().name)
    print('一共用时：', time.time()-start_time)
```
在一个独立的文件中运行代码，通过调整标号的两个地方，可以观察到其区别。

除了如上所示的两个操作,并没有太多可以对线程做的事情。你无法结束一个线程,无法给它发送信号,无法调整它的调度,也无法执行其他高级操作。如果需要这些特性,你需要自己添加。比如说,如果你需要终止线程,那么这个线程必须通过编程在某个特定点轮询来退出。

```python
class CountdownTask:
    def __init__(self):
        self._running = True
    def terminate(self):
        self._running = False
    def run(self, n):
        while self._running and n > 0:
            print('T-minus', n)
            n -= 1
            time.sleep(0.1)
        if self._running:
            print("job done")
        else:
            print("be terminated")

c = CountdownTask()
t = Thread(target=c.run, args=(10,))
t.start()
c.terminate() # Signal termination
t.join() # Wait for actual termination (if needed)
```

## 2. 判断线程是否已经启动

线程的一个关键特性是每个线程都是独立运行且状态不可预测。对一个`Thread`调用`start`方法并不是使这个线程立刻启动，而是说将该线程加入操作系统调度的范围，**至于该线程具体的运行时间，则是程序员不能控制的**。

```python
from threading import Thread, Event
import time
# Code to execute in an independent thread
def countdown(n, started_evt):
    print('countdown start!')
    time.sleep(0.2)
    started_evt.set()
    while n > 0:
        print('T-minus', n)
        n -= 1
        time.sleep(0.1)

# Create the event object that will be used to signal startup
started_evt = Event()

# Launch the thread and pass the startup event
print('Launching countdown')
t = Thread(target=countdown, args=(5,started_evt))
t.start()

# Wait for the thread to start
started_evt.wait()
print('countdown is running')
```

上面这段代码使用`Event`对象控制线程在某个时间点的运行先后顺序。`event.wait`要等到`event.set`执行后。在上面的代码中，主程序中的wait就要等待绑定了countdown函数的子线程执行完set才可以继续执行。如果将`started_evt.wait()`这句代码删除就无法保证”start“在”is running“之前打印。

`event`对象最好单次使用,就是说,你创建一个`event`对象,让某个线程等待这个对象,一旦这个对象被设置为真,你就应该丢弃它。尽管可以通过`clear`方法来重置`event`对象,但是很难确保安全地清理`event`对象并对它重新赋值。很可能会发生错过事件、死锁或者其他问题(特别是,你无法保证重置`event`对象的代码会在线程再次等待这个`event`对象之前执行)。如果一个线程需要不停地重复使用`event`对象,你最好使用`Condition`对象来代替。另外，`event`对象的一个重要特点是当它被设置为真时会唤醒所有等待它的线程。如果你只想唤醒单个线程,最好是使用信号量或者`Condition`对象来替代。




* * *
1. [谈谈Python协程技术的演进](https://zhuanlan.zhihu.com/p/30275154)
