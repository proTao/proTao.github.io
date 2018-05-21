---
layout: post
title: 大数据集群工作笔记
category: 大数据
tags:
- bigdata
- spark
- dataprocessing
- shell
keywords: spark bigdata
description:
---


- 日期：20180402
- 工作目标：执行C1实时处理的spark任务
- 上下文：批处理没有数据，实时处理部分kafka上有数据，我就好像一个运维加测试人员，还是很差的那种，马卫师兄作为一个研发人员，给我代码，我跑一跑，测试一下、

spark-submit命令后有错.

使用yarn application --list查看当前任务已经shutdown
在启动log中查看分配的applicationID： application_1521425076696_0157
使用yarn logs -applicationId application_1521425076696_0157查看yarn日志
发现是配置文件中kafka topic配置的问题，这部分是由马卫师兄直接生成的所有省份的日志

<!-- more -->

* * *



- 日期：20180403
- 工作目标：了解当前集群资源情况，多跑几个job
- 上下文：上午和马卫师兄沟通一下代码，下午准备多跑几个任务，先跑起来再说，但是要考虑到集群上的资源

- 进展：没有头绪，暂且搁置，复习spark


关于web界面，配置host

* * *



- 日期：20180403
- 工作目标：熟悉一下spark，跑几个wordcount，了解大致程序结构、打包方式。

1. 在spark-shell中发现默认的hdfs路径是hdfs://hadoop-master01-crs2:8020/user/cdn/SecurityConfig\_shanghai.xml
2. spark集群是on yarn，master地址是yarn-sluster
3. 第一个python脚本。提交：`spark-submit --master yarn --deploy-mode client script.py`


* * *

- 日期：20180408
- 工作目标：完成测试框架脚本
- 结果：主要工具是expect。已完成
- 主要问题：需要经常查阅shell脚本命令。还有就是expect语法不熟练，tcl语言基本就是不会，但是这次使用基本巩固了expect的基本用法，学会了使用expect的正则方式并捕获命令输出传递给环境变量，还有一些零碎的小trick，比如xargs和cut命令的结合使用；在expect中log_file将输出分流到文件；puts命令输出当前expect环境变量，stderr方便的使用标准错误输出。

- 工作目标：封装expect脚本，标准化数据输出.
- 结果：已完成.

- 工作目标：封装exe脚本，批量化数据输出.
- 结果：已完成.


* * *

- 日期：20180409
- 工作目标：理解参数，在大规模数据上运行

问题1：测试数据是纯文本，给的数据是压缩的，用手动处理吗
回答：spark的textFile可以直接读取gz文件，这个文件可以任意大小，我的有2个多G，不用担心OOM，因为这里不做处理，所以没关系

问题2：随便跑了一个小文件，看不见输出？
回答：粗心。命令中有两个地方需要设置配置文件，我只改动了一个

问题3：得到hdfs上一个文件夹的空间和多个文件的大小
`hdfs dfs -du -s -h /coll_data/dns/beijing100/20180407/100_211136028244_2018040700* | awk '{a+= $0}END{print a}'`

