



由于工作需要，本篇文章尝试 Kafka + SparkStreaming 编程。

总的来说，流计算秉承一个基本理念，即数据的价值随着时间的流逝而降低。因此，当事件出现时就应该立即进行处理，而不是缓存起来进行批量处理。为了及时处理流数据，就需要一个低延迟、可扩展、高可靠的处理引擎。

## Pharm环境

#### 参考文章
[使用PyCharm配置Spark的Python开发环境 ](http://blog.tomgou.xyz/shi-yong-pycharmpei-zhi-sparkde-pythonkai-fa-huan-jing.html)
[PyCharm 常用快捷键和设置](https://blog.csdn.net/weixin_41059146/article/details/78826163)

#### 解决Ubuntu中Ctrl+Space和输入法冲突的问题
设置->文本输入，选择带有Fcitx标记的输入源，点击扳手图标进入输入法配置界面，在全局配置中取消快捷键。

#### Spark环境说明
在我PC机上使用的是Hadoop+Spark环境，工作的时候

<!-- more -->

## Spark Streaming

### 简介

一个RDD的处理称为一个“血缘关系（Lineage）”，即DAG拓扑排序的结果。采用惰性调用，通过血缘关系连接起来的一系列RDD操作就可以实现管道化（pipeline），避免了多次转换操作之间数据同步的等待，而且不用担心有过多的中间数据，因为这些具有血缘关系的操作都管道化了，一个操作得到的结果不需要保存为中间数据，而是直接管道式地流入到下一个操作进行处理。同时，这种通过血缘关系把一系列操作进行管道化连接的设计方式，也使得管道中每次操作的计算变得相对简单，保证了每个操作在处理逻辑上的单一性；相反，在MapReduce的设计中，为了尽可能地减少MapReduce过程，在单个MapReduce中会写入过多复杂的逻辑。

Spark Streaming是Spark的核心组件之一，为Spark提供了可拓展、高吞吐、容错的流计算能力。如下图所示，Spark Streaming可整合多种输入数据源，如Kafka、Flume、HDFS，甚至是普通的TCP套接字。经处理后的数据可存储至文件系统、数据库，或显示在仪表盘里。

Spark Streaming的基本原理是将实时输入数据流以时间片（秒级）为单位进行拆分，然后经Spark引擎以类似批处理的方式处理每个时间片数据。

Spark Streaming最主要的抽象是DStream（Discretized Stream，离散化数据流），表示连续不断的数据流。在内部实现上，Spark Streaming的输入数据按照时间片（如1秒）分成一段一段的DStream，每一段数据转换为Spark中的RDD，并且对DStream的操作都最终转变为对相应的RDD的操作。例如，下图展示了进行单词统计时，每个时间片的数据（存储句子的RDD）经flatMap操作，生成了存储单词的RDD。整个流式计算可根据业务的需求对这些中间的结果进一步处理，或者存储到外部设备中。

### 对比Storm

Spark Streaming和Storm最大的区别在于，Spark Streaming无法实现毫秒级的流计算，而Storm可以实现毫秒级响应。

Spark Streaming无法实现毫秒级的流计算，是因为其将流数据按批处理窗口大小（通常在0.5~2秒之间）分解为一系列批处理作业，在这个过程中，会产生多个Spark 作业，且每一段数据的处理都会经过Spark DAG图分解、任务调度过程，因此，无法实现毫秒级相应。Spark Streaming难以满足对实时性要求非常高（如高频实时交易）的场景，但足以胜任其他流式准实时计算场景。相比之下，Storm处理的单位为Tuple，只需要极小的延迟。

Spark Streaming构建在Spark上，一方面是因为Spark的低延迟执行引擎（100毫秒左右）可以用于实时计算，另一方面，相比于Storm，RDD数据集更容易做高效的容错处理。此外，Spark Streaming采用的小批量处理的方式使得它可以同时兼容批量和实时数据处理的逻辑和算法，因此，方便了一些需要历史数据和实时数据联合分析的特定应用场合。

### Streaming 原理

在Spark中，一个应用（Application）由一个任务控制节点（Driver）和若干个作业（Job）构成，一个作业由多个阶段（Stage）构成，一个阶段由多个任务（Task）组成。当执行一个应用时，任务控制节点会向集群管理器（Cluster Manager）申请资源，启动Executor，并向Executor发送应用程序代码和文件，然后在Executor上执行task。在Spark Streaming中，会有一个组件Receiver，作为一个长期运行的task跑在一个Executor上。每个Receiver都会负责一个input DStream（比如从文件中读取数据的文件流，比如套接字流，或者从Kafka中读取的一个输入流等等）。Spark Streaming通过input DStream与外部数据源进行连接，读取相关数据。

### 程序框架

1. 通过创建输入DStream来定义输入源
2. 通过对DStream应用转换操作和输出操作来定义流计算。
3. 用streamingContext.start()来开始接收数据和处理流程。
4. 通过streamingContext.awaitTermination()方法来等待处理结束（手动结束或因为错误而结束）。
5. 可以通过streamingContext.stop()来手动结束流计算进程。

