

* * *
- 日期：20180605
- 工作目标：对HTTP日志提取特征

拿到手里的bro HTTP日志字段含义。

字段含义：
（1-6）

| 时间戳 | uid | sip | sport | dip | dport |
|-----|-----|-----|-----|-----|-----|
| 1465601748.513841 | C6tQ1j2quWmpEvTque | 10.42.65.141 | 1695 | 61.132.54.2 | 80 |

（7-12）

| session_seq | method | domain | uri | referrer | useragent |
|-----|-----|-----|-----|-----|-----|
| 6 | GET | rand.com | /manageonline/images/login/login_btn.png | http://manage.com/manageonline/login.aspx | Mozilla/4.0  |

（13-27）

| 啥长度1 | 啥长度2 | RCODE | R | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 奇怪的id | 奇怪的类型 | 不知道啥id | MIME |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0 | 4035 | 200 | OK | - | - | - | (empty) | - | - | - | - | - | FBIJWU2KqyqlNqwqXi | image/png |


## all.log数据探索：

一共有380041条记录

### 离散特征值
ahent、method、端口、uri、domain、RCODE、奇怪的类型和MIME

### 连续特征是
两个不知道什么意义的长度、时间差

#### useragent
`cut -f 12 all.log | cut -d ' ' -f 1 | sort -u`查看不同的agent种类，发现种类不多，如下：
-、DavClnt、GreenBrowser、Microsoft、Microsoft-WebDAV-MiniRedir/6.1.7601、Mozilla/4.0、Mozilla/5.0、Youdao

可以考虑使用离散类型编码，节省空间还方便看。

### method
`cat all.log  | cut  -f 8 | uniq | sort -u`
GET、HEAD、OPTIONS、POST、PROPFIND


#### 没有信息的字段
其中，9(domain) 16(响应码描述) 17 18 19 20 21 22 23 字段在整个all.log中没有变化，只有一个值。使用该命令证实：`cat all.log | cut -f17,18,19,20,21,22,23 | uniq`

### 每个都不一样的字段
6(dest_port) 12(agent，费劲) 24 26（两个奇怪的id）

#### 奇怪的字段
有奇怪id和类型的文件大概长这样：
elasticsearch@zookeeper2:~/yjyj/zte$ grep F0wvWi3089VeFdScS3 all.log 
1465605459.204891 | CZHmulZmCGR6Zfgw5 | 10.42.115.102 | 1124 | 61.132.54.2 | 80 | 24 | POST | rand.com | /gzsystem/bonusmgnt/bonustake/service/bonustakeservice.asmx/getempconfig | http://manage.com/gzsystem/bonusmgnt/bonustake/apply/bonustake.aspx | Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C; .NET4.0E; TCO_20160607134202) | 82 | 428 | 200 | OK | - | - | - | (empty) | - | - | - | F0wvWi3089VeFdScS3 | text/plain | FzorrF3DmUIVO60fDl | text/json
elasticsearch@zookeeper2:~/yjyj/zte$ grep FADyvg1RmeJdUhiP33 all.log 
1465606248.608513 | CwfdQX2LyN9VzlKS8b | 10.42.89.37 | 53056 | 61.132.54.2 | 80 | 2 | POST | rand.com | /manageonline/cn_manageonline/gz/viewhistorygz.aspxhttp://manage.com/manageonline/cn_manageonline/gz/viewhistorygz.aspx | Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; TCO_20160611084049) | 884 | 10011 | 200 | OK | - | - | - | (empty) | - | - | - | FADyvg1RmeJdUhiP33 | text/plain | F7yCxgCJjRWJmqRR6 | text/html

对于奇怪的id字段，要么是空，要么独一无二，在all.log中有356715为空，占了93.86%，感觉没卵用。

对于奇怪的类型字段，使用命令`cat all.log | cut -f 25 | sort | uniq -c | less`，输出：
> 356726 -
>      1 text/json
>  23314 text/plain

#### 不知道啥id字段
对于“不知道啥id”字段，要么是空，要么就独一无二。在all.log中有49984条为空，占了13.15%，感觉没大用。

#### uid（会话）
`cat all.log | cut -f 2 | sort | uniq -c | less`
共有35951个会话

#### 源ip（用户）
`cat all.log | cut -f 3 | sort | uniq -c | wc`
共有1563个用户

* * *

- 日期：20180605
- 工作目标：对HTTP日志提取特征

```bash
# 预处理
# 记录下响应码对应的描述，万一有用呢
cut -f15,16 all.log | sort | uniq -c > RCODE
# 删除掉上面说的没用的字段
# 第12个特征agent也删掉了，所有的浏览器都说自己是mozilla，有的浏览器的agent后面放一对浏览器，流氓，删掉该特征
cut --complement -f6,9,12,16,17,18,19,20,21,22,23,24,26 all.log | tr -d '\r'> all1.log

sed_file=sed.scr
rm $sed_file


for f in 7 12 13
do
	i=0
	for field in `cut -f$f all1.log | uniq | sort -u`
	do
    	i=$((i+1))
		echo s/"\"\t$field\t\"/"\"\t$i\t\""/ >> $sed_file
	done
done
```
## 用户特征

### 单个record特征
- 距离上一条的时间
- uri的长度、分隔符数、特殊字符数；referrer在单个的record中不考虑特征，放到session中考虑；tfidf啊！uri的处理我觉得可以作为单独的特征向量一部分，host和post提取出频率，即被访问的这个host在整个内网中被访问多少次，

### 单个session特征
- session持续时间
- 

* * *

## 遇到的问题

### 1. 大量有限的类别比如特征端口、目的ip、目的端口怎么处理？

### 2. 无线的类别特征比如怎么处理，比如uri，referrer？



参考：
1. [hmmlearn 官方文档](http://hmmlearn.readthedocs.io/en/latest/tutorial.html#available-models)
2. [用hmmlearn学习隐马尔科夫模型HMM](https://www.cnblogs.com/pinard/p/7001397.html)
3. [bro文档](https://www.bro.org/sphinx-git/logs/index.html)
4. [bro监控HTTP流量](https://blog.csdn.net/mhpmii/article/details/52936378)
5. [特征哈希](http://breezedeus.github.io/2014/11/20/breezedeus-feature-hashing.html)
6. [Feature Hashing](https://en.wikipedia.org/wiki/Feature_hashing)
7. [Topic extraction with Non-negative Matrix Factorization and Latent Dirichlet Allocation](http://sklearn.apachecn.org/cn/0.19.0/auto_examples/applications/plot_topics_extraction_with_nmf_lda.html#sphx-glr-auto-examples-applications-plot-topics-extraction-with-nmf-lda-py)
8. [Javascript unescape() vs. Python urllib.unquote()](https://stackoverflow.com/questions/23158822/javascript-unescape-vs-python-urllib-unquote)
9. [](https://distill.pub/2016/misread-tsne/)
