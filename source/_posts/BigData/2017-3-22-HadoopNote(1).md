---
layout: post
title: Hadoop笔记（一）
category: 大数据
tags: 
- bigdata 
- hadoop 
keywords: 
description: 
---

[TOC]


# **写在前面**

一直在上学，所以我接触到的偏工程的项目不是特别多，大部分都是基础而范范的理论。而在这学期的一门大数据系统和大规模数据分析的课程，让我有机会接触到了一部分目前广泛应用于业界的开源项目，这篇文章就是关于第一次课程作业的，也是我的第一篇博文。希望能真真正正的积累一些东西，也算对自己的学习负责。在文章中尽量少涉及概念，主要记录自己的工作。
这次的作业内容比较简单，主要是在ubuntu14.04系统上搭建一个伪分布式环境。作业要求是安装JAVA1.7，HADOOP2.6和HBASE0.98。作业内容不难，主要是熟悉环境。

# **知识点**

- HADOOP是一个Apache的开源项目，主要是由两部分构成，分布式文件系统HDFS和分布式计算框架MapReduce这篇文章只涉及到HDFS，暂不考虑MapReduce。

- HDFS是GFS的基于Java开源实现，是一个实现在应用层的分布式文件系统，系统架构是master/slave，在HDFS中master是namenode，存放文件的元信息和所在的datanode，slave是datanode，存放真正的数据。出于效率的考虑，对文件不支持修改，只能追加。

- 由于namenode存储了全部的文件的元信息，宕机的代价无法承担，所以会建立一个secodarynamenode，他可以理解为namenode的一个备份，提供crash recovery。而datanode中一个文件默认有三个备份，所以即使丢失也可以从其他的备份datanode中恢复。



# **开始动手**

## **Ubuntu**
电脑实在太渣，装在虚拟机里系统卡的蛋疼，所以就装了一个双系统，顺便重温一下很久没用的linux操作系统，没什么可说的。

## **Java**
java是1.7版本，官网下载，解压，使用`sudo vim /etc/profile`[^profile]文件中配置环境变量。
[^profile]:profile文件：linux是一个多用户操作系统，而在/etc/profile中修改的系统变量是对所有用户都可见的。注销重启后本次修改的系统变量才会生效。

```shell
	#java environment
	export JAVA_HOME=/usr/lib/jvm/java7
	export CLASSPATH=.:${JAVA_HOME}/lib/dt.jar:${JAVA_HOME}/lib/tools.jar
	export PATH=${JAVA_HOME}/bin:$PATH
```
JAVA_HOME是安装目录。配置后用source[^source]生效或者重启，用`java -version`验证是否配置成功。

[^source]:source命令：网上很多教程说使用source命令使当前修改生效。source命令的本意是在当前进程中执行脚本，而正常情况下脚本会在一个子进程中执行。所以使用source命令后在当前进程中系统变量修改时生效的，但是对其他进程是没有用的。
```
java version "1.7.0_79"
Java(TM) SE Runtime Environment (build 1.7.0_79-b15)
Java HotSpot(TM) 64-Bit Server VM (build 24.79-b02, mixed mode)
```

