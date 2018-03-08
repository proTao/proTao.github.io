---
layout: post
title: 字符集与字符编码问题
category: python
tags:
- python
- programmer
keywords: 编码
description:
---
## 字符集

### ascii
基本学计算机的童鞋接触到字符串的时候都会学ascii编码，在这里不用特意去分字符集和编码的问题，因为此时ascii是字符集同时也规定了编码。
ascii实际上就是用一个字节8位去表示控制码，大小写英文字母以及阿拉伯数字，当时电脑还没有普及开，所以这种简单的甚至是简陋的方法得以正常使用，ascii的名字也可以看出当时的人的看法：American Standard Code for Information Interchange（美国信息互换标准代码）。
此时的ascii码只用到了低128位，最高位默认位0。然而低128位只用来编码英文字符没有问题，但是当电脑发展到其他一些欧洲国家或者采用拉丁字母的国家中，这些国家自己用的字母在ascii中是不存在的。于是各个国家开始自己给自己编码，为了保持对ascii的兼容，就在ascii的128到255编码范围内做文章。补充进来的被称为“扩展字符集”。
但是由于各个国家都编写自己的编码规则，导致不同国家的编码是不通用的，此时就已经开始出现一些编码导致的通信问题。但是当计算机传入中国的时候大问题才来了。

### gb×系列
ascii是单字节编码，就算加上扩展字符集也只能编码256个字符，然而中国文化博大精深，即使是只考虑常用汉字也有六千多个。于是在ascii这种单字节编码上做文章是不大可能了，因为采用双字节编码，就是**gb2312**编码。
>  规定：一个小于127的字符的意义与原来相同，但两个大于127的字符连在一起时，就表示一个汉字，前面的一个字节（他称之为高字节）从0xA1用到 0xF7，后面一个字节（低字节）从0xA1到0xFE，这样我们就可以组合出大约7000多个简体汉字了。在这些编码里，我们还把数学符号、罗马希腊的字母、日文的假名们都编进去了，连在 ASCII 里本来就有的数字、标点、字母都统统重新编了两个字节长的编码，这就是常说的"全角"字符，而原来在127号以下的那些就叫"半角"字符了。

双字节理论上可以编码65536种字符，但是由于为了解决当时燃眉之急，只收录了六千余个汉字，并且为了保持与ascii的兼容，就规定对于汉字的编码只使用一个字节的128到255的范围，低于128的范围保留用于与ascii兼容。然后台湾等地区由于常用繁体字，所以他们也有一套自己的编码规则Big5，即大五码，收录了一万三千多个汉子。
后来用着用着，发现在某些人名地名古汉字上，gb2312总是有不支持的地方，开始的时候用一些造字软件凑合，后来这种问题越来越多，于是大家就像干脆再出一套新的编码，这就是GBK。
**GBK**兼容gb2312，采用单双字节变长编码，英文使用单字节编码，完全兼容ASCII字符编码，中文部分采用双字节编码。GBK和gb2312都是采用双字节字符集（DBCS），扩展出来的原理是解除了gb2312对于低位字节的限制，GBK中只要求第一个字节是大于127就固定表示这是一个汉字的开始，不管后面跟的是不是扩展字符集里的内容。
然后后来又有更大的扩展即**gb18030**，这个字符集基本涵盖了所有汉字，少数民族文字，采用四字节变长编码方式。这里就不细说了。
### ANSI
ANSI不是特指某种编码，前面的GB系列中文编码实际上都是属于ANSI，但是ANSI也不止这些。
不同的国家和地区制定了不同的标准，由此产生了 GB2312、GBK、GB18030、Big5、JIS 等各自的编码标准。这些使用多个字节来代表一个字符的各种汉字延伸编码方式，称为 ANSI 编码。在简体中文Windows操作系统中，ANSI 编码代表 GBK 编码；在繁体中文Windows操作系统中，ANSI编码代表Big5；在日文Windows操作系统中，ANSI 编码代表 JIS 编码。
不同 ANSI 编码之间互不兼容，当信息在国际间交流时，无法将属于两种语言的文字，存储在同一段 ANSI 编码的文本中。
ANSI编码表示英文字符时用一个字节，表示中文用两个或四个字节。

### UCS（unicode）
但是各个国家民族都在自己的语言上开发编码，那么在计算机的领域内，交流的鸿沟就会越来越大，最好的方式就是一共有足够公信力的机构组织以全球的语言体系为基础开发一套字符集与对应的编码方案。
果不其然，这档子事是由ISO（国际标准化组织）来做的，他们重新做了一套"Universal Multiple-Octet Coded Character Set"，简称 UCS, 是一种定长编码方式，俗称 "UNICODE",通过ISO10646标准发布。
UCS分为UCS-2和UCS-4，分别指使用两字节和四字节的编码方案。目前所有的编码都可以用UCS2涵盖，UCS如果前两字节是0x00，那么就成为UCS4的BMP（Basic Multilingual Plane）。将UCS-4的BMP去掉前面的两个零字节就得到了UCS-2。在UCS-2的两个字节前加上两个零字节，就得到了UCS-4的BMP。而目前的UCS-4规范中还没有任何字符被分配在BMP之外。

## 字符编码
### UTF
前面已经说了，字符集和字符编码是不同的东西，但是前面的ANSI系列的字符集和编码集合在使用方式上有着局部性，所以基本编码方式是唯一的。
UCS是一套比较完备的编码，规定了每个字符与一个特定字节的联系，但是这样会有一些问题。一是unicode字符串的长度和ANSI的长度的定义方式不同了。二是会有一定程度上空间的浪费。三是unicode字符串中会有零字节，但是在C中，\0表示字符串的结尾。
为了（在一定程度上）解决这些问题，是UCS能够有效地被使用起来，UTF（UCS Transformation Format）便应运而生。UTF是UNICODE的编码方案，也就是具体的实现，有很多版本。最常见的就是UTF-8，除了这个还有UTF-16，UTF-7等等。

