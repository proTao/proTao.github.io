---
layout: post
title: 大数据集群工作笔记
category: 大数据
tags:
- bigdata
- dataprocessing
- machinelearning
- shell
---




* * *

- 日期：20180408
- 工作目标：完成测试框架脚本
- 结果：主要工具是expect。已完成
- 主要问题：需要经常查阅shell脚本命令。还有就是expect语法不熟练，tcl语言基本就是不会，但是这次使用基本巩固了expect的基本用法，学会了使用expect的正则方式并捕获命令输出传递给环境变量，还有一些零碎的小trick，比如xargs和cut命令的结合使用；在expect中log\_file将输出分流到文件；puts命令输出当前expect环境变量，stderr方便的使用标准错误输出。

- 工作目标：封装expect脚本，标准化数据输出.
- 结果：已完成.

- 工作目标：封装exe脚本，批量化数据输出.
- 结果：已完成.


* * *

- 日期：20180409
- 工作目标：理解参数，在大规模数据上运行

问题1：测试数据是纯文本，给的数据是压缩的，用手动处理吗
回答：spark的textFile可以直接读取gz文件，这个文件可以任意大小，我的有2个多G，不用担心OOM，因为这里不做处理，所以没关系

问题2：得到hdfs上一个文件夹的空间和多个文件的大小
`hdfs dfs -du -s -h /coll_data/dns/beijing100/20180407/100_211136028244_2018040700* | awk '{a+= $0}END{print a}'`

