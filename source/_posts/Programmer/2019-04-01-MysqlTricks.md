---
layout: post
date: 2019-04-01
title: 仓鼠一般搜集到的mysql技巧
category: 程序员的玩具
tags:
- mysql
- trick
---

1. 比`count(*)`粗略但是更快的查询行数。
select table_schema,table_name,table_type,table_rows from information_schema.tables where table_schema='rule_ceshi' and table_name='operation_log';

2. select @@identity;
