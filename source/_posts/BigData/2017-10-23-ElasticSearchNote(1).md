---
layout: post
date: 2017-10-23
title: ElasticSearch笔记（一）
category: 大数据
tags: 
- bigdata 
- elasticsearch
- database
keywords:
description:
---

```json
// 新建数据Demo
{"name":"Zhang Yongtao", "hobby":["sports","music"], "sex":"M", "age":23, "career":{"junior":"twenty","senior":"nankai","undergraduate":"nankai"}}


// 获取文档主体部分
GET /_index/_type/_id/_source

// 获取文档制定字段
GET /_index/_type/_id?_source=[SomeField]

// 更新整个文档
PUT /_index/_type/_id
{}

// 更新指定版本的文档
PUT /_index/_type/_id?version=[SomeVersionNum]

// 创建默认id文档
POST /_index/_type 
{}

// 创建自定义id文档
PUT /_index/_type/_id/_create
{}

// 局部更新文档
POST /_index/_type/_id/_update
<!-- more -->
{"doc":{[Some Key:Value]}} 或者 {"script":[SomeGroovyScript]}

// 检索任意多个文档
GET /_mget
{"docs":[{"_index":?, "_type":?, "_id":?, ("_source":?)},{}]}

// 检索某个表中多个文档
GET /_index/_type/_mget
{"ids":[]}


// 字符串搜索（url可以灵活多变）
GET /_index/_type/_search?q=[SomeConditions]
// 或者
GET /_search?q=[SomeConditions]

// 使用分词器进行分词
GET /_analyze?analyzer=standard
[SomeString]

```