问题3：hadoop输入路径支持的通配符很强
参考[hadoop输入路径读取文件的正则通配符](https://blog.csdn.net/u013013024/article/details/53128071)

问题4：现在的问题是应该是给定数据大小，得到最优的参数，所谓最优的意思就是时间最短。那么这个数据怎么利用呢？
最优化方法比如DFO算法需要真正的求解函数值，一是代价大，二是肯定是数据越小时间短，因此size是一个需要固定的参数，但是他又是一个连续值。还有一个问题就是当前手头数据的不平衡，小数据的执行结果过多，大数据的执行较少。
目前可以考虑的就是首先通过插值算法或ML回归模型拟合时间函数。然后通过DFO局部最优化方法或者粒子群全局最优化方法求最小点。



- drop table之后底层文件残留？
权限粘滞位（Sticky bit）问题，已解决


- 工作目标：正则表达式编写
匹配闰年2月29：(([13579][26]|[2468][048])00|\d{2}([13579][26]|[2468][048]|0[48]))0229
匹配正常日期：(?:\d{4}(?:(?:1[02]|0[3578])(?:[12][0-9]|3[01]|0[1-9])|(?:0[469]|11)(?:[12][0-9]|30|0[0-9])|02(?:[1][0-9]|2[0-8]|0[1-9])))
匹配时间：([01]\d|2[0-3])[012345]\d[012345]\d
匹配14位时间戳：(?:(([13579][26]|[2468][048])00|\d{2}([13579][26]|[2468][048]|0[48]))0229|(?:\d{4}(?:(?:1[02]|0[3578])(?:[12][0-9]|3[01]|0[1-9])|(?:0[469]|11)(?:[12][0-9]|30|0[0-9])|02(?:[1][0-9]|2[0-8]|0[1-9]))))([01]\d|2[0-3])[012345]\d[012345]\d

用新的正则表达式匹配原来配置文件中的匹配规则，只需要改pre的就行，子表的配置文件中的相关项目可以删掉了



- 任务：完善最优参数搜索
当前的解决方案是对每个省建立一个GradientBoosting回归模型，然后认为对回归模型的拟合函数求各个参数对预测运行时间的的最优参数。使用python的pyswarms工具包（实现了粒子群算法）对函数空间进行搜索，因为已经对各个特征进行过最大最小规格化了，所以是有界的最小值搜索。目前函数已封装完毕。

- 问题1：实践中意识到在线学习算法的重要性，能否改进为在线算法？
- 问题2：上述做法的一个强假设是每个省每天的数据量相同或者在TB的量级上稳定，不过我看了一下现有的数据，很难做到这一点。那么就要考虑把数据量做为特征，但是这么做了之后发现无论是分省份还是全国建立一个统一模型，效果都不如上面的这个方法好，后面还可以优化一下。现在这个方法就是批训练，训练一次之后模型固定，找到的最优点也是一样的，除非有新的数据再次训练。




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

第一个子任务：脚本没什么问题，函数数组传参时遇到了一些问题，整理到博客《Bash笔记中》。
第二个字任务：耽误了不少时间，原因在于第一点是cron表达式第一个设置的是分钟数，我以为是秒数了，crontab会自动报错。后来在博客中看到cron最小执行时间单位是分钟。还有就是crontab执行的时候内部环境和外部环境不同，一些环境变量需要重新设置，这部分我写在setEnvironment函数中了。另外，检查crontab的日志很重要，这部分日志在`/var/log/cron`。
但是最后我发现在业务集群中只靠`/etc/profile`无法导入全部环境变量比如很多有关hadoop的路径都没有，使得flume-ng起不来，最后使用笨方法，手动执行env，将crontab需要的环境变量硬编码到脚本里，再用source生效。


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

* * *

日期：20180514

任务分解：

- [x] 定时删除脚本产生的日志
- [x] 优化flume监控脚本
- [x] 监控upload脚本（暂时取消该任务）
- [x] 优化定时批处理脚本
- [ ] 自动进行任务分配？？（给自己的任务）
- [x] 青海省的flumeagent起得太多了？？？（目前来看不是大问题，写完upload监控再说）

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

| 省份 | 大小 | 上传方式 | logrotate | 并发数 | 状态 |
| ---- | ---- | ----- | ------ | ---- | --- |
| 甘肃391 | 1.3T | put | 是 | 6 | 已关闭 |
| 广东200 | 2.5T | put | 是 | 3 | 已关闭 |
| 江西791 | 2.3T | put |  是 | 6 | 已关闭 |
| 青海971 | 0.3T | flume |  否 | 6 | 已关闭 |
| 山西351 | 1.8T | put | 是 | 6 | 已关闭 |
| 天津220 | 0.8T | flume |  否 | 6 | 已关闭 |
| 宁夏951 | 0.5T | flume | 否 | 3 | 已关闭 |
| 上海210 | 0.5T | flume | 否 | 3 | 已关闭 |
| 贵州851 | 1.9T | put | 是 | 6 | 已关闭 |
| 黑龙江451 | 2T | put | 是 | 6 | 已关闭 |
| 辽宁240 | 3.3T | put | 是 | 6 | 已关闭 |
| 湖北270 | 4.4T | put | 是 | 9 | 已关闭 |



* * *

日期：20180520
任务：部署10个省份的任务。


* * *

日期：20180521
优化脚本：
- [ ] 修改有问题的return语句
- [ ] 整理日志
- [ ] 日志中记录ApplicationId

* * *

日期：20180625
该安全模块正式结束，整理已有工作。

## 第一部分工作：
开始工作时，在本地机器执行命令收集信息。使用 expect 工具远程登录跳板机后登录目标机，执行 spark-submit 命令，通过 time 命令对执行任务计时，然后回传该时间。然后exe脚本调用remote脚本，记录日志。batch脚本封装exe脚本，对不同省份批量执行，并且对参数进行有限的波动。这部分代码如下。

- remote.sh:

```bash
#!/usr/bin/expect
 # Author: protao
 # 脚本功能，登录远程服务器执行spark job，记录源文件大小与执行时间，通过标准错误输出返回
 # Date: 2018-4-8

# expect 输出日志
# log_file time

# 读取命令行参数
set m [lindex $argv 0]
set e [lindex $argv 1]
set k [lindex $argv 2]
set p [lindex $argv 3]
set date [lindex $argv 4]
set province [lindex $argv 5]
set work_dir [lindex $argv 6]

# 设置常量
set timeout -1 
set USERNAME "×××"
set JUMP "×××.×××.×.××"
set TERMINAL "××.××.×.×××"
set PASSWORD "×××××××"
set PORT "××××"

# DEBUG
puts $date
puts $province
puts $work_dir

# 登录跳板机
spawn ssh -p $PORT ${USERNAME}@${JUMP}
expect "*password:" 
send "${PASSWORD}\r"

# 登录 terminal02
expect "cdn" 
send "ssh -p $PORT $USERNAME@$TERMINAL\r"
expect "*password:" 
send "${PASSWORD}\r"

# 进入工作目录
expect "cdn"
send "cd workspace/zhangyongtao/$work_dir\r"

# 获取省份长短码
expect "cdn"
send "python script/code.py $province|cut -d ' ' -f 2,3\r"
expect -re "\r\n(\[0-9\]*).(\[0-9\]*)\r\n"
send "\r"
set long_code $expect_out(1,string)
set short_code $expect_out(2,string)

# shannxi -> shanxi
if { $province == "shannxi" } {
	set province "shanxi"
}

# 删除hdfs输出目录
expect "cdn" 
send "hdfs dfs -rm -r /coll_data/security_dns/$province$short_code/$date\r"
#send "\r"


# 生成配置文件
expect "cdn"
send "sed -e s/'PROVINCE'/$province/ -e s/'DATE'/$date/ -e s/'SHORTCODE'/$short_code/ source/template.xml > $province-$date.xml\r"

# 提交任务
expect "cdn"
send "(time spark-submit --master yarn-cluster --name SparkSecBatchPre-$province-$date --queue security --driver-memory 1g --num-executors ${e} --executor-memory ${m}g  --executor-cores ${k} --conf spark.default.parallelism=${p} --files $province-$date.xml --class cn.ac.iie.iaa.SparkSecBatchPre  CRS-SecBatchPre-assembly-1.0.jar $province-$date.xml ${long_code} ${date} 1>/dev/null) 2>$province-$date.log\r"

# 移动日志和配置文件
expect "cdn"
send "mv $province-$date.xml xml\r"
expect "cdn"
send "mv $province-$date.log log\r"

# 获取输入数据总大小
## （tcl语言中中括号有特殊含义，先转义。而且注意这里一定要加上\r\n,这样才能捕获中间行的数字）
expect "cdn"
send "hdfs dfs -du -s -h /coll_data/dns/$province$short_code/$date | cut -d ' ' -f 1,2\r"
expect -re "\r\n(\[0-9\.\]+ \[MGT\])\r\n"
send "tail -3 log/$province-$date.log\r"  
set datasize $expect_out(1,string)

# 获取执行时间
expect -re "real(.*?)s.*user(.*?)s.*sys(.*?)s"
send "\r" 
set realtime $expect_out(1,string)
set usertime $expect_out(2,string)
set systime $expect_out(3,string)

# 返回本地机器
expect "cdn" 
send "exit\r"
expect "*closed"
send "exit\r"	

# 通过标准错误流返回数据
puts stderr $datasize
puts stderr $realtime
puts stderr $usertime
puts stderr $systime

expect eof
```

- exe.sh

```bash
#!/bin/bash
 # Author: protao
 # 脚本功能，封装remote.sh，写入日志
 # Date: 2018-4-8

while getopts ":m:e:c:p:o:d:" opt
do
        case $opt in
        m)
                memory=$OPTARG
                ;;
        e)
                executors=$OPTARG
                ;;
	c)
                cores=$OPTARG
                ;;
	p)
		parallelism=$OPTARG
		;;
	o)
		object=$OPTARG
		;;
	d)
		date=$OPTARG
		;;
        ?)
                echo "error"
                exit 1
        esac
done

echo "m=$memory, e=$executors, c=$cores, p=$parallelism" >>raw.log
./second_remote.sh $memory $executors $cores $parallelism $date $object PRE 1>/dev/null 2>>raw.log
echo $memory, $executors, $cores, $parallelism, `tail -4 raw.log | xargs | cut -d ' ' -f 1,2,3 | sed -e s/' '/''/ -e s/' '/', '/`, $object, $date >> realtime.csv
```

- batch.sh

```bash
provinces="qinghai gansu jiangxi shanxi tianjin"
dates="20180507"
for repeat in `seq 1`
do
	for date in $dates
	do
		for province in $provinces 
		do
			# memory : 10 ~ 19
			# executors : 60 ~ 120
			# cores : 2 ~ 4
			# parallelism : 300 ~ 500
			m_base=10
			e_base=60
			c_base=2
			p_base=300
			m_delta=$((RANDOM%10)) 
			e_delta=$((RANDOM%60))
			c_delta=$((RANDOM%3))
			p_delta=$((RANDOM%200))
			echo "./second_exe.sh -m $((m_base+m_delta)) -e $((e_base+e_delta)) -c $((c_base+c_delta)) -p $((p_base+p_delta)) -d $date -o $province" | tee batch.log
			./second_exe.sh -m $((m_base+m_delta)) -e $((e_base+e_delta)) -c $((c_base+c_delta)) -p $((p_base+p_delta)) -d $date -o $province
		done
	done
done
```
然后对参数与执行时间的关系进行建模，预测最佳参数，这部分代码上传到[notebook Repositories](https://github.com/proTao/jupyter-notebook)中。

## 第二部分工作
出于最后验收和方便其他同事使用的目的，直接在服务器上部署定时任务，完成类似于第一部分工作的内容。一个改变是计时方式从使用time命令计时变成了从yarn调度器中查询执行时间。
```bash
#!/bin/bash
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
        env
        hdfs
        spark-submit
}


function getRunningTime
{
        # $1 applicationId
        python /home/cdn/workspace/zhangyongtao/workspace/script/getRunningTime.py ` yarn application -status $1 | grep --color=auto -E -o " [0-9]{13}" | xargs`
}

function randomExec
{
        # $1 : which batch process : Pre / A1D / A2D / A2HB2 / B1 / A1H
        # $2 : province
        # $3 : date
        # $4 : province long id
        # 功能：执行批处理任务并生成日志
        echo $*

        # random choose parameters
        if [[ $1 == A1D ]]||[[ $1 == A2D ]]||[[ $1 == A2HB2 ]]||[[ $1 == A1H ]]
        then
                # m emory : 13 ~ 18
                # e xecutors : 40 ~ 60
                # c ores : 3 ~ 4
                # p arallelism : 120 ~ 240
                m_base=13
                e_base=40
                c_base=3
                p_base=120
                m_delta=$((RANDOM%6))
                e_delta=$((RANDOM%20))
                c_delta=$((RANDOM%2))
                p_delta=$((RANDOM%120))
        else
                # m emory : 16 ~ 18
                # e xecutors : 100 ~ 125
                # c ores : 3 ~ 4
                # p arallelism : 280 ~ 450
                m_base=16
                e_base=100
                c_base=3
                p_base=280
                m_delta=$((RANDOM%3))
                e_delta=$((RANDOM%25))
                c_delta=$((RANDOM%2))
                p_delta=$((RANDOM%170))
        fi

        # generate temporary config file
        if [[ $1 == A1D ]]||[[ $1 == A2D ]]||[[ $1 == A2HB2 ]]||[[ $1 == A1H ]]
        then
                cp ./DataCheck-DW.xml ./$2-$3.xml
        else
                sed -e s/'PROVINCE'/$province/ -e s/'DATE'/$date/ -e s/'SHORTCODE'/$short_code/ source/template.xml > ./$2-$3.xml
        fi

        # 临时参数文件
        data_size=`hdfs dfs -du -s -h /coll_data/dns/$province$short_code/$date | cut -d ' ' -f 1,2`
        echo -n $((m_base+m_delta)),$((e_base+e_delta)),$((c_base+c_delta)),$((p_base+p_delta)),$province,$date,$data_size, > $2-$3.tmp

        # submit spark job
        echo   "spark-submit --master yarn-cluster --driver-memory 1g --num-executors $((e_base+e_delta)) --executor-memory $((m_base+m_delta))g  --executor-cores $((c_base+c_delta)) --conf spark.default.parallelism=$((p_base+p_delta)) --files $2-$3.xml --class cn.ac.iie.iaa.SparkSecBatch$1  CRS-SecBatch-$1-assembly-1.0.jar $2-$3.xml $2 $3 > $2-$3.log 2>&1"

        spark-submit --master yarn-cluster  --name SparkSecBatch$1-$2-$3 --queue security --driver-memory 1g --num-executors $((e_base+e_delta)) --executor-memory $((m_base+m_delta))g  --executor-cores $((c_base+c_delta)) --conf spark.default.parallelism=$((p_base+p_delta)) --files $2-$3.xml --class cn.ac.iie.iaa.SparkSecBatch$1  CRS-SecBatch-$1-assembly-1.0.jar $2-$3.xml $4 $3 > $2-$3.log 2>&1

        # delete temporary config file
        rm $2-$3.xml

        # 归档日志
        mv ./$2-$3.log log/
}


function BatchProcess
{
        # $1 : folder name
        # $2 : province
        # $3 : date
        # $4 : province long_code
        # return : status (SUCCEEDED or FAILED)
        echo $1表处理，开始于 `date +"(%y-%m-%d) %H:%M:%S"`
        cd /home/cdn/workspace/zhangyongtao/$1
        tablename=`echo $1 | tr -d "_"`
        randomExec $tablename $2 $3 $4

        # 获取job执行状态与执行时间
        status=`tail -20 log/$2-$3.log | grep "final status" | grep -o SUCCEEDED`
        if [[ $status == SUCCEEDED ]]
        then
                applicationId=`tail -20 log/$2-$3.log | grep "state: FINISHED" | grep -E -o application_[0-9]{13}_[0-9]*`
                running_time=`getRunningTime $applicationId`
                echo `cat $2-$3.tmp`$running_time,$status >> realtime.csv
                rm $2-$3.tmp
        else
                # 将失败状态输出为注释行
                status=FAILED
                echo \#`cat $2-$3.tmp`0m,$status >> realtime.csv
                rm $2-$3.tmp
        fi

        # 日志输出
        echo $1表处理状态：$status
        echo $1表处理结束于 `date +"(%y-%m-%d) %H:%M:%S"`
        echo 
        if [[ $status == SUCCEEDED ]]
        then
                echo 执行时间：$running_time
        else
                echo 未成功执行 
        fi

        echo
        echo ----------------------------------------------

        if [[ $status == SUCCEEDED ]]
        then
                return 0
        else
                return 1
        fi
}


province=$1
date=$2
long_code=`python /home/cdn/workspace/zhangyongtao/Pre/script/code.py $province | cut -d ' ' -f 2`
short_code=`python /home/cdn/workspace/zhangyongtao/Pre/script/code.py $province | cut -d ' ' -f 3`
folders=("Pre" "A1_D" "A1_H" "A2_D" "A2H_B2")


# 日志输出
echo
echo "=================================================================================================="
echo "=============================`date`================================="
echo "=================================================================================================="
echo $*

# 清空hdfs输出目录
hdfs dfs -rm -r /coll_data/security_dns/$province$short_code/$date
all_status=""

for folder in ${folders[@]}
do
        BatchProcess $folder $province $date $long_code
        if [[ $? == 1 ]]
        then
                echo "中断后续执行"
                exit 1
        fi
done
```

## 第三部分工作
处理数据的上传，一开始选择用flume上传，后来由于吞吐量的问题，改为直接用Hadoop put上传。然后两个脚本负责监控flume上传状态和持续put文件。

- flume-check.sh

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


参考资料:
1. [linux time命令详解](http://blog.chinaunix.net/uid-26557245-id-3782974.html)
2. [expect基础语法](https://blog.csdn.net/k122769836/article/details/49051243)
3. [expect用法](https://www.cnblogs.com/tychyg/p/5086499.html)
4. [spark通过合理设置spark.default.parallelism参数提高执行效率](https://blog.csdn.net/bbaiggey/article/details/51984753)
5. [spark 资源参数调优](https://www.cnblogs.com/bonelee/p/6042267.html)
6. [Spark性能优化指南——基础篇](https://tech.meituan.com/spark-tuning-basic.html)
7. [Spark性能优化指南——高级篇](https://tech.meituan.com/spark-tuning-pro.html)
8. [关于sparksql on yarn生成大量.hive-staging文件问题](http://www.aboutyun.com/thread-20657-1-1.html)
9. [Linux日志文件总管——logrotate](https://linux.cn/article-4126-1.html)
10. [linux下logrotate 配置和理解](https://blog.csdn.net/cjwid/article/details/1690101)
11. [在线Crontab表达式执行时间验证](http://www.atool.org/crontab.php)
12. [shell 定时任务对java_home的影响](https://www.cnblogs.com/yht-817/p/7248584.html)
13. [Hive之分区（Partitions）和桶（Buckets）](http://www.aahyhaa.com/archives/316)
14. [hive深入浅出](https://blog.csdn.net/hguisu/article/details/18986759)
15. [Hive原理及查询优化](https://blog.csdn.net/LW_GHY/article/details/51469753)
16. [Scala入门到精通——第十四节 Case Class与模式匹配（一）](https://blog.csdn.net/lovehuangjiaju/article/details/47176829)




