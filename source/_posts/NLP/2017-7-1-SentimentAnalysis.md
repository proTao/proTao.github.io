---
layout: post
title: 基于词向量和LSTM的情感判别
category: 自然语言处理
tags: nlp
keywords: keras nlp lstm
description:
---


# 基于中文的评价情感分析

## 项目目标
我选择的题目是基于中文文本情感的文本自动分类系统。由于对张家俊老师讲的神经语言模型部分与词向量表示很感兴趣，所以希望通过词向量模型和神经语言模型结合实现一个有较高分类正确率的情感分析模型。


## 国内外相关工作

### 集成工具调研

情感分析实际上就是一个文本二分类的问题，目前也有不少集成的自然语言处理的非常好的一体化工具，比如Stanford CoreNLP和TextBlob，还有国人开发的针对中文文本的python库SnowNLP。
以SnowNLP为例，基于python的它使用起来十分方便：

```python
>>> from snownlp import SnowNLP

>>> s = SnowNLP(u'这个东西真心很赞')

>>> s.words
[u'这个', u'东西', u'真心', u'很', u'赞']

>>> s.tags
[(u'这个', u'r'), (u'东西', u'n'), (u'真心', u'd'), (u'很', u'd'), (u'赞', u'Vg')]

>>> s.sentiments
0.9769663402895832 # positive的概率
```

这个工具中通过sentiments返回的是一个0到1之间的正数来表示测试文本是正向情感的可能性的大小。实验中并没有没有进行深入了解，因此不进行这几个工具的详细介绍。

<!-- more -->
### 分词工具调研

