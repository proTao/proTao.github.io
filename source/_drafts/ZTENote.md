

* * *
- 日期：20180605
- 工作目标：对HTTP日志提取特征

拿到手里的bro HTTP日志字段含义。

字段含义：
（1-6）
| 时间戳 | uid | sip | sport | dip | dport | 
| 1465601748.513841 | C6tQ1j2quWmpEvTque | 10.42.65.141 | 1695 | 61.132.54.2 | 80 |

（7-12）
| session_seq | method | domain | uri | referrer | useragent | 
| 6 | GET | rand.com | /manageonline/images/login/login_btn.png | http://manage.com/manageonline/login.aspx | Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; InfoPath.2; TCO_20160611073226) |

（13-27）
| 啥长度 | 啥长度 | RCODE | R | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 奇怪的id | 奇怪的类型 | 不知道啥id | MIME |
| 0 | 4035 | 200 | OK | - | - | - | (empty) | - | - | - | - | - | FBIJWU2KqyqlNqwqXi | image/png |


## all.log数据探索：

一共有380041条记录

### useragent
`cut -f 12 all.log | cut -d ' ' -f 1 | sort -u`查看不同的agent种类，发现种类不多，如下：
- -
- DavClnt
- GreenBrowser
- Microsoft
- Microsoft-WebDAV-MiniRedir/6.1.7601
- Mozilla/4.0
- Mozilla/5.0
- Youdao

可以考虑使用离散类型编码，节省空间还方便看。

### 没用的字段

其中，17 18 19 20 21 22 23 字段在整个all.log中没有变化，只有一个值。

### 奇怪的字段
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

### 不知道啥id字段
对于“不知道啥id”字段，要么是空，要么就独一无二。在all.log中有49984条为空，占了13.15%，感觉没大用。

### uid（会话）
`cat all.log | cut -f 2 | sort | uniq -c | less`
共有35951个会话

### 源ip（用户）
`cat all.log | cut -f 3 | sort | uniq -c | wc`
共有1563个用户

参考：
1. [hmmlearn 官方文档](http://hmmlearn.readthedocs.io/en/latest/tutorial.html#available-models)
2. [用hmmlearn学习隐马尔科夫模型HMM](https://www.cnblogs.com/pinard/p/7001397.html)
3. [bro文档](https://www.bro.org/sphinx-git/logs/index.html)
4. [bro监控HTTP流量](https://blog.csdn.net/mhpmii/article/details/52936378)