## **HADOOP**
在官网的下载链接(http://www.apache.org/dyn/closer.cgi/hadoop/common)中下载你需要的版本。我下载的版本是2.6，注意HADOOP版本要与java版本配套，HADOOP2.7要求至少java1.7，HADOOP2.6要求java至少2.6。

下载完成后使用`tar zxvf hadoop-x.y.x.tar.gz -C /usr/local`解压，我的安装目录是/usr/local，如果觉得文件夹名字太长可以重命名。同理在/etc/profile中配置系统变量。
```shell
#hadoop environment
export HADOOP_HOME=/usr/local/hadoop-2.6.0
export PATH=$PATH:${HADOOP_HOME}/bin
```
配置环境变量的目的是在任何目录下都可以执行hadoop的命令。但是到这里还没有完全完成。有的教程说要关闭防火墙和在配置hosts文件中配置DNS解析，这里我没有这么配置，直接用的localhost。如果配置好了HADOOP的系统变量，可以简单的在任意一个目录下使用`hadoop`命令来测试一下，如果提示了帮助信息就说明路径没有问题。
```shell
tao@tao-Inspiron-5425:/usr/local/hadoop-2.6.0/sbin$ hadoop
Usage: hadoop [--config confdir] COMMAND
       where COMMAND is one of:
  fs                   run a generic filesystem user client
  version              print the version
  jar <jar>            run a jar file
  checknative [-a|-h]  check native hadoop and compression libraries availability
  distcp <srcurl> <desturl> copy file or directories recursively
  archive -archiveName NAME -p <parent path> <src>* <dest> create a hadoop archive
  classpath            prints the class path needed to get the
  credential           interact with credential providers
                       Hadoop jar and the required libraries
  daemonlog            get/set the log level for each daemon
  trace                view and modify Hadoop tracing settings
 or
  CLASSNAME            run the class named CLASSNAME

Most commands print help when invoked w/o parameters.

```
但是此时只是能正确的找到hadoop命令的所在位置，此时还不能真正的执行，要想能让hadoop服务启动还需要最后几步。
然后如果没有安装ssh要安装ssh，这个网上的教程很多了。主要的目的是在集群环境或者伪分布式环境中，如果不用ssh免密码登陆的话，每个进程都需要输入密码。生成公钥并且加入信任列表的话，只有第一次需要用户确认选择yes，之后便可以直接登录。这个也可以不在这里配置，并不影响hadoop的安装，不过也是迟早要完成的。

使用ssh localhost验证是否成功：
```
tao@tao-Inspiron-5425:/usr/local$ ssh localhost
Welcome to Ubuntu 16.04.2 LTS (GNU/Linux 4.4.0-66-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

0 个可升级软件包。
0 个安全更新。

*** System restart required ***
Last login: Mon Mar 20 22:25:59 2017 from 127.0.0.1
tao@tao-Inspiron-5425:~$ exit
注销
Connection to localhost closed.
```
使用exit返回当前环境。然后hadoop还需要改动至少两个地方，一个是hadoop-env.sh，另外一个是几个xml配置文件，都在`$HADOOP_HOME/etc/hadoop`目录下。
首先是hadoop-env.sh:
```
# The java implementation to use.
export JAVA_HOME=/usr/lib/jvm/java7
```
其实我觉得可以不用修改，因为在初始状态这个变量已经指向了${JAVA_HOME}，只要设置好了JAVA_HOME应该就没有问题，不过我还是以防万一改了过来。。。
然后是几个配置文件，我先把内容贴出来，再进行说明。

**core-site.xml**
```xml
<configuration>
        <property>
                <name>fs.default.name</name>
                <value>hdfs://localhost:9000/</value>
                <description>your hostname</description>
        </property>
        <property>
                <name>hadoop.tmp.dir</name>
                <value>/usr/local/hadoop-2.6.0/tmp</value>
        </property>
</configuration>
```
**hdfs-site.xml**
```xml
<configuration>
        <property>
                <name>dfs.replication</name>
                <value>1</value>
        </property>
        <property>
                <name>dfs.permissions</name>
                <value>false</value>
        </property>
</configuration>
```
**mapred-site.xml**
```xml
<configuration>
        <property>
                <name>mapred.job.tracker</name>
                <value>localhost:9001</value>
                <description>your hostname</description>
        </property>
</configuration>
```
- 解释：
1. 第一个文件中的fs.default.name是可以访问到你的hdfs的URI，也就是说在将来编写的程序中可以通过hdfs://localhost:9000/来访问你的hdfs；hadoop.tmp.dir的值是hdfs在你本地中的临时目录的存放位置。
2. 第二个文件中dfs.replication是hdfs的冗余备份数，默认是3，由于咱们配置的是伪分布式，不需要额外的冗余也为了防止可能的Error和Warning，在这里改成1。后者顾名思义是禁用文件操作权限检查。
3.  第三个文件的mapred.job.tracker配置的应该是作业跟踪管理器，目前来说应该不配置也可以。
4. 注释：其实在`$HADOOP_HOME/share/doc`文件夹下有很多hadoop的文档，例如core-site.xml的默认配置和参数描述就在这里`$HADOOP_HOME/share/doc/hadoop/hadoop-project-dist/hadoop-common/core-default.xml`。按照以上步骤完成后没有意外的话就可以启动hadoop了。

在启动服务之前先使用`hadoop namenode -format`命令格式化namenode。
hadoop的启动脚本在`$HADOOP_HOME/sbin`目录下，使用`./start-dfs.sh`命令来启动hdfs的相关进程。 然后可以使用jps来查看相关java进程是否启动成功。

```shell
tao@tao-Inspiron-5425:/usr/local/hadoop-2.6.0/sbin$ ./start-dfs.sh 
Starting namenodes on [localhost]
localhost: starting namenode, logging to /usr/local/hadoop-2.6.0/logs/hadoop-tao-namenode-tao-Inspiron-5425.out
localhost: starting datanode, logging to /usr/local/hadoop-2.6.0/logs/hadoop-tao-datanode-tao-Inspiron-5425.out
Starting secondary namenodes [0.0.0.0]
0.0.0.0: starting secondarynamenode, logging to /usr/local/hadoop-2.6.0/logs/hadoop-tao-secondarynamenode-tao-Inspiron-5425.out

tao@tao-Inspiron-5425:/usr/local/hadoop-2.6.0/sbin$ jps
3311 NameNode
3619 SecondaryNameNode
3426 DataNode
3739 Jps
```
可以看到在localhost上面启动了namenode，datanode，和SecondaryNamenode三个进程，相关日志也写入了日志文件。用jps命令也可以看到三个java进程存在。截止至此，hadoop启动成功。
我们还可以用其他的方法验证一下hadoop服务能否正常工作。

- 使用hadoop shell：在任意文件夹下输入`hadoop fs -ls /`，这个命令可以查看hdfs的根目录的文件。里面已经存在hbase文件夹是因为我已经在hdfs部署了hbase，这个稍后进行讲解。另外input.tbl是我自己随意上传的测试文件。
```shell
tao@tao-Inspiron-5425:/usr/local/hadoop-2.6.0/sbin$ hadoop fs -ls /
Found 2 items
drwxr-xr-x   - tao supergroup          0 2017-03-22 11:04 /hbase
-rw-r--r--   1 tao supergroup        150 2017-03-21 15:45 /input.tbl
```
- 另外可以在浏览器中输入localhost:50070[^port]查看namenode工作情况。
[^port]:端口：50070是默认的namenode的http服务的端口，所以可以通过浏览器访问。50075是datanode的http服务端口。还有很多其他的默认端口，可查阅hadoop的手册。所有端口基于TCP。


# **坑们**
- 权限问题：用惯了windows，突然在转到linux下还是比较不太习惯如此明晰的权限管理。一定确保安装之后整个安装文件夹都是属于自己当前用户的。使用ll命令可以检查当前目录下所有文件的详细信息。可以发现hadoop的文件所有者是当前用户tao而不是root。ssh同理也要是在当前用户条件下配置无密码登录，否则就会出现ssh localhost没有问题但是启动进程的时候要求反复输入密码而且还Permission Denied的情况。
```
drwxr-xr-x 14 root root 4096 3月  21 10:33 ./
drwxr-xr-x 11 root root 4096 7月  20  2016 ../
drwxr-xr-x  2 root root 4096 3月  17 21:49 bin/
drwxr-xr-x  2 root root 4096 7月  20  2016 etc/
drwxr-xr-x  2 root root 4096 7月  20  2016 games/
drwxr-xr-x 11 tao  root 4096 3月  21 14:42 hadoop-2.6.0/
drwxr-xr-x  8 tao  root 4096 3月  21 10:53 hbase-0.98.24/
```
- hadoop namenode -format命令只需要执行一次。在第一次执行后会格式化format文件，在dfs目录下创建name文件夹并管理一个VERSION文件，然后创建datanode后，data文件夹中同样会保存一个VERSION文件，这两个VERSION需要保持一致。

**name VERSION**

```
#Thu Mar 23 16:16:20 CST 2017
namespaceID=531037972
clusterID=CID-a03f8986-c3e3-42e4-a094-247c1f3e91e4
cTime=0
storageType=NAME_NODE
blockpoolID=BP-963905725-127.0.1.1-1490034290631
layoutVersion=-60
```

**data VERSION**

```
#Thu Mar 23 16:16:27 CST 2017
storageID=DS-6084e0ed-0590-4d22-a36f-6c94ef6629e6
clusterID=CID-a03f8986-c3e3-42e4-a094-247c1f3e91e4
cTime=0
datanodeUuid=c5c10d13-0311-4854-8108-5eb9d25b6a50
storageType=DATA_NODE
layoutVersion=-56
```

发现两者的clusterID要保持一致，如果多次`hadoop namenode -format`可能导致版本不一样而使得secondaryname或者datanode进程无法启动，查看日志可能会发现有如下信息`java.io.IOException: Version Mismatch`。
此时可能就是这个原因导致的问题，有两种解决办法，一种是手动改动VERSION文件与namenode的VERSION一致，另一种是删除全部文件夹，重新执行`hadoop namenode -format`