问题4：hadoop输入路径支持的通配符很强
参考[hadoop输入路径读取文件的正则通配符](https://blog.csdn.net/u013013024/article/details/53128071)

问题5：现在的问题是应该是给定数据大小，得到最优的参数，所谓最优的意思就是时间最短。那么这个数据怎么利用呢？
最优化方法比如DFO算法需要真正的求解函数值，一是代价大，二是肯定是数据越小时间短，因此size是一个需要固定的参数，但是他又是一个连续值。还有一个问题就是当前手头数据的不平衡，小数据的执行结果过多，大数据的执行较少。
目前可以考虑的就是首先通过插值算法或ML回归模型拟合时间函数。然后通过DFO局部最优化方法或者粒子群全局最优化方法求最小点。

问题6：配置crontab
尚未解决

问题7：job出现错误`Container killed on request. Exit code is 143`？
可能是由于物理内存达到限制，导致container被kill掉报错。目前通过增加内存到40g的方式可以解决问题。注意增加48g会突破的yarn的memory限制。
* * *




- 日期：201804010
- 工作目标：重构脚本，优化命令行参数
基本完成

- 工作目标：理解各个表的参数
对于PRE表，需要hdfs输入输出路径，然后同时会在hive的pre_table中写数据，命令参数中的省份长码只会影响到任务名。对于子表，实际上配置文件基本没用，然而省份长码会控制写出子表中的内容，这里的上分长吗要注意下。

- 问题：全国的批处理一遍太慢了，这个问题一是不能满足要求，二是影响调参效率。
* * *


- 日期：20180411
- 工作目标：尽快完成AB表数据的输出。
从代码上来看，目前AB表的处理是不区分省份的，因此我感觉有些问题，与崔老师沟通后他表示会尽快修改，并且修改之后会解决小文件太多处理过慢的问题。并表示修改之后会利用省份进行分区，
修改之后PRE的命令行参数中的省份长码会影响向hive中写数据。

- 问题：hdfs上的数据情况
内蒙古和天津9号之后的是纯文本，北京10号之后的是纯文本。

- 问题：崔老师对hive进行了partition，这个不太明白，需要查一下

- 问题：改变了spark的提交方式，从yarn变成了yarn-cluster，这个不太明白，需要查一下

- 问题：读取文件夹内篇日志文件失败

* * *

- 日期：20180412
- 问题：AB表需要测吗？怎么测？

- 问题：hadoop-slave失去连接


* * *

- 日期：20180413
- 任务：小批量数据大量测试
目前进行压缩包数据的大量测试，全部处理一遍基本需要12小时，在这一步骤中遇到问题，选取的十个数据量较小的省份中，有三个省一定会出错，目前还没有排查到原因，处理手段是放弃先放弃这三个省份，将问题提交至崔老师，然后继续跑后续省份。
目标是获得较大量程序运行结果后进行最优参数的搜索，但是目前遇到的主要几个问题是：（1）日后正式上线应该是纯文本的文件，本周发现过一次程序的问题，一次数据的问题，崔老师调整好没有问题的实时数据是本周五开始上传，导致本周没有采集到可以使用的运行时间数据。（2）程序本周内进行过一次改动，改动后程序运行时间与之前运行时间发生变化。（3）一次运行需要的时间太慢太慢，集群资源不足，无法同时并发大量任务，导致时间数据采集效率低下。目前该问题没有解决的较好办法。因此需要调整的参数较多，变动的范围较大，肯定需要大量尝试才可以得到最优参数组合。

- 问题：子表怎么知道自己处理的是哪一天的数据

* * *

- 日期：20180409 - 20180413
- 本周进展：

1. 基本掌握批处理部分全部代码逻辑，参数设置
2. 完成了自动化运行脚本，配置文件生成脚本与数据采集功能如果程序不出错，可以全部自动化完成。
3. 在测试过程中发现代码逻辑问题，与崔华俊老师协调后修复。在测试过程中发现数据问题，与崔华俊老师沟通后修改上传日志。
4. 完成了十个省份的批处理部分的6个表的整体流程与处理数据生成。


问题： 43g超出最大内存了，要小心

* * *

- 日期： 20180419
- 工作目标：初步了解hive工作原理。理解AB表工作流程，解决争吵师兄提出的问题.AB表内数据有误。

- hive 知识点：
参考：

1. [Hive之分区（Partitions）和桶（Buckets）](http://www.aahyhaa.com/archives/316)
2. [hive深入浅出](https://blog.csdn.net/hguisu/article/details/18986759)
3. [Hive原理及查询优化](https://blog.csdn.net/LW_GHY/article/details/51469753)

- AB表遇到的问题1：没有跑19号的数据，但是pre\_table中有19号的分区数据。看的是分区18号的表，但是里面的数据字段显示20180411。
分区键是dt，dt指的是哪天运行，表里面的第一个字段才是真正的数据的日期。

- 即使这样，现在等与是我今天19号，跑15号到18号的数据，dt就是19，但是表里面的字段有15-18？再有就是如果dt作为分区键，我为啥不把前一天跑的数据都删除掉？在AB表读取数据的时候只考虑省份长码，不考虑日期，这样是不是很影响效率？删除前一天表的问题是在代码中解决还是额外写脚本？

- drop table之后底层文件残留？
权限粘滞位（Sticky bit）问题，已解决

* * *

- 日期：20180420
- 问题1：A1表跑完只有几条数据吗？这几条数据里还有重复的应该是代码逻辑问题吧？我是20号对19号的三个省先跑批。为啥结果里面是1718号的数据？
没有问题，因为A1D表功能上实现的就是一天一个省份出一条日志。但是更严重的问题是后面这个，数据积压的问题，按理说理想情况是我跑19号的PRE批，跑了三个省，然后跑A1D，里面应该有三条，分别是三个省19号的统计结果。但是这个问题现在无法解决。崔老师说原因在于现在的日志是从移动一期的FTP迁移过来的，一期的集群复杂，且flume由于性能等问题导致数据积压，这个问题无法解决，但下周从二期的FTP上直接上传日志的时候再看看还有没有问题。

- 问题2：跑A1H时跑安徽的，但是pre表中应该没有安徽的数据啊？
这个问题暂且搁置

* * *

- 日期：20180423
- 问题：继续上面的问题2，尝试分析
症状是：我在20号只跑了19号的数据，先不管19号里面有其他日期的数据，省份我是只跑了三个省的，我看了一下hdfs上原始日志的内容，文件内是没有省份信息的（但是有真实的时间戳），也就是说省份信息靠文件夹定位，那么我跑了三个省份的，pre_table应该也只有三个省份了，我看了一下pre_table里面也的确只有三个省份，但是A1H跑起来的确是会有一些其他的省份出现，这个问题不行就在确认一下，但是之前周五确认过了的确有这个问题。

- 代码更新
崔老师更新一版本代码，改变dt分区模式，dt需要手动以命令行参数输入作为分区键。这样的话需要测试一些新的功能。对于我的自动化脚本来说，需要更改的地方就是remote脚本，真正提交命令的地方，其他两个脚本来维护date变量，并且表示的意思是处理那天的日志，无需改动。然后目前来看A表使用sql取数据都是同时依赖省份码和日期，解决了前面指出的问题。

- [x] 把全部hive中的table删除，然后跑省公司直接上传的数据，手动查看原始日志文件，手动查看生成的pre\_table，看看有没有数据滞后性的问题。（先跑一天的省份的）

- [x] 然后执行A1D，检查生成日期和总条数

- [x] 然后执行A1H，查看数据是否正常

- [x] 如果都没有问题，测试A2

- 工作目标：正则表达式编写
匹配闰年2月29：(([13579][26]|[2468][048])00|\d{2}([13579][26]|[2468][048]|0[48]))0229
匹配正常日期：(?:\d{4}(?:(?:1[02]|0[3578])(?:[12][0-9]|3[01]|0[1-9])|(?:0[469]|11)(?:[12][0-9]|30|0[0-9])|02(?:[1][0-9]|2[0-8]|0[1-9])))
匹配时间：([01]\d|2[0-3])[012345]\d[012345]\d
匹配14位时间戳：(?:(([13579][26]|[2468][048])00|\d{2}([13579][26]|[2468][048]|0[48]))0229|(?:\d{4}(?:(?:1[02]|0[3578])(?:[12][0-9]|3[01]|0[1-9])|(?:0[469]|11)(?:[12][0-9]|30|0[0-9])|02(?:[1][0-9]|2[0-8]|0[1-9]))))([01]\d|2[0-3])[012345]\d[012345]\d

用新的正则表达式匹配原来配置文件中的匹配规则，只需要改pre的就行，子表的配置文件中的相关项目可以删掉了


* * *

- 日期：20180427
- 任务：理解zookeeper

参考：

1. 《大数据日知录：架构与算法》
2. [ZAB协议分析](http://blog.jobbole.com/104985/)
3. [zookeeper CLI](https://www.w3cschool.cn/zookeeper/zookeeper_cli.html)


* * *

- 日期：20180428
- 任务：配置zookeeper，kafka，spark，编写spark streaming

Spark Streaming这一部分分到第三篇去屑。

* * *

- 日期：五一假期回来的三个工作日
- 任务1：尝试编写SparkStreaming（杨老师说暂且不用）

大致配了环境，看了一下《大数据》那本书中的流处理算法，没有实现


- 任务2：完善最优参数搜索
当前的解决方案是对每个省建立一个GradientBoosting回归模型，然后认为对回归模型的拟合函数求各个参数对预测运行时间的的最优参数。使用python的pyswarms工具包（实现了粒子群算法）对函数空间进行搜索，因为已经对各个特征进行过最大最小规格化了，所以是有界的最小值搜索。目前函数已封装完毕。

- 问题1：实践中意识到在线学习算法的重要性，能否改进为在线算法？
- 问题2：上述做法的一个强假设是每个省每天的数据量相同或者在TB的量级上稳定，不过我看了一下现有的数据，很难做到这一点。那么就要考虑把数据量做为特征，但是这么做了之后发现无论是分省份还是全国建立一个统一模型，效果都不如上面的这个方法好，后面还可以优化一下。现在这个方法就是批训练，训练一次之后模型固定，找到的最优点也是一样的，除非有新的数据再次训练。


- 任务3：A1D表debug
出现的问题是int类型精度不够，我追踪变量看了半天，觉得没有问题了，但是运行还是会被int的最大值截掉。最后交给崔华俊老师那边改，一晚上就改完了，是开头case class语句的问题。
我之前也一直疑惑生成表的时候表中的数据类型在哪里定义。我找的的问题是给一个表传值的时候的确传的是一个Long了，但是这个表的字段类型声明成int的了，就自动截取了。

> 当一个类被声名为case class的时候，scala会帮助我们做下面几件事情：
1 构造器中的参数如果不被声明为var的话，它默认的话是val类型的，但一般不推荐将构造器中的参数声明为var
2 自动创建伴生对象，同时在里面给我们实现子apply方法，使得我们在使用的时候可以不直接显示地new对象
3 伴生对象中同样会帮我们实现unapply方法，从而可以将case class应用于模式匹配，关于unapply方法我们在后面的“提取器”那一节会重点讲解
4 实现自己的toString、hashCode、copy、equals方法
除此之此，case class与其它普通的scala类没有区别

参考[Scala入门到精通——第十四节 Case Class与模式匹配（一）](https://blog.csdn.net/lovehuangjiaju/article/details/47176829)


* * *


- 日期：20180508
- 任务：跑数据，现在有五个省份了。

回家回来第一周崔给了新的代码，但是实际运行起来并没有想象的快，而且还是有奇怪的A1D的跑一天出两天的问题。然后我直接把coallapse函数删掉了，只保留filter函数，速度变成原来那样子了，但是还是有跑一天出两天的问题，这个问题我索性先不想了。

- 任务：自动跑一天的脚本
TODO

- 任务：维护FTP上数据上传的任务

任务分解
- [x] 监控flume的运行，将失败的进程重启
- [x] 设置定时任务


进程监控脚本
```bash
#!/bin/bash

# 需要手动设置的参数
if [[ $# != 3 ]]
then
	echo 参数数目不正确
	echo 三个参数为: 1.flume agent数目；2. 省份全拼；3. 省份短码
	exit 1
fi
agent_num=$1
province=$2
short_code=$3



# set environment
function setEnvironment
{
	source /etc/profile
	JAVA_HOME="/opt/apps/java/jdk1.7.0_80"
	HADOOP_COMMON_LIB_NATIVE_DIR=/opt/apps/flume/hadoop/lib/native
	HDFS_CONF_DIR=/opt/apps/flume/hadoop/etc/hadoop
	HADOOP_HDFS_HOME=/opt/apps/flume/hadoop
	HADOOP_CONF_DIR=/opt/apps/flume/hadoop/etc/hadoop
	HADOOP_OPTS=-Djava.library.path=/opt/apps/flume/hadoop/lib:/opt/apps/flume/hadoop/lib/native
	HADOOP_HOME=/opt/apps/flume/hadoop
	PATH=/usr/lib64/qt-3.3/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/opt/apps/java/jdk1.7.0_80/bin:/opt/apps/flume/bin:/opt/apps/flume/hadoop/sbin:/opt/apps/flume/hadoop/bin:.:/home/cdn/bin:/opt/apps/java/jdk1.7.0_80/bin:/opt/apps/flume/bin:/opt/apps/flume/hadoop/sbin:/opt/apps/flume/hadoop/bin:.
	FLUME_HOME=/opt/apps/flume
	export JAVA_HOME HADOOP_COMMON_LIB_NATIVE_DIR HDFS_CONF_DIR HADOOP_HDFS_HOME HADOOP_CONF_DIR HADOOP_OPTS HADOOP_HOME PATH FLUME_HOME
	#env
}

function getpid()
{
	# $1: flume agent name
	pid_res=`ps aux | grep $1 | grep -v grep | awk '{print $2}'`
	return $pid_res
}

function isInArray
{
	# $1 被检索元素
	# $2 被检索字符串列表(不是数组)
	# return : 存在返回0，否则返回1
        for i in $2
        do
                if [[ $i == $1 ]]
                then
                        return 0
                fi
        done
        return 1
}

function showLocalState
{
	declare -a queue_state
	i=0
	for folder in `ls -d /data2/flume_source/spool/$province/hdfs* | cut -d / -f 6`
	do
	        queue_state[$i]=`ls -a /data2/flume_source/spool/$province/$folder/*.hdfs 2>/dev/null | wc -l`
		i=$((i+1))
	done

	echo
	echo "当前本地待上传文件数量"
	echo ${queue_state[*]}
	echo
}


echo
echo "============================`date`================================"
echo 

setEnvironment
showLocalState

# 自动设置的参数
declare -a  prefix_array
for i in `seq 1 $agent_num`
do
	prefix_array[$((i-1))]=a$i
done
date=`date +%Y%m%d`
still_running=`/opt/apps/flume/hadoop/bin/hdfs dfs -ls hdfs://hadoop-master01-crs2:8020/coll_data/dns/$province$short_code/$date/*.tmp | grep -o "a[1-9]" | xargs`


echo "All Flume Agent :" ${prefix_array[*]}
echo "Still Running :" $still_running
echo ""

for prefix in ${prefix_array[@]}
do
	isInArray $prefix "$still_running"
	if [[ $? == 1 ]]
	then
		agent_name=${prefix:0:1}3${prefix:1:1}
		echo "restart agent of $agent_name"
		pid=`ps aux | grep $agent_name | grep -v grep | awk '{print $2}'`
		echo pid of $agent_name is $pid
		kill $pid
		echo "/opt/apps/flume/bin/start-flume-$province-only-hdfs${prefix:1:1}.sh"
		/opt/apps/flume/bin/start-flume-$province-only-hdfs${prefix:1:1}.sh
		echo ""
	fi
done


```

第一个子任务：脚本没什么问题，函数数组传参时遇到了一些问题，整理到博客《Bash笔记中》。
第二个字任务：耽误了不少时间，原因在于第一点是cron表达式第一个设置的是分钟数，我以为是秒数了，crontab会自动报错。后来在博客中看到cron最小执行时间单位是分钟。还有就是crontab执行的时候内部环境和外部环境不同，一些环境变量需要重新设置，这部分我写在setEnvironment函数中了。另外，检查crontab的日志很重要，这部分日志在`/var/log/cron`。
但是最后我发现在业务集群中只靠`/etc/profile`无法导入全部环境变量比如很多有关hadoop的路径都没有，使得flume-ng起不来，最后使用笨方法，手动执行env，将crontab需要的环境变量硬编码到脚本里，再用source生效。

参考：
1. [在线Crontab表达式执行时间验证](http://www.atool.org/crontab.php)
2. [shell 定时任务对java_home的影响](https://www.cnblogs.com/yht-817/p/7248584.html)

Tips：可以通过外网登录ftp。首先配置了一下~/.ssh/config，设置ftp别名。



```bash
Host ftp01
Hostname 117.128.6.128
Port 10022
User cdn
```

* * *

- 日期：20180509

任务分解：
- [x] 需要在服务器写一个脚本，类似于之前写的，去每天跑应该执行的任务

脚本没啥难的，但是还是用了快一天的时间。这里对任务计时的方法和之前不一样了，之前是用time命令，这次是用yarn中的日志，从日志里面匹配出开始和结束的时间戳，然后转换为运行时间。精确度的话取前十位精确到秒就行。

```bash
#!/bin/bash

function getRunningTime
{
	# $1 applicationId
	python getRunningTime.py ` yarn application -status $1 | grep --color=auto -E -o " [0-9]{13}" | xargs`
}


function randomExec
{
	# $1 : which batch process : Pre / A1D / A2D / A2HB2 / B1 / A1H
	# $2 : province
	# $3 : date
	# 功能：执行批处理任务并生成日志
	echo $*

	# random choose parameters
	if [[ $1 == A1D ]]||[[ $1 == A2D ]]||[[ $1 == A2HB2 ]]||[[ $1 == A1H ]]
	then
		# m emory : 10 ~ 18
		# e xecutors : 25 ~ 30
		# c ores : 3 ~ 4
		# p arallelism : 100 ~ 240
		m_base=10
		e_base=25
		c_base=3
		p_base=100
		m_delta=$((RANDOM%9))
		e_delta=$((RANDOM%6))
		c_delta=$((RANDOM%2))
		p_delta=$((RANDOM%130))
	else
		# m emory : 10 ~ 18
		# e xecutors : 60 ~ 120
		# c ores : 2 ~ 4
		# p arallelism : 280 ~ 450
		m_base=10
		e_base=60
		c_base=2
		p_base=280
		m_delta=$((RANDOM%9))
		e_delta=$((RANDOM%60))
		c_delta=$((RANDOM%3))
		p_delta=$((RANDOM%170))
	fi

	# generate temporary config file
	if [[ $1 == A1D ]]||[[ $1 == A2D ]]||[[ $1 == A2HB2 ]]||[[ $1 == A1H ]]
	then
		cp ./DataCheck-DW.xml ./$2-$3.xml
	else
		sed -e s/'PROVINCE'/$province/ -e s/'DATE'/$date/ -e s/'SHORTCODE'/$short_code/ source/template.xml > ./$2-$3.xml
	fi


	# submit spark job
	echo   "spark-submit --master yarn-cluster --driver-memory 1g --num-executors $((e_base+e_delta)) --executor-memory $((m_base+m_delta))g  --executor-cores $((c_base+c_delta)) --conf spark.default.parallelism=$((p_base+p_delta)) --files $2-$3.xml --class cn.ac.iie.iaa.SparkSecBatch$1  CRS-SecBatch-$1-assembly-1.0.jar $2-$3.xml $2 $3 > $2-$3.log 2&>1"

	spark-submit --master yarn-cluster --driver-memory 1g --num-executors $((e_base+e_delta)) --executor-memory $((m_base+m_delta))g  --executor-cores $((c_base+c_delta)) --conf spark.default.parallelism=$((p_base+p_delta)) --files $2-$3.xml --class cn.ac.iie.iaa.SparkSecBatch$1  CRS-SecBatch-$1-assembly-1.0.jar $2-$3.xml $2 $3 > $2-$3.log 2>&1

	# delete temporary config file
#	rm $2-$3.xml

	mv ./$2-$3.log log/
}

function BatchProcess
{
	# $1 : folder name
	# $2 : province
	# $3 : date
	echo $1表处理，开始于 `date +"(%y-%m-%d) %H:%M:%S"`
	cd /home/cdn/workspace/zhangyongtao/$1
	tablename=`echo $1 | tr -d "_"`
	randomExec $tablename $2 $3
	echo $1表处理，结束于 `date +"(%y-%m-%d) %H:%M:%S"`
	echo ----------------------------------------------
}

province=$1
date=$2
long_code=`python /home/cdn/workspace/zhangyongtao/Pre/script/code.py $province | cut -d ' ' -f 2`
short_code=`python /home/cdn/workspace/zhangyongtao/Pre/script/code.py $province | cut -d ' ' -f 3`
folders=("Pre" "A1_D" "A1_H" "A2_D" "A2H_B2" "B1")
echo "=============================`date`================================="
echo $*
for i in ${folders[@]}
do
	BatchProcess $i $province $date
done
```


* * *

日期：20180514

任务分解：

- [ ] 定时删除脚本产生的日志
- [x] 优化flume监控脚本
- [x] 监控upload脚本（暂时取消该任务）
- [x] 优化定时批处理脚本
- [ ] 自动进行任务分配？？（给自己的任务）
- [ ] 青海省的flumeagent起得太多了？？？（目前来看不是大问题，写完upload监控再说）

1. 完成对flume监控脚本的优化，抽象出变量，方便在不同机器上进行部署。另外增加监控当前剩余文件数的功能，方便调试。
2. 完善定时批处理脚本：任务名修改；增加对数据量大小的数据收集；统一成功失败的日志输出格式。


* * *

日期：20180517

- [x] 定时删除脚本产生的日志
- [ ] 优化定时批处理脚本

任务分解：
```bash
/home/cdn/workspace/yjyj/upload*.log {
	daily
	nocompress
	notifempty
	rotate 3
	dateext
	olddir /home/cdn/workspace/yjyj/oldlog
	size 6M
}
```

1. 对日志的定时清理我选择使用logrotate服务，在使用脚本put到hdfs上的机器上部署logrotate任务即可。这里所谓的部署也只是新增指定格式的logrotate配置，然后logrotate会定时执行。如上述代码所示，表示每天执行、不进行压缩、忽略空文件、保存三个轮转旧文件、自动添加日期后缀、旧文件存放到指定文件夹、对指定大小以下的日志不予处理。目前已经在甘肃广东江西山西的ftp上进行配置
2. 对输出日志的统一管理


上传文件配置情况

日志统一存放于：`home/cdn/workspace/yjyj`
日志轮转配置：daily，10M

| 省份 | 大小 | 上传方式 | logrotate | 并发数 |
| ---- | ---- | ----- | ------ | ---- |
| 甘肃391 | 1.3T | put | 是 | 6 |
| 广东200 | 2.5T | put | 是 | 3 |
| 江西791 | 2.3T | put |  是 | 6 |
| 青海971 | 0.3T | flume |  否 | 6 |
| 山西351 | 1.8T | put | 是 | 6 |
| 天津220 | 0.8T | flume |  否 | 6 |
| 宁夏951 | | flume | 否 | 3 |
| 上海210 | | flume | 否 | 3 |
| 贵州851 | | put | 是 | 6 |
| 黑龙江451 | | put | 是 | 6 |
| 辽宁240 | | put | 是 | 6 |
| 湖北270 | | put | 是 | 6 |



参考：
[Linux日志文件总管——logrotate](https://linux.cn/article-4126-1.html)
[linux下logrotate 配置和理解](https://blog.csdn.net/cjwid/article/details/1690101)

* * *



参考资料:
1. [linux time命令详解](http://blog.chinaunix.net/uid-26557245-id-3782974.html)
2. [expect基础语法](https://blog.csdn.net/k122769836/article/details/49051243)
3. [expect用法](https://www.cnblogs.com/tychyg/p/5086499.html)
4. [spark通过合理设置spark.default.parallelism参数提高执行效率](https://blog.csdn.net/bbaiggey/article/details/51984753)
5. [spark 资源参数调优](https://www.cnblogs.com/bonelee/p/6042267.html)
6. [Spark性能优化指南——基础篇](https://tech.meituan.com/spark-tuning-basic.html)
7. [Spark性能优化指南——高级篇](https://tech.meituan.com/spark-tuning-pro.html)
8. [关于sparksql on yarn生成大量.hive-staging文件问题](http://www.aboutyun.com/thread-20657-1-1.html)