> UTF-8的编码规则很简单，只有二条：
> 1）对于单字节的符号，字节的第一位设为0，后面7位为这个符号的unicode码。因此对于英语字母，UTF-8编码和ASCII码是相同的。
> 2）对于n字节的符号（n>1），第一个字节的前n位都设为1，第n+1位设为0，后面字节的前两位一律设为10。剩下的没有提及的二进制位，全部为这个符号的unicode码。
> 下表总结了编码规则，字母x表示可用编码的位。跟据下表，解读UTF-8编码非常简单。如果一个字节的第一位是0，则这个字节单独就是一个字符；如果第一位是1，则连续有多少个1，就表示当前字符占用多少个字节。
> 
|**Unicode符号范围** | **UTF-8编码方式**|	
|----|----:|  	
|0000 0000-0000 007F | 0xxxxxxx|  	
|0000 0080-0000 07FF | 110xxxxx 10xxxxxx|  	
|0000 0800-0000 FFFF | 1110xxxx 10xxxxxx 10xxxxxx|  
|0001 0000-0010 FFFF | 11110xxx 10xxxxxx 10xxxxxx 10xxxxxx|  

### 字节序与BOM
字节序实际上就是传输过程中高低位的顺序问题，常被称为大端小端顺序，也会被称为网络序和主机序。另外字节序位本机的存储中还会导致一些类型转换之类的细节问题，这里不细谈。
而unicode在存储的时候就会遇到这个问题。比如，“奎”的Unicode编码是594E，“乙”的Unicode编码是4E59。如果我们处理字符“594E”，那么这是“奎”还是“乙”？
为了解决这个问题，并且可以识别 Unicode 文件，Microsoft 建议所有的 Unicode 文件应该以 ZERO WIDTH NOBREAK SPACE（U+FEFF）字符开头。这作为一个“特征符”或“字节顺序标记（byte-order mark，BOM）”来识别文件中使用的编码和字节顺序。
在传输中，UCS规范建议我们在传输字节流前，先传输字符"ZERO WIDTH NO-BREAK SPACE"。
这样如果接收者收到FEFF，就表明这个字节流是Big-Endian的；如果收到FFFE，就表明这个字节流是Little-Endian的。

```python
In [38]: s="编码"

In [39]: s # 默认用utf-8
Out[39]: '\xe7\xbc\x96\xe7\xa0\x81'

In [40]: unicode(l.decode("utf8")) # 解码后用unicode编码（UCS2）
Out[40]: u'\u7f16\u7801'

In [41]: s.decode("utf8") # 从这个看出解码后默认用ucs字符集
Out[41]: u'\u7f16\u7801'

In [42]: s.decode("utf8").encode("gbk") # 用gbk编码
Out[42]: '\xb1\xe0\xc2\xeb'

In [43]: len(s) #看出各个编码的长度定义是不同的，utf8是统计字节数
Out[43]: 6

In [44]: len(s.decode("utf8")) # unicode(UCS2)每两字节算一个长度
Out[44]: 2

In [46]: len(s.decode("utf8").encode("gbk")) # gbk也是统计字节数，但是由于定长编码，一个字固定两字节。
Out[46]: 4

In [47]: us=u"编码"

In [48]: us
Out[48]: u'\u7f16\u7801'
```

### 解析编码
- XML解析读取XML文档时，W3C定义了3条规则：
	1. 如果文档中有BOM，就定义了文件编码
	2. 如果文档中没有BOM，就查看XML声明中的编码属性
	3. 如果上述两者都没有，就假定XML文档采用UTF-8编码

- 对于Unicode文本最标准的途径是检测文本最开头的几个字节。如：
 1. 开头字节时 EF BB BF--------------UTF-8
 2. 开头字节时 FE FF------------------UTF-16/UCS-2, little endian(UTF-16LE)
 3. 开头字节时 FF FE------------------UTF-16/UCS-2, big endian(UTF-16BE)
 4. 开头字节时 FF FE 00 00-----------UTF-32/UCS-4, little endian.
 5. 开头字节时 00 00 FE FF-----------UTF-32/UCS-4, big-endia


## 其他编码
### BASE64
是一种以可见ascii符号作为编码单元编码二进制的方式。
base64可以编码小幅图片或者音频等二进制文件,并且可以被文本编辑器打开。例如下图就是用base64编码的图片，可以在网页源代码中查看其编码内容。

![](data:image/jpeg;base64,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)

除了base64之外还有base24/base32等等原理大同小异。

### base58
Base58是用于Bitcoin中使用的一种独特的编码方式，主要用于产生Bitcoin的钱包地址。相比Base64，Base58不使用数字"0"，字母大写"O"，字母大写"I"，和字母小写"l"，以及"+"和"/"符号。
这个编码应用于bitcoin中，用来可视化一些密钥和哈希值，为了更好的可视化，去掉了一些容易混淆的字符，毕竟和钱有关，防止粗心大意看错编码，也防止有些别有用心的人在这上面做文章。
- - -

参考内容：

1. [各种字符编码方式详解及由来](http://gjican.iteye.com/blog/1028003)
2. 阮一峰 [字符编码笔记：ASCII，Unicode和UTF-8](http://www.ruanyifeng.com/blog/2007/10/ascii_unicode_and_utf-8.html)
3. ANSI百度百科词条
4. [程序员趣味读物：谈谈Unicode编码](http://pcedu.pconline.com.cn/empolder/gj/other/0505/616631.html)
