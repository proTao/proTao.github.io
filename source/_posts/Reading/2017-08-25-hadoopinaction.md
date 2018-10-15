---
layout: post
date: 2017-08-25
title: hadoop实战
category: 读书笔记
tags: 
- hadoop 
- bigdata
- reading
keywords:
description:
---

# 第一章 Hadoop简介

## 1.2 什么是Hadoop
与众不同之处：

- 方便：运行在一般商用机器构成的大型集群上，或者如EC2等云计算服务上。
- 健壮：致力于在一般的甚至廉价的商用机器上运行。
- 可扩展：方便的增加节点。
- 简单：MR编程模型。

## 1.4 Hadoop与SQL数据库比较
- 用向外扩展代替向上扩展
- 用键值对代替关系表
- 用函数式编程代替声明式查询
- 用离线批处理代替在线处理

## 1.5 理解MapReduce
管道有助于进程原语的组合重用。消息队列有助于进程原语的同步。在mapreduce中，mapper和reducer对应为进程原语。

# 第二章 初识Hadoop

## 2.1 Hadoop的构造模块

- 一组守护进程：Namenode，Datanode，SecondaryNamenode，JobTracker，TaskTracker
- SNN（SecondaryNameNode），类似于NameNode，独占一台服务器，与NameNode不同的是不接受或记录HDFS的任何实时变化，它只与NameNode通信，根据集群配置的时间间隔获取NameNode的快照。Namenode失效后，SNN需要手动配置。
- 类似于HDFS，计算的守护进程也是主从结构：JobTracker和TaskTracker。JobT负责分配节点监控运行等任务，TaskTrakcer管理各个任务在各自从节点上的执行情况。每个节点上只有一个TaskT，但是每个TaskT可以生成多个JVM来并行处理map或red任务。
- Namenode和JobTracker分别驻留在两台服务器上，每个从节点均驻留Namenode和Tasktracker。

<!-- more -->
## 2.4 基于Web的集群用户界面
- Name通过端口50070提供集群HDFS的常规视图报告。

# 第三章 Hadoop组件

## 3.1 HDFS文件操作
一些基本的命令行操作。
MergeFile程序debug：

1. 权限不足
	```java
	FileSystem hdfs = FileSystem.get(conf);
	FSDataOutputStream dhfs = hdfs.create(path);
	```
	解决：path要带有协议和主机名，如hdfs://localhost:9000/output

2. Wrong FS: hdfs://localhost:9000/,expect:file:///
	解决：添加
```java
conf.set("mapred.jop.tracker", "hdfs://10.64.44.113:9001");
conf.set("fs.default.name", "hdfs://10.64.44.113:9000");
```
可能是由于伪分布式环境和物理集群不同的问题，物理集群应该是不用添加这两行

3. 直接运行class文件失败，说找不到一些奇怪的包，没找到错。

## 3.2 剖析MapReduce程序
1. 节点间通信的唯一时间是在shuffle阶段，这个通信约束对于可扩展性有着极大帮助。
2. hadoop数据类型有
	- BooleanWritable
	- ByteWritable
	- DoubleWritable
	- FloatWritable
	- IntWritable
	- LongWritable
	- Text
	- NullWritable

	作为hadoop中的value，就要实现Writable接口中的readFields与write方法。他们与Java中的DataInput和DataOutput类一起用于类中内容的序列化。如果想要作为hadoop的键类型，还需要实现Comparable中的compareTo方法。

3. Mapper
	继承自MapReduceBase类，调用configure函数提取配置文件或者参数，在数据处理之前该函数被调用。close函数完成结尾工作，如关闭数据库连接，打开文件等。
	Mapper泛型<K1,V1,K2,V2>。
	Mapper只有一个方法map(K1 key, V1 value, OutputCollector<K2,V2> output, 		Reporter reporter) throw Exception.OutputCollector负责接受映射过程的输出，Reporter提供附加信息。
	一些预定义的Mapper：
	- IdentityMapper
	- InverseMapper
	- RegexMapper
	- TokenCountMapper

4. Reducer
	基本类似于Mapper的介绍。有两个内置的Reducer
    - IdentityReducer
    - LongSumReducer

5. Patitioner
	决定mapper之后的数据哪些归为一类递交给一个reducer。默认实现的是HashPatitioner，如果想要自定义patitioner，需要实现Partitioner中的getPartition和configure方法。前者返回一个介于0和reduce任务数之间的整数，后者将Hadoop对作业的配置应用在patitioner上。

6. Combiner
	其实是本地的reducer

7. InputFormat和OutputFormat
	![](/img/FileInputFormat.png)
    重点说明InputFormat。这个类负责读取数据，进行文件分片，并通过正确的格式将数据移交给MapReduce计算模块。如类图所示，常用的InputFormat有：
    - TextInputFormat
    - KeyValueTextInputFormat
    - SequenceFileInputFormat
    - NLineInputFormat
    如果这些还不够，想要自定义的话，若是继承InputFormat，需要实现两个方法：getSpilit和getRecordReader。前者对文件进行分片，后者返回一个对象（RecordReader），循环提取给定分片中的记录，并解析每个记录为预订一类型的键值对。
    当然这样的话太过繁琐，尤其是getSplit函数。所以我们可以直接继承FileInputFormat，此时我们只需要关注定制RecordReader并返回就行。
    RecordReader我们也不用从头构建，可以直接实现RecordReader接口，返回一个RecordReader的子类。
