

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
| 6 | GET | rand.com | /manageonline/login.png | http://manage.com/login.aspx | Mozilla/4.0  |

（13-27）

| 啥长度1 | 啥长度2 | RCODE | R | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0 | 4035 | 200 | OK | - | - | - | (empty) | - | - | - |

| 奇怪的id | 奇怪的类型 | 不知道啥id | MIME |
|-----|-----|-----|-----|
| - | - | FBIJWU2KqyqlNqwqXi | image/png |


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

### uri特征
- uri_chrlen
- uri_len
- query_chrlen
- query_count
- longest_query
- query_parts
- tfidf



### 处理 user 特征
输入： 
- session个数 (1)

- 每个 session 长度构成的1维序列的统计特征（平均值、方差、max、min）
- 每个 action 长度1 构成的1维序列的统计特征（平均值、方差、max、min）
- 每个 action 长度2 构成的1维序列的统计特征（平均值、方差、max、min）
- 每个 action 中的 uri 字符长度构成的1维序列的统计特征（平均值、方差、max、min）
- 每个 action 中的非空 query 部分的字符长度构成的1维序列的统计特征（平均值、方差、max、min）
- 相邻两个 action 的时间差构成的1维序列的统计特征（平均值、方差、中位数、max、min）

- session开始时间提取得到月份，周几，时辰，作为类别特征，处理为直方图，直方图size分别是12，7,12
- action特征中的类别特征，目前是type\_、MIME、rcode、method这四个。
- uri特征中的类别特征，目前是

* * *



## 遇到的问题

### 1. 大量有限的类别比如特征端口、目的ip、目的端口怎么处理？

### 2. 无线的类别特征比如怎么处理，比如uri，referrer？





















* * *

## 服务器环境配置
```bash
# 基础环境是 ubuntu
workspace=zte

# python3.6 安装
wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tar.xz
sudo apt-get update
sudo apt-get install zlib1g zlib1g-dev
sudo apt-get install libbz2-dev
# sudo apt-get install tcl-dev tk-dev python3-tk bzip2 # 后续的matplotlib包需要
tar -xvf Python-3.6.2.tar.xz
cd Python-3.6.2
./configure
make
sudo make install

# python3 虚拟环境和包管理
## 好像上面的python包中有pip和setuptools
# curl "https://bootstrap.pypa.io/3.2/get-pip.py" -o "get-pip.py"
# sudo python3 get-pip.py
sudo pip3 install --upgrade pip
pip install --user pipenv
# pip3 list # 如果是新安装的环境，此时只有pip和setuptools
sudo ln -s /usr/local/bin/python3.6 /usr/bin/python3
cd $workspace
pipenv install numpy
pipenv install scikit-learn
pipenv install pandas
pipenv install matplotlib
pipenv install ipython --dev

# 进入虚拟环境
pipenv shell

# 配置虚拟工作环境，安装依赖包




```

* * *

# 工程技巧
给特征命名可以很好地在模块之间提高可扩展性。前面加了新的特征，后面的模块可以不改动，也可以添加少许代码利用起新的特征。


参考：
1. [hmmlearn 官方文档](http://hmmlearn.readthedocs.io/en/latest/tutorial.html#available-models)
2. [用hmmlearn学习隐马尔科夫模型HMM](https://www.cnblogs.com/pinard/p/7001397.html)
3. [bro文档](https://www.bro.org/sphinx-git/logs/index.html)
4. [bro监控HTTP流量](https://blog.csdn.net/mhpmii/article/details/52936378)
5. [特征哈希](http://breezedeus.github.io/2014/11/20/breezedeus-feature-hashing.html)
6. [Feature Hashing](https://en.wikipedia.org/wiki/Feature_hashing)
7. [Topic extraction with Non-negative Matrix Factorization and Latent Dirichlet Allocation](http://sklearn.apachecn.org/cn/0.19.0/auto_examples/applications/plot_topics_extraction_with_nmf_lda.html#sphx-glr-auto-examples-applications-plot-topics-extraction-with-nmf-lda-py)
8. [Javascript unescape() vs. Python urllib.unquote()](https://stackoverflow.com/questions/23158822/javascript-unescape-vs-python-urllib-unquote)
9. [How to Use t-SNE Effectively](https://distill.pub/2016/misread-tsne/)
10. [Hopkins test for cluster tendency](https://matevzkunaver.wordpress.com/2017/06/20/hopkins-test-for-cluster-tendency/)
11. [机器学习——聚类质量评估方法（有效性指标）](http://blog.sina.com.cn/s/blog_135031dae0102xgov.html)
12. [Pandas分类数据](https://www.yiibai.com/pandas/python_pandas_categorical_data.html)
13. [通俗理解LDA主题模型](http://www.360doc.com/content/16/0428/10/478627_554452907.shtml)
14. [用pandas处理大数据———减少90%内存消耗](https://blog.csdn.net/wally21st/article/details/77688755)
15. [CategoricalDtype Doc](http://pandas.pydata.org/pandas-docs/stable/categorical.html#categoricaldtype)
16. [numpy,pandas,scipy求众数速度比较](http://blog.sina.com.cn/s/blog_12c3192a50102xdhd.html)
17. [使用sklearn做单机特征工程](http://www.cnblogs.com/jasonfreak/p/5448385.html)
18. [Python包和版本管理的最好工具----pipenv](http://www.mamicode.com/info-detail-2214218.html)