*注：参考PaperWeekly的[中文分词工具测评](http://rsarxiv.github.io/2016/11/29/%E4%B8%AD%E6%96%87%E5%88%86%E8%AF%8D%E5%B7%A5%E5%85%B7%E6%B5%8B%E8%AF%84/)。*

参考文章《中文分词工具测评》中，对比了4个常见的分词工具，分别是：哈工大LTP、中科院计算所NLPIR、清华大学THULAC和jieba，为了对比分词速度，选择了这四个工具的c++版本进行评测。

这篇文章得出的结论是清华大学的THULAC工具的整体性能非常不错，但是由于我之前使用过的工具是结巴分词和CRF++，觉得结巴分词的接口十分容易使用，对于这个工具也比较熟悉，因此选择了结巴分词作为分词工具。

另外我又使用了CRF++这个条件随机场的工具进行了基于条件随机场的由字构词的的方法，使用的语料是人民日报分词标注语料。使用预定义特征函数模板：

```python
# Unigram
U00:%x[-2,0]
U01:%x[-1,0]
U02:%x[0,0]
U03:%x[1,0]
U04:%x[2,0]
U05:%x[-2,0]/%x[-1,0]/%x[0,0]
U06:%x[-1,0]/%x[0,0]/%x[1,0]
U07:%x[0,0]/%x[1,0]/%x[2,0]
U08:%x[-1,0]/%x[0,0]
U09:%x[0,0]/%x[1,0]
 
U10:%x[-2,1]
U11:%x[-1,1]
U12:%x[0,1]
U13:%x[1,1]
U14:%x[2,1]
 
U15:%x[-1,0]/%x[1,0]
U16:%x[-1,1]/%x[1,1]
 
U17:%x[-1,1]/%x[0,1]
U18:%x[0,1]/%x[1,1]
 
U19:%x[-2,1]/%x[-1,1]/%x[0,1]
U20:%x[-1,1]/%x[0,1]/%x[1,1]
U21:%x[0,1]/%x[1,1]/%x[2,1]
 
# Bigram
B
```

最后使用测试数据判断分词效果：

```bash
WordCount from test result: 102690
WordCount from golden data: 102952
WordCount of correct segs : 101950
P = 0.992794, R = 0.990267, F-score = 0.991529`
```

可以看出训练后得到的模型拥有很不错的分词效果。

### 词嵌入工具调研

目前比较常见的词嵌入工具有谷歌的word2vec，还有一个gensim集成工具包，另外在spark的mllib中也提供了word2vec功能。
我选择使用的是gensim工具包，这是一个非常强大的工具包，根据他的主页可以看到他可以实现LDA/LSI/TFIDF/各种词或文章的嵌入模型以及其他很多的使用模型及其分布式版本。对于该工具的具体使用在后面会详细说明。



## 核心思想与系统流程
考虑到词向量模型的强大的分布式表达能力，第一步是利用大量的文本语料训练出合适的词嵌入模型。第二步是对训练语料中的句子分词，然后使用词嵌入模型进行词语表示，将句子表示为关于词向量的变长向量。第三步就是使用神经语言模型进行训练，将前一步带便签的向量数据和标签进行输入，学习句子中的语义并期望训练出一个合适的二分类模型。最后一步就是进行数据测试，调参和模型调整。

整体架构如下图所示：

![architecture](/img/sentimentanalyse1.png)


### 数据来源
对于词向量的训练数据主要来自于三个部分。

第一部分来自于搜狗发放的新闻数据，解压后的文本文档大小为50兆左右，共9个文件夹，总共不到两万个文件。可以在[搜狗实验室](http://www.sogou.com/labs/resource/list_pingce.php)下载得到。

第二部分来自于一些网络小说。选择网络小说的目的，一是网络小说的用词造句更为与时俱进，不像新闻用户那么标准统一，更贴合生活；相比微博等UGC又没有表情或者链接等噪声数据。二是获取途径方便，数据量大，格式统一。在这里我选择的小说是：《另一个宇宙来的人》和《盗梦宗师》两本。

第三部分来自于网络上携程当当等网络的带标记用户评价数据。使用这部分数据的目的是希望有针对性的使训练出的模型更适用于评价语料的判断。


### 数据预处理
在使用中发现新闻数据中有很多在句子中影响语义的内容。比如：
> - 董事会中独立董事（执行董事）必须占多数
> - 5年(含)以下贷款由现行年利率3.96％调整为4.14％
> - 【本报讯】深圳银行业请来高参智囊，为其日益发展的信贷行业出谋划策。
> - 通过收购母公司的东风煤矿（120万吨）和兴建玉溪煤矿（300万吨）
> - 更多详情免费咨询021*64690729或登录WWW.KL178.COM（证券通），资深行业研究员为您提供客观、深度、超前的投资信息。
> - &nbsp&nbsp&nbsp&nbsp会议由董事长王建乔主持

有很多由于来自于互联网html网页中的特殊符号或者来自于书面语但是不会再用户评价中出现的语言使用方法，因此需要进行预处理。经过实验证明合适的预处理使得分类正确率大幅提升。

```python
# 将被删除的正则模式
self.remove_pattern=[]
self.remove_pattern.append(re.compile(u"www\..*\.com"))
self.remove_pattern.append(re.compile(u"\(.{0,10}\)"))
self.remove_pattern.append(re.compile(u"\[.{0,10}\]"))
self.remove_pattern.append(re.compile(u"（.{0,10}）"))
self.remove_pattern.append(re.compile(u"「.{0,10}」"))
self.remove_pattern.append(re.compile(u"&nbsp;"))
self.remove_pattern.append(re.compile(u"[●　 -“”]"))

# 将被用来分割句子的正则模式
self.split_pattern = []
self.split_pattern.append(re.compile(u"[?!。？！…「」\(\)（）:：]"))
self.split_pattern.append(re.compile(u"\.　"))
self.split_pattern.append(re.compile(u"． "))
self.split_pattern.append(re.compile(u"\.\.\."))

# 剔除指定的正则模式
for pattern in self.remove_pattern:
    lines = map(lambda line: pattern.sub("", line), lines)

# 替换指定的正则模式为换行符
for pattern in self.split_pattern:
    lines = map(lambda line: pattern.sub("\n", line), lines)

# 用splitlines()切分句子
lines = map(lambda line: line.splitlines(),lines)
flatten = lambda x: [y for l in x for y in flatten(l)] if type(x) is list else [x]
lines = flatten(lines)

# 剔除空行
lines = filter(lambda line:len(line.strip())>0, lines)
```


### 模型生成与测试
网络结构使用这种方式定义：

```python
# 定义贯序模型
network = Sequential()  # or Graph or whatever

# 使用训练好的词嵌入模型进行分布式表示
network.add(Embedding(output_dim=wv_dim,
                    input_dim=vocab_scale,
                    mask_zero=True,
                    weights=[embedding_weights],
                    input_length=max_len))
# 添加LSTM层
network.add(LSTM(output_dim=50, activation='sigmoid', inner_activation='hard_sigmoid'))

# 在与全连接层连接之前，使用0.5的概率进行dropout
network.add(Dropout(0.5))

# 单层感知机
network.add(Dense(1))

# 使用ReLU作为激活函数
network.add(Activation('relu'))

# 交叉熵作为损失函数
model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
# 进行训练
model.fit(x_train, y_train, batch_size=batch_size, nb_epoch=n_epoch,validation_data=(x_test, y_test))

```

最后在测试集上可以达到97.89的正确率。

### 测试用例展示


``` python
In [73]: predict_one(u"距离川沙公路较近,但是公交指示不对,如果是\"蔡陆线\"的话,会非常麻烦.建议用别的路线.房间较为简单.")
Out[73]: 1

In [74]: predict_one(u"房间内环境还是不错的,就是上网有点贵,12块一个小时,还有门口修路,门前环境不好")
Out[74]: 1

In [75]: predict_one(u"早餐太差，全是素菜。另外礼宾部还弄丢了我一件行李，最后发现是被别人领走了，半天才找回来。其他都还可以。")
Out[75]: 0

In [76]: predict_one(u"1。送货慢，19号订单，20号打款，28号到货2。联保单不填写，不盖章，送来的联保单没什么用，3。没什么中文说明书，有两张纸，什么文字都有，就是没发现微星的任何标识，4。没有一部可以直接打得通的电话，有一部声讯电话，打10次。10次不通。浪费消费者的钱5。电池不是原装，我怀疑是水货")
Out[76]: 0

In [77]: predict_one(u"呵呵，卖家死全家，谁买谁傻逼")
Out[77]: 0

In [78]: predict_one(u"位置好找，房间干净面积大，隔音好")
Out[78]: 1

In [79]: predict_one(u"小巧轻便，竟然比我的X61还轻，做工一贯的好。屏幕比X61亮，分辨率也高。")
Out[79]: 1

In [80]: predict_one(u"外观，键盘，性能和电池都挺不错，但就是进不了系统，郁闷啊。硬盘嘎吱响，怀疑有问题。虽然楼上有人讲F9导入系统可以解决问题，但验货的时候可不知道，京东的售后也没提这个方法，直接换货了，还是换个新的保险")
Out[80]: 1

In [81]: predict_one(u"特别喜欢")
Out[81]: 1

In [82]: predict_one(u"不会再买他们家的东西了")
Out[82]: 0

In [83]: predict_one(u"位置虽然比较好找，但是房间隔音一般，特别的吵。。。而且说好的红包返现，竟然要五天之后才能收到，各位可要擦亮眼睛啊！")
Out[83]: 0
```

## 结果分析
可以直接执行train_network.py中的全部代码，我已经将里面训练模型的部分代码注释掉并且更改为加载训练好的模型，然后会输出此次在划分测试集的正确率。

较高正确率的主要原因在于事先的比较充分的预处理工作，较好的词嵌入模型和LSTM强大的序列学习能力。
我认为还可以改进的地方在于使用更好的分词工具，由于我没有使用更高级的深度学习的模型，也没有进行细致的超参数调参，所以在这两方面上可以期望达到模型的优化。

完成了此次作业的主要目的：
- 在实践中了解词嵌入技术与神经语言模型，并且达到了较为不错的正确率


## 参考资料：
1. [word2vec中的数学原理详解系列](http://blog.csdn.net/itplus/article/details/37969519)

2. [科学空间](http://kexue.fm)

3. [Shopping Reviews Sentiment analysis](https://buptldy.github.io/2016/07/20/2016-07-20-sentiment%20analysis/)

4. [ Keras + LSTM + 词向量 情感分类/情感分析实验 ](http://blog.csdn.net/churximi/article/details/61210129)

5. [gensim主页](http://radimrehurek.com/gensim/corpora/dictionary.html)

6. [keras文档](http://keras-cn.readthedocs.io/en/latest/)