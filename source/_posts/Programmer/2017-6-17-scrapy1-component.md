---
layout: post
date: 2017-6-17
title: scrapy tutorial
category: 程序员的玩具
tags: tools
keywords: spider scrapy
description: 又是一段没有营养的description
---
# scrapy学习

## 架构

![architecture](http://scrapy-chs.readthedocs.io/zh_CN/1.0/_images/scrapy_architecture.png)

1. 引擎打开一个网站(open a domain)，找到处理该网站的Spider并向该spider请求第一个要爬取的URL(s)。
2. 引擎从Spider中获取到第一个要爬取的URL并在调度器(Scheduler)以Request调度。
3. 引擎向调度器请求下一个要爬取的URL。
4. 调度器返回下一个要爬取的URL给引擎，引擎将URL通过下载中间件(请求(request)方向)转发给下载器(Downloader)。
5. 一旦页面下载完毕，下载器生成一个该页面的Response，并将其通过下载中间件(返回(response)方向)发送给引擎。
6. 引擎从下载器中接收到Response并通过Spider中间件(输入方向)发送给Spider处理。
7. Spider处理Response并返回爬取到的Item及(跟进的)新的Request给引擎。
8. 引擎将(Spider返回的)爬取到的Item给Item Pipeline，将(Spider返回的)Request给调度器。
9. (从第二步)重复直到调度器中没有更多地request，引擎关闭该网站。

## Spider
整体架构中需要编写的最主体部分就是spider，首先就先对这一组件进行说明。
###流程
1. generating the initial Request
2. parse the response
3. using seletor
4. store item


### 属性
- name：spider的id，唯一
- allowed_domains：域名限制
- start_urls：初始url列表
- custom_settings：局部设置，优先级高于全局设置
- crawler：
- setting：
<!-- more -->
- logger：

### 方法
- from_crawler 
- start_requests
- make_requests_from_url
- parse
- log：新版本使用self.logger.info("info")
- closed

### 子类
- CrawlSpider：
- XMLFeedSpider
- CSVFeedSpider
- SitemapSpider






### 选择器Selector
#### 概念
构建于 lxml 库之上的选择器

#### 初始化
- Selector(text = String)
- Selector(response = HtmlResponse)，在写spider时，在回调函数中可以通过response.selector获取。但是我们平时调用是直接用`response.xpath`就可以，因为这个是对`response.selector.xpath`的简化写法。

####方法
- extract()：返回满足选择器的html内容的列表。
- xpath()：xpath选择器，我会用一篇文章另说这个。
- re()：使用者则表达式过滤。
- css()：css选择器。










## Item Pipeline
### Item
#### 自定义Item
我在我的一个demo中使用的Item是：
```python
class TaospiderItem(scrapy.Item):
    # define the fields for your item here like:
    user = scrapy.Field()
    quesion = scrapy.Field()
    submit_id = scrapy.Field()
    time = scrapy.Field()
    pass
```
#### Item操作
1. 通过Item.fields得到Item的schema
2. 通过`item = TaospiderItem()`构造一个空对象，或者在构造函数中输入class预定义的field对应的值，比如`item = TaospiderItem(user=‘tom’)`，如果有Item.fields中包含的属性会报错。
3. 像python字典一样读取或赋值，类似于：`item['user']`或者`item['time']=100`。也可以用get方法取值，这种方法的好处是可以在get方法的第二个可选参数中为读取失败的情况设置返回值。
4. 使用`item.keys()`获取所有键的列表，使用`item.items()`获取所有键值对元组列表。
5. 允许拷贝构造函数，即`item2 = TaospiderItem(item1)`或者通过通过`item2 = item1.copy()`。*（注：深拷贝）*
6. `dict(item)`强制类型转换为字典。反之亦可。



#### 使用Item Loader
我们可以在parse函数中对Item进行复制，比如在我的代码中：
```python
lines = response.xpath("//table[@id='alternate']/tbody/tr")
item=TaospiderItem()
for line in lines:
	item['user'] = line.xpath("td[@class='u-name']/a/text()").extract()
	item['submit_id'] =line.xpath("td[1]/text()").extract()
	item['question'] = line.xpath("td[3]/a/text()").extract()
	item['time'] = line.xpath("td[last()-2]/text()").extract()
	yield item

```
在scrapy中提供了更优雅的方式。可以这么理解，Items 提供了盛装抓取到的数据的**容器** , 而Item Loaders提供了构件**装载**该容器。
使用方法是：
```python
loader = ItemLoader(item=TaospiderItem(), response=response)
lines = len(response.xpath("//table[@id='alternate']/tbody/tr"))
for i in range(lines):
	j=str(i+1)
    loader.replace_xpath('user',"//table[@id='alternate']/tbody/tr["+j+"]/td[@class='u-name']/a/text()")
    loader.replace_xpath('submit_id',"//table[@id='alternate']/tbody/tr["+j+"]/td[1]/text()")
    loader.replace_xpath('question',"//table[@id='alternate']/tbody/tr["+j+"]/td[3]/a/text()")
    loader.replace_xpath('time',"//table[@id='alternate']/tbody/tr["+j+"]/td[last()-2]/text()")
    yield loader.load_item()
```

两者的效果是完全一致的。这里有些尴尬的是ItemLoader构造函数中的response参数接受的赋值要是一个具有text属性的对象，response是满足这个要求的，但是通过xpath得到的对象却由于这个原因不能赋值给response参数，导致只能用整个response来构造这个loader，这就导致后面的xpath路径比较冗余。
因此我感觉前者的代码更清晰一点，但是好在loader为我们提供了不少的API可供调用。如下：
- add_xpath(field,value):类似于上面的replace_xpath，但是这个函数会在item中拼接处一个列表。
- get_xpath(value):传递进去一个xpath表达式，相当于当做一个选择器用。
- load_item():返回loader中当前加载的item。
- 等等


### Pipeline作用
- 清理HTML数据
- 验证爬取的数据(检查item包含某些字段)
- 查重(并丢弃)
- 将爬取结果保存到数据库中

### 启用pipeline
在setting.py文件中添加以下代码，格式为‘文件名’：‘优先级’，优先级的数字越小，说明优先级越高，执行顺序越靠前。不同优先级的pipeline文件形成流水线一次处理item数据流。
```python
ITEM_PIPELINES = {
    'myproject.pipelines.PricePipeline': 300,
    'myproject.pipelines.JsonWriterPipeline': 800,
}
```
### 使用pipeline
在pipeline中通过`process_item(self, item, spider)`方法处理item。
每个item pipeline组件都需要调用该方法，这个方法必须返回一个具有数据的dict，或是 Item (或任何继承类)对象， 或是抛出 DropItem 异常，被丢弃的item将不会被之后的pipeline组件所处理。
因为在前面的parse函数中，直接将extract()之后的内容存放到item中，而extract()返回的是一个列表，这个列表在该例中只有一个元素，并且里面的内容是unicode编码，类似于这种格式：

```json
{"submit_id": ["2040240"], "question": ["A+B Problem"], "user": ["octobervj"], "time": [" 240"]},
```

因此我们在pipeline中处理，希望将列表去除并得到utf-8编码的数据。
```python
def process_item(self, item, spider):
    keys = item.keys()
    for key in keys:
        item[key] = item[key][0].encode('utf8').strip()
    return item
```

经过pipeline处理之后的数据：
```json
{"submit_id": "2040240", "question": "A+B Problem", "user": "octobervj", "time": "240"},
```

## Request 和 Response
### Request
用于发送HTTP请求。
### 参数
- url：必须参数，指定目的地址。
- callback：常用。指定处理该Request得到的Response的回调函数。
- meta：用于在两个连续的解析函数之间传递数据。数据类型是一个python字典。在Request中对meta参数赋值，在回调函数可以通过meta方法得到该数据。另外这个字典中有一些制定的特殊的key可以被scrapy识别并完成特定功能。


### 子类：FormRequest
可以用于登录！
#### 特殊参数
- formdata：表单数据

### Response
通常不会手动创建，而是通过Request得到。

#### 子类
- TextResponse
- HtmlResponse（继承于TextResponse）
- XmlResponse




## 其他零碎
### Feed Export
用于输出得到的数据的组件，这里的输出文件被称为“feed”，支持多种序列化格式(serialization format)及存储方式(storage backends)。feed文件使用Item exporters进行输出。
- XML
- JSON
- JSON line
- CSV
最简单的使用方式就是直接在使用命令行运行爬虫的个时候使用-o参数：

```bash
scrapy crawl spider -o item.json
```

### logging
#### 常用setting.py设置
- LOG\_LEVEL:显示日志的最低级别，低于这个级别的不予显示。*这个对重定向到文件中的日志不起作用。*log有五个级别,从高到低是：
	1. CRITICAL
	2. ERROR
	3. WARNING
	4. INFO
	5. DEBUG
- LOG\_FILE：如果设置了这个参数，log就不会标准输出中输出，而是重定向到文件中。
- LOG\_ENCODING：Log使用的编码。
- LOG\_STDOUT：默认为False，如果为 True ，进程所有的标准输出(及错误)将会被重定向到log中。例如， 执行 print 'hello' ，其将会在Scrapy log中显示。

#### 使用
在scrapy中直接使用`self.logger.info()`或者其他级别来调用。

### setting
这个文件中有很多选项可以设置，关于Log和Pipeline相关的在上面已经提到了。这里说一些我比较感兴趣的：

- DEFAULT\_REQUEST\_HEADERS：Scrapy HTTP Request使用的默认header。由DefaultHeadersMiddleware 产生。默认为:
```json
{
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}
```

- DEPTH\_LIMIT：默认为0。爬取网站最大允许的深度(depth)值。如果为0，则没有限制。

- DOWNLOAD\_DELAY：默认为0。下载器在下载同一个网站下一个页面前需要等待的时间，以ms为单位。该选项可以用来限制爬取速度， 减轻服务器压力。同时也支持小数。该设定影响(默认启用的) RANDOMIZE\_DOWNLOAD\_DELAY 设定。另外您可以通过spider的 download\_delay属性为每个spider设置该设定。


- RANDOMIZE\_DOWNLOAD\_DELAY：默认为True。如果启用，当从相同的网站获取数据时，Scrapy将会等待一个随机的值 (0.5到1.5之间的一个随机值×DOWNLOAD\_DELAY)。该随机值降低了crawler被检测到(接着被block)的机会。某些网站会分析请求， 查找请求之间时间的相似性。若 DOWNLOAD\_DELAY 为0(默认值)，该选项将不起作用。
- STATS\_CLASS:默认为'scrapy.statscollectors.MemoryStatsCollector'。收集数据的类。该类必须实现 **状态收集器(Stats Collector)** API.





* * *

参考Scrapy在线文档：<http://scrapy-chs.readthedocs.io/zh_CN/1.0/index.html>


