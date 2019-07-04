---
layout: post
date: 2017-3-23
title: HBase初探（一）
category: 大数据
tags: 
- bigdata 
- hbase
- database
keywords:
description:
---
[TOC]

# **写在前面**

上一篇文章已经布置好了Hadoop环境，接下来的任务是在Hadoop的基础上搭建Hbase环境，然后简单的调用HDFS和HBase的API，完成从hdfs中读取数据，简单的处理之后存储至HBase的任务。

# **知识点** 

-  前面讲到在hdfs中namenode存放所有文件的元信息，datanode存放文件真正的数据块，但是这样导致hdfs在存放大量小文件的时候对namenode的压力很大，这也是为什么hdfs中的数据块大小是64MB或者更大，而HBase就是一个可以解决这种问题的，支持实时随机读写的的超大规模数据集。

- HBase不是关系型数据库，不支持SQL，也不能支持触发器或外键约束这类RDBMS可以支持的特性，但是作为nosql（not only sql）的一种表现形式，它在廉价硬件集群上可以很好的管理超大规模稀疏表。

- 对于HBase的的数据类型，仅仅是作为字节流。行键，列族和列一起构成key，另外由于HDFS不支持修改，所以每个值会附带上它的版本或者时间戳，


# **开始动手**

##  **安装**

已有环境：
> ubuntu 16.04
> java 1.7
> hadoop 2.6.0

准备安装：
> HBase 0.98

还是先去官网（http://www-eu.apache.org/dist/hbase/）下载hbase的安装包，有stable是稳定版本。另外还可以下载到源码和md5校验文件，源码可以阅读或者手动编译，MD5校验是否有坏位。
还是使用`tar zxvf hbase-x.y.z.tar.gz -C /usr/local`安装到/usr/local文件夹下，使用mv命令重命名，使用chown命令确认权限，这些和前面安装Hadoop大同小异，不再赘述。
<!-- more -->
上述步骤完成后同样`sudo vim /etc/profile`修改系统变量：
```shell
#base environment
export HBASE_HOME=/usr/local/hbase-0.98.24
export PATH=$PATH:${HBASE_HOME}/bin
```
类似于Hadoop，有几个关键的配置文件需要改动。
第一个是$HBASE_HOME/conf/hbase-env.sh，第一处改动还是JAVA_HOME的问题，第二处是讲HBASE_MANAGES_ZK的值设置为true，注释给出了解释，HBase是否管理自己的ZooKeeper实例，ZooKeeper是一个协调器，如果没有安装在这里设置为true就可以。这里有一个作为初学者觉得很有用的功能是在vim的命令行模式下按`/`直接可以进行搜索，再次按`n`可以查找下一处。
下一个文件是同一个文件夹下的hbase-site.xml，先贴出我修改之后的文件。
```shell
<configuration>
        <property>
                <name>hbase.rootdir</name>
                <value>hdfs://localhost:9000/hbase</value>
        </property>
        <property>
                <name>hbase.cluster.distributed</name>
                <value>true</value>
        </property>
        <property>
                <name>hbase.zookeeper.quorum</name>
                <value>localhost</value>
        </property>
        <property>
                <name>dfs.replication</name>
                <value>1</value>
        </property>
</configuration>
```
第一项`hbase.rootdir`是指HBase在hdfs中的存放目录，区分开本地文件系统的目录。需要注意的是这个主机名和端口号一定要与Hadoop中coure-site.xml中配置的一致。第二项`hbase.cluster.distributed`顾名思义是是否配置成分布式。第三项是指zookeeper协调器运行在哪一个节点上，第四项同理是dfs的冗余数。

