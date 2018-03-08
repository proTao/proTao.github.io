---
layout: post
title: 边学边用shell军刀
category: 程序员的玩具
tags: tools
keywords: shell
description:
---

记录下自己的shell使用记录。

## 任务一：
**输出绝对路径**

详见[输出绝对路径](https://protao.github.io/20/output-path.html)一文。


## 任务二：
**把所有错误格式的jpg文件的后缀改为png**

```bash
for f in ./download/*
do
    head=`od -N2 -t x1 $f | head -1 | sed -e 's/0000000//g' -e  |tr -d '\n'`
    if test $head = 8950
    then
        mv ${f%%.jpg}.jpg ${f%%.jpg}.png
    fi
done
```
**解释**：`od`用于输出文件的八进制、十六进制或其它格式编码的字节，通常用于显示或查看文件中不能直接显示在终端的字符。`-N2`表示输出两个字符，`-t x1`是指用十六进制输出。`head`易于理解。`sed`是字符串处理命令，`-e`指有多个命令，s是替换指令。`tr`又是一种字符串处理命令，`-d`表示需要删除。




**知识点1**:测试命令test，可以用在if语句中测试字符串或数字或文件是否满足一些简单的条件。详见[RUNOOB](http://www.runoob.com/linux/linux-shell-test.html)


**知识点2**：字符串操作

![](/img/shellstr1.png)
![](/img/shellstr2.png)


## 任务3：
**将文件依次**
```bash
i=0
for f in ./*.gz
do
	gzip -d $f
	hadoop fs -put ${f:2:21} /user/zhangyongtao/ChinaMobile/beijing/20170726/
	gzip ${f:2:21}
	echo $i
	((i+=1)) 
	echo ${f:2:21}
done
```


## 任务4
**依次执行文件夹下以时间戳命名的大量定长文件**

```bash
#for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
#do
#	echo "----------  BEGIN PROCESS ON DAY $i  -------------"
#	#hadoop jar FindFrequentDomain.jar FindFrequentDomain /user/mawei/RandomDomFieldDDoS/Data/DNS_2016.12.$i/dns-??-all /user/zhangyongtao/output/fredomain$i 12000 0.85 500
#	#hadoop fs -get /user/zhangyongtao/output/fredomain$i/part-r-00000 ./output/fredomain$i
#	cat ./output/fredomain$i
#done

for i in $(seq 0 2302)
do 
# make sub file name 
    if test $i -lt 10
    then
        subname=000${i}
    elif test $i -lt 100
    then
        subname=00${i}
    elif test $i -lt 1000
    then
        subname=0${i}
    else
        subname=${i}
    fi
    echo ${subname}
# execute hadoop jar command （hadoop后面的参数不用管，是上传的jar包需要解析的参数）
    hadoop jar FindFrequentDomain.jar FindFrequentDomain /user/zhangyongtao/ChinaMobile/guangdong/20170607/200_1_20170607${subname}?? /user/zhangyongtao/output/chinamobile/ddos/guangdong0607${subname} 20000 0.8 1000 0 1 \\\| no
    echo ${subname}
done
```

### 参考
1. [shell字符串详解](http://www.cnblogs.com/chengmo/archive/20/1841355.html)
2. [RUNOOB](http://www.runoob.com/linux/linux-shell-test.html)
3. [Linux命令大全](http://man.linuxde.ne)