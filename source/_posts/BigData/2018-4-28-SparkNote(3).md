---
layout: post
date: 2018-04-28
title: Spark笔记（三）
category: 大数据
tags:
- bigdata
- spark
- dataprocessing
keywords: scala spark bigdata
description:
---

## 开发环境搭建

### 安装sbt

```bash
echo "deb https://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
sudo apt-get update
sudo apt-get install sbt
```

### sbt 初识
参考[极客学院SBT手册](http://wiki.jikexueyuan.com/project/sbt-getting-started/)

在scala源代码中编写简单的测试代码。
```scala
/**
  * Created by protao on 18-5-2.
  */

import org.apache.spark.SparkConf
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._

object WordCount {
  def main(args: Array[String]) {
    val inputFile =  "/tmp/0401.txt"
    val conf = new SparkConf().setAppName("TestTianjin")
    val sc = new SparkContext(conf)
    val textFile = sc.textFile(args(0))
    val wordCount = textFile.flatMap(line => line.split(" ")).map(word => (word, 1)).reduceByKey((a, b) => a + b)
    wordCount.saveAsTextFile(args(1))
  }
}
```

按照手册进行项目文件夹的整理，简单的sbt文件的编写与编译，在本地spark环境下执行没有问题。

```java
name := "SparkWithSbt"

version := "1.0"

scalaVersion := "2.11.8"

libraryDependencies += "org.apache.spark" %% "spark-core" % "2.1.0"

```

### 远程脚本
由于工作环境是在远程集群上提交任务，而远程集群由于工作需要，不能自己随意配置环境，因此我在本地搭建代码开发与测试环境，并且在本地进行打包，然后提交到远程服务器，下面的脚本通过expect工具自动完成与远程服务器的交互。
```bash
#!/usr/bin/expect
 # Author: prota
 # 脚本功能:  上传jar包，远端执行
 # Date: 20180502

# expect 输出日志
# log_file time

# 读取命令行参数
set jarfile [lindex $argv 0]
set inpath [lindex $argv 1]
set outpath [lindex $argv 2]

# 设置常量
set timeout -1 # 不设置超时
set USERNAME "xxx" # 敏感信息要打码
set JUMP "xxx.xxx.x.xxx"
set TERMINAL "xx.xx.x.xxx"
set PASSWORD "xxxxxxxxxxxxx"
set PORT "xxxxx"

# DEBUG
puts $jarfile


# 传送文件到跳板机
spawn scp -P $PORT $jarfile $USERNAME@$JUMP:~/workspace
expect "password"
send "$PASSWORD\r"
expect "100%"
expect eof

# 这里要重新spawn一个进程，因为前面的scp进程已经结束了
spawn ssh -p $PORT $USERNAME@$JUMP 
expect "password"
send "$PASSWORD\r"

# 传送文件到目标机，并删除跳板机上的文件
expect "$USERNAME"
send "scp -P $PORT ~/workspace/$jarfile $USERNAME@$TERMINAL:~/workspace/zhangyongtao/workspace\r"
expect "password"
send "$PASSWORD\r"
expect "$USERNAME"
send "rm workspace/$jarfile\r"

# 登录目标机
expect "$USERNAME"
send "ssh -p $PORT $USERNAME@$TERMINAL\r"
expect "password"
send "$PASSWORD\r"

expect "$USERNAME"
send "hdfs dfs -rm -r $outpath\r"
expect "$USERNAME"
send "cd ~/workspace/zhangyongtao/workspace\r"
expect "$USERNAME"
send "spark-submit --master yarn-cluster sparkwithsbt_2.11-1.0.jar $inpath $outpath\r"


expect "$USERNAME"
send "exit\r"

expect "closed" # 这里要匹配closed，匹配命令提示符中的用户名的话跑不通，我也不知道为啥
send "exit\r"

expect eof
```
### IDE集成Sbt环境

参考
1. [配置IntelliJ IDEA 13的SBT和Scala开发环境](http://debugo.com/idea-scala-ide/)
2. [使用Intellij Idea编写Spark应用程序（Scala+SBT）](使用Intellij Idea编写Spark应用程序（Scala+SBT）_厦大数据库实验室博客.html)