完成对配置文件的修改之后就可以启动HBase服务了，在启动之前一定要先成功启动Hadoop的HDFS。然后进入$HBASE_HOME/bin目录下执行`./start-hbase.sh`，启动后我们依然用`jps`命令查看java进程。
```
tao@tao-Inspiron-5425:/usr/local/hbase-0.98.24/bin$ ./start-hbase.sh 
localhost: starting zookeeper, logging to /usr/local/hbase-0.98.24/bin/../logs/hbase-tao-zookeeper-tao-Inspiron-5425.out
starting master, logging to /usr/local/hbase-0.98.24/logs/hbase-tao-master-tao-Inspiron-5425.out
localhost: starting regionserver, logging to /usr/local/hbase-0.98.24/bin/../logs/hbase-tao-regionserver-tao-Inspiron-5425.out

tao@tao-Inspiron-5425:/usr/local/hbase-0.98.24/bin$ jps
8082 HRegionServer
7183 NameNode
7305 DataNode
7928 HMaster
8282 Jps
7504 SecondaryNameNode
7864 HQuorumPeer
```

成功启动后我们可以发现多了三个进程，HMaster，HRegionServer和HQuorumPeer。另外我们可以通过其他几种方式验证HBase的成功启动。HMatser是master/slave架构中的master，负责分配数据表到RegionServer等,不存储任何具体数据，HRegionServer存储具体的数据。Region是Table由行划分出的子集。HQuorumPeer就是HBase子集管理的zookeeper。

- 第一种还是通过HBase的http服务端口，我们可以访问localhost:60010来进行验证

- 第二种是使用hbase shell，在任意目录下使用hbase shell命令应该可以进入hbase的命令行模式。简单的使用`list`可以查看HBase中的所有表。
```
tao@tao-Inspiron-5425:/usr/local/hbase-0.98.24/bin$ hbase shell
2017-03-23 23:41:32,242 INFO  [main] Configuration.deprecation: hadoop.native.lib is deprecated. Instead, use io.native.lib.available
HBase Shell; enter 'help<RETURN>' for list of supported commands.
Type "exit<RETURN>" to leave the HBase Shell
Version 0.98.24-hadoop2, r9c13a1c3d8cf999014f30104d1aa9d79e74ca3d6, Thu Dec 22 02:36:05 UTC 2016

hbase(main):001:0> list
TABLE                                                                           
SLF4J: Class path contains multiple SLF4J bindings.
SLF4J: Found binding in [jar:file:/usr/local/hbase-0.98.24/lib/slf4j-log4j12-1.6.4.jar!/org/slf4j/impl/StaticLoggerBinder.class]
SLF4J: Found binding in [jar:file:/usr/local/hadoop-2.6.0/share/hadoop/common/lib/slf4j-log4j12-1.7.5.jar!/org/slf4j/impl/StaticLoggerBinder.class]
SLF4J: See http://www.slf4j.org/codes.html#multiple_bindings for an explanation.
Result                                                                          
1 row(s) in 2.8680 seconds

=> ["Result"]
```
Result是我已经建好的一个表，初始状态应该是有0 row(s)。

## **API上手**

###  **HDFS读取文件**
```java
public static Queue<String> readFromHDFS(String path_in_hdfs) throws IOException {
        String file = "hdfs://localhost:9000/"+path_in_hdfs;

        Configuration conf = new Configuration();
        FileSystem fs = FileSystem.get(URI.create(file),conf);
        Path path = new Path(file);
        FSDataInputStream in_stream = fs.open(path);

        BufferedReader in = new BufferedReader(new InputStreamReader(in_stream));
        Queue<String> input_data = new LinkedList<>();
        String tempstr;
        while((tempstr = in.readLine()) != null) {
            input_data.offer(tempstr);
        }

        in.close();
        fs.close();
        System.out.println("read success");
        return input_data;
    }
```

###  **存放数据到HBase**

-  创建表
```java
private static void createTable(String table_name, String CF) throws IOException {
        // create table descriptor with table name
        HTableDescriptor htd = new HTableDescriptor(TableName.valueOf(table_name));
        System.out.println("tablename is "+table_name);
        System.out.println("Column family is "+ CF);
        //create hbase admin with configuration
        Configuration conf = HBaseConfiguration.create();
        HBaseAdmin h_admin = new HBaseAdmin(conf);

        //if exit then delete
        if (h_admin.tableExists(table_name)) {
            h_admin.disableTable(table_name);
            h_admin.deleteTable(table_name);
        }

        //column
        HColumnDescriptor cf = new HColumnDescriptor(CF);
        htd.addFamily(cf);

        h_admin.createTable(htd);

        h_admin.close();
        System.out.println("table success create");
    }
```
- put数据 


