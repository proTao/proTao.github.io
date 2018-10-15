---
layout: post
date: 2017-10-19
title: Hadoop笔记（二）
category: 大数据
tags: 
- bigdata 
- hadoop
keywords:
description:
---
## 前言
研一结束前通过雁栖湖校区大数据的相关课程真真正正的使用了hadoop等工具，研二到了实验室就开始使用七这些工具进行真实场景下的一些简单的大数据分析。在这里进行简单的总结，记录一下之前使用过程中没有用到的一些hadoop功能与工作中的一些小trick。

## 全局参数配置
由于实验需要，在使用中通常需要抽象出一些外部参数在运行时通过命令赋值。而当参数变多的时候，直接靠`args`从命令行读入参数开始变得臃肿而不便于维护和使用。比如在我的例子中一共有十多个可调参数，如果每次命令都要赋值显然十分不方便。

好在已经有可以直接使用的参数解析工具包** args4j **可以直接使用。
```java
import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.CmdLineParser;
import org.kohsuke.args4j.Option;
/**
 * Created by protao on 17-10-17.
 */
public class TestJava {

    public static class SampleCmdOption {

        @Option(name="-h", usage="show help doc")
        public boolean help = false;

        @Option(name="-n", usage="how many time you want print")
        public int n = 1;

        @Option(name="-s", usage="the string you want to print")
        public String s = "hello world";

    }

    public static void showHelp(CmdLineParser parser){
<!-- more -->
        System.out.println("LDA [options ...] [arguments...]");
        parser.printUsage(System.out);
    }

    public static void main(String[] args) {
        //开始解析命令参数
        SampleCmdOption option  = new SampleCmdOption();
        CmdLineParser parser = new CmdLineParser(option);

        try {
	    parser.parseArgument(args);

            if (option.help){
                showHelp(parser);
                return;
            }
            for(int i = 0; i < option.n; i++) {
		System.out.println(option.s);
	    }
	

        }catch (CmdLineException cle){
            System.out.println("Command line error: " + cle.getMessage());
            showHelp(parser);
            return;
        }catch (Exception e){
            System.out.println("Error in main: " + e.getMessage());
            e.printStackTrace();
            return;
        }
	System.out.println("main program");
    }
}
```
其中Option Annotation中name是在命令行中参数的赋值入口，usage是对该参数的描述，如上述代码，在命令行中运行`java TestJava -h`会显示：
```bash
LDA [options ...] [arguments...]
 -h     : show help doc (default: true)
 -n N   : how many time you want print (default: 1)
 -s VAL : the string you want to print (default: hello world)
```
运行`java TestJava -n 5 -s 23333`会显示：
```bash
23333
23333
23333
23333
23333
main program
```

此外在Option中还有一些额外的配置。例如required标注的参数在使用时一定要手动赋值：
```java
@Option(name="-iamstupid", usage="you must be stupid", required=true)
public boolean joke1=true;
```
这样的话运行的时候就一定要加上`-iamstudid`。

另外，我们还可以标注对参数的赋值要求，例如上面可以看到在输出的帮助文档中usage显示在冒号的后面，而前面冒号除了参数名称还有一个类似参数类型的标注，这个也是可以手工配置的。
```java
@Option(name="-h", usage="show help doc")
public boolean help = false;

@Option(name="-n", usage="how many time you want print", metaVar="1<=n\<10")
public int n = 1;

@Option(name="-s", usage="the string you want to print", mataVar="String")
public String s = "hello world";

@Option(name="-iamstupid", usage="you must be stupid", required=true)
public String joke1=true;
```
此时`java TestJava -iamstupid -h`输出：

```bash
LDA [options ...] [arguments...]
 -h         : show help doc (default: true)
 -iamstupid : you must be stupid
 -n 1<=n\<10 : how many time you want print (default: 1)
 -s String  : the string you want to print (default: hello world)
```

再hadoop集群中需要注意的是第三方jar需要分发到各个节点，2.0之前通过`-libjars`选项，2.0之后把第三方jar包存放到`$HADOOP_HOME/share/hadoop/common`下即可。（网上看到的方法，前一种方法我试了没有成功，后一种方法成功了）

然后hadoop主程序读入参数后还需要将参数全局共享到各个Task节点上，通过job的Configuration可以完成这个工作。
```java
// main函数中向job写入参数
Configuration conf = new Configuration();
conf.setInt("max_count", option.max_count);

// map或者reduce中读出参数
Configuration conf = context.getConfiguration();
int max_count = conf.getInt("max_count", 50000);
```


## 分布式缓存
一些只读的小文件可以通过这个方式在节点间共享。
```java
// main函数中向job写入路径
DistributedCache.addCacheFile(new Path([String path in hdfs]).toUri(    ), conf);

// map或reduce中，通过DistributeCache读取文件
BufferedReader reader = new BufferedReader(new FileReader((cache    Files[0].toString())));
String s;
while ((s = reader.readLine()) != null) {
// 按行读入文件
}
reader.close();


```
## 其他
在新版本中貌似已经弃用IdentityMapper或者IdentityReducer了，直接使用Mapper.class或者Reducer.class就可以完成直接输出的功能。

### 参考
1. [Args4J使用指南](http://sunxboy.iteye.com/blog/697708)
2. [args4j的使用](blog.csdn.net/qy20115549/article/details/53588782)