```java
private static void putIntoHbase(String table_name, String CF, int[] keys, Enumeration<ArrayList<String>> value) {
        // make sure the table does exist
        ArrayList<String> data_record;
        int record_length = keys.length;


        try {
            HTable table = new HTable(HBaseConfiguration.create(), table_name);

            int i = 0;
            while (value.hasMoreElements()) {
                data_record = value.nextElement();
                Put put1 = new Put(Bytes.toBytes(i+"")); // turn to String
                for (int j = 0; j < record_length; j++) {
                    System.out.println("R"+keys[j]+" "+data_record.get(j));
                    put1.add(Bytes.toBytes(CF), Bytes.toBytes("R"+keys[j]), Bytes.toBytes(data_record.get(j)));
                    table.put(put1);
                }
                i++;
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
```

这些都是API最最简单的应用，没有丝毫技术含量，实际上只为了证明这个系统可以正常工作，更多的内容应该会在以后分两三次继续实现。

# **坑们**

- 版本问题，这是一个比较简单无脑弱智的问题，可是我还是毅然决然的踩了这个不是坑的坑，就是HBase0.98有针对hadoop1和hadoop2不同版本的发行包，在hadoop2上面运行hbase-0.98-Hadoop1就会导致HMaster进程无法启动，查看日志也没有什么关键的提示信息。

```java
2017-03-22 11:09:20,551 ERROR [main] master.HMasterCommandLine: Master exiting
java.lang.RuntimeException: HMaster Aborted
        at org.apache.hadoop.hbase.master.HMasterCommandLine.startMaster(HMasterCommandLine.java:207)
        at org.apache.hadoop.hbase.master.HMasterCommandLine.run(HMasterCommandLine.java:135)
        at org.apache.hadoop.util.ToolRunner.run(ToolRunner.java:70)
        at org.apache.hadoop.hbase.util.ServerCommandLine.doMain(ServerCommandLine.java:127)
        at org.apache.hadoop.hbase.master.HMaster.main(HMaster.java:3164)
```
后来试了所有的办法，甚至想重新安装才发现有可能是版本的问题。估计没有人和我犯一样的错误吧。。。

- javac编译的问题：在IDE中整个程序运行无误，然后在javac中编译显示找不到用户包出错，这个可以在`/etc/profile`中配置需要的jar包到CLASSPATH，我看到网上说这个路径内的目录不起作用，必须要把每一个jar包单独写一个路径。我试了一下好像的确是这样，也不知道是为什么。还有一种方法是写到另外一个变量中，然后再`javac`编译时用`-cp`或者`-classpath`参数输入用户包路径也可以。

- 但是在引入包之后执行不报错但是会超时，不停的提示`client.RpcRetryingCaller`， 理论上代码和在IDE中一样一样的没有改动，包也引入了没有问题，重新再IDE中跑也流畅完成。。。后来一点一点排查发现是少导入了两个包：`$HADOOP_HOME/share/hadoop/common/hadoop-common-2.6.0-tests.jar`和`$HADOOP_HOME/share/hadoop/hdfs/hadoop-hdfs-2.6.0-tests.jar`本来以为是带着tests的包是无关紧要的，自以为是真的是需要付出代价的。。。

- 下面贴出全部的classpath：


```bash
#basic
export CLASSPATH=${CLASSPATH}:$HADOOP_HOME/share/hadoop/common/hadoop-common-2.6.0.jar:$HADOOP_HOME/share/hadoop/common/hadoop-nfs-2.6.0.jar:$HADOOP_HOME/share/hadoop/hdfs/hadoop-hdfs-2.6.0.jar:$HADOOP_HOME/share/hadoop/hdfs/hadoop-hdfs-nfs-2.6.0.jar$HADOOP_HOME/share/hadoop/common/hadoop-common-2.6.0-tests.jar:$HADOOP_HOME/share/hadoop/hdfs/hadoop-hdfs-2.6.0-tests.jar

# mapreduce
export CLASSPATH=${CLASSPATH}:${HADOOP_HOME}/share/hadoop/mapreduce/hadoop-mapreduce-client-app-2.6.0.jar:${HADOOP_HOME}/share/hadoop/mapreduce/hadoop-mapreduce-client-common-2.6.0.jar:${HADOOP_HOME}/share/hadoop/mapreduce/hadoop-mapreduce-client-core-2.6.0.jar:${HADOOP_HOME}/share/hadoop/mapreduce/hadoop-mapreduce-client-hs-2.6.0.jar:${HADOOP_HOME}/share/hadoop/mapreduce/hadoop-mapreduce-client-hs-plugins-2.6.0.jar:${HADOOP_HOME}/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-2.6.0.jar:${HADOOP_HOME}/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-2.6.0-tests.jar:${HADOOP_HOME}/share/hadoop/mapreduce/hadoop-mapreduce-client-shuffle-2.6.0.jar:${HADOOP_HOME}/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.6.0.jar

#yarn
export CLASSPATH=${CLASSPATH}:${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-api-2.6.0.jar:${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-applications-distributedshell-2.6.0.jar:${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-applications-unmanaged-am-launcher-2.6.0.jar:${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-client-2.6.0.jar:${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-common-2.6.0.jar:${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-registry-2.6.0.jar:${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-server-applicationhistoryservice-2.6.0.jar:${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-server-common-2.6.0.jar:${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-server-nodemanager-2.6.0.jar:${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-server-resourcemanager-2.6.0.jar:${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-server-tests-2.6.0.jar:${HADOOP_HOME}/share/hadoop/yarn/hadoop-yarn-server-web-proxy-2.6.0.jar

#common/lib
export CLASSPATH=${CLASSPATH}:${HADOOP_HOME}/share/hadoop/common/lib/guava-11.0.2.jar:${HADOOP_HOME}/share/hadoop/common/lib/hadoop-annotations-2.6.0.jar:${HADOOP_HOME}/share/hadoop/common/lib/hadoop-auth-2.6.0.jar:${HADOOP_HOME}/share/hadoop/common/lib/hamcrest-core-1.3.jar:${HADOOP_HOME}/share/hadoop/common/lib/htrace-core-3.0.4.jar:${HADOOP_HOME}/share/hadoop/common/lib/httpclient-4.2.5.jar:${HADOOP_HOME}/share/hadoop/common/lib/httpcore-4.2.5.jar:${HADOOP_HOME}/share/hadoop/common/lib/jackson-core-asl-1.9.13.jar:${HADOOP_HOME}/share/hadoop/common/lib/jackson-jaxrs-1.9.13.jar:${HADOOP_HOME}/share/hadoop/common/lib/jackson-mapper-asl-1.9.13.jar:${HADOOP_HOME}/share/hadoop/common/lib/jackson-xc-1.9.13.jar:${HADOOP_HOME}/share/hadoop/common/lib/jasper-compiler-5.5.23.jar:${HADOOP_HOME}/share/hadoop/common/lib/jasper-runtime-5.5.23.jar:${HADOOP_HOME}/share/hadoop/common/lib/java-xmlbuilder-0.4.jar:${HADOOP_HOME}/share/hadoop/common/lib/jaxb-api-2.2.2.jar:${HADOOP_HOME}/share/hadoop/common/lib/jaxb-impl-2.2.3-1.jar:${HADOOP_HOME}/share/hadoop/common/lib/jersey-core-1.9.jar:${HADOOP_HOME}/share/hadoop/common/lib/jersey-json-1.9.jar:${HADOOP_HOME}/share/hadoop/common/lib/jersey-server-1.9.jar:${HADOOP_HOME}/share/hadoop/common/lib/jets3t-0.9.0.jar:${HADOOP_HOME}/share/hadoop/common/lib/jettison-1.1.jar:${HADOOP_HOME}/share/hadoop/common/lib/jetty-6.1.26.jar:${HADOOP_HOME}/share/hadoop/common/lib/jetty-util-6.1.26.jar:${HADOOP_HOME}/share/hadoop/common/lib/jsch-0.1.42.jar:${HADOOP_HOME}/share/hadoop/common/lib/jsp-api-2.1.jar:${HADOOP_HOME}/share/hadoop/common/lib/jsr305-1.3.9.jar:${HADOOP_HOME}/share/hadoop/common/lib/junit-4.11.jar:${HADOOP_HOME}/share/hadoop/common/lib/log4j-1.2.17.jar:${HADOOP_HOME}/share/hadoop/common/lib/mockito-all-1.8.5.jar:${HADOOP_HOME}/share/hadoop/common/lib/netty-3.6.2.Final.jar:${HADOOP_HOME}/share/hadoop/common/lib/paranamer-2.3.jar:${HADOOP_HOME}/share/hadoop/common/lib/protobuf-java-2.5.0.jar:${HADOOP_HOME}/share/hadoop/common/lib/servlet-api-2.5.jar:${HADOOP_HOME}/share/hadoop/common/lib/slf4j-api-1.7.5.jar:${HADOOP_HOME}/share/hadoop/common/lib/slf4j-log4j12-1.7.5.jar:${HADOOP_HOME}/share/hadoop/common/lib/snappy-java-1.0.4.1.jar:${HADOOP_HOME}/share/hadoop/common/lib/stax-api-1.0-2.jar:${HADOOP_HOME}/share/hadoop/common/lib/xmlenc-0.52.jar:${HADOOP_HOME}/share/hadoop/common/lib/xz-1.0.jar:${HADOOP_HOME}/share/hadoop/common/lib/zookeeper-3.4.6.jar

#hbase 
export CLASSPATH=${CLASSPATH}:${HBASE_HOME}/lib/commons-codec-1.7.jar:${HBASE_HOME}/lib/hbase-client-0.98.24-hadoop2.jar:${HBASE_HOME}/lib/hbase-common-0.98.24-hadoop2.jar:${HBASE_HOME}/lib/hbase-hadoop2-compat-0.98.24-hadoop2.jar:${HBASE_HOME}/lib/hbase-hadoop-compat-0.98.24-hadoop2.jar:${HBASE_HOME}/lib/hbase-it-0.98.24-hadoop2.jar:${HBASE_HOME}/lib/hbase-prefix-tree-0.98.24-hadoop2.jar:${HBASE_HOME}/lib/hbase-protocol-0.98.24-hadoop2.jar:${HBASE_HOME}/lib/hbase-server-0.98.24-hadoop2.jar:${HBASE_HOME}/lib/hbase-shell-0.98.24-hadoop2.jar:${HBASE_HOME}/lib/hbase-testing-util-0.98.24-hadoop2.jar:${HBASE_HOME}/lib/hbase-thrift-0.98.24-hadoop2.jar:${HBASE_HOME}/lib/htrace-core-2.04.jar:${HBASE_HOME}/lib/metrics-core-2.2.0.jar
```

#  **写在最后**

这篇和HADOOP初探（一）加在一起是我写的第一篇CSDN博文，甚至可以说是我在网上公开的第一篇文章。自己的编程过程中通过CSDN着实收到了不小的帮助，也看过了很多的大神的博文，自己真的动手写来发现自己还差得远，觉得自己写的东西太简单，在CSDN这个高手云集的地方肯定不少人都写过类似的文章。但是自己作为小白就要有小白的觉悟，踏踏实实做事，认真记下自己做的事，如果能帮助到如我遇到一样问题的人再好不过。即使不能也算是对自己思路的整理。回头看看如果再让我安装一遍可能半天时间就够了，但是这一个个问题解决下来却用了我三天不到。希望慢慢积累下来，以后的自己也可以面对新的技术新的挑战，游刃有余，从容不迫。
