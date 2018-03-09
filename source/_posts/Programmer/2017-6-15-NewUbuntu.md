---
layout: post
title: Ubuntu装机
category: 程序员的玩具
tags: 
- linux 
- tools
keywords: 
description: 
---


## Vim
```bash
sudo apt install vim
```

## 搜狗输入法(参考<http://www.linuxdiyf.com/linux/22075.html>)
1. 官网下载系统对应安装包(使用uname -m命令查看系统位数),如果是14以上的系统，尝试直接双击安装，如果成功就无需后续步骤。
2. 配置fcitx。因为搜狗中文输入法基于fcitx，而ubuntu系统默认的输入法框架是iBus。
	1. 添加源:`sudo add-apt-repository ppa:fcitx-team/nightly`
	2. 更新源:`sudo apt-get update`
	3. 安装fcitx:`sudo apt-get install fcitx`
	4. 安装fcitx配置工具:`sudo apt-get install fcitx-config-gtk`(这个步骤我做的时候提示不用安装)。
	5. 安装table-all软件包:`sudo apt-get install fcitx-table-all`(这个步骤我没有做，因为感觉没有必要)。
	6. 安装im-switch切换工具:`sudo apt-get install im-switch`(这个步骤我没有做，因为感觉没有必要)。
	7. `im-config`命令，如果弹出窗口中选择的不是fcitx，就改成fcitx，然后重启电脑。
3. 安装搜狗输入法安装包，下载的是deb安装包，到所在文件夹使用`sudo dpkg -i <搜狗输入法包名>`进行安装。
4. `fcitx-config-gtk3`命令，点击加号，取消“Only Show Current Language”，输入sogou找到搜狗输入法。
5. 我的安装过程中有依赖项不满足的情况，使用`sudo apt-get check`检查依赖，然后使用`sudo apt -f install`安装不满足的依赖项。

## git
```bash
sudo apt install git
```

## Markdown编辑器——Haroopad
一款跨平台的Markdown编辑器。下载链接：<https://bitbucket.org/rhiokim/haroopad-download/downloads/haroopad-v0.13.1-x64.deb>
四十兆多一点，比我在windows上用的MarkdownEditor.exe大了不少，不过这个代价换来的是更强的预览功能，导出PDF功能，自定义主题和字体大小，代码提示与折叠，同步滚动，甚至是Vim模式（虽然这个我没用到...)。
使用`sudo dpkg -i haroopad.deb`来安装，安装之后调整一下配置，可配置向不多，编辑主题我选择的是solarized light，预览主题选择的是default，其他的根据自己喜好调整即可。
<!-- more -->

## 截图工具
有一些很好的截图工具但是需要另外下载，其实在Ubuntu内自带一个很好的截图工具就叫“截图”（汗）。我试了一下，这个工具完全满足我的需要了，然后添加到启动器中方便使用。

## Flash 浏览器插件
```bash
sudo apt-get install flashplugin-installer
```

## 编辑器Sublime-Text3
```bash
sudo add-apt-repository ppa:webupd8team/sublime-text-3
sudo apt-get update
sudo apt-get install sublime-text
```
### 中文输入问题：
参考[这篇文章](http://blog.csdn.net/jackailson/article/details/50878089)

## scrapy
最近在学这个爬虫框架，就把这个也写进去喽。
首先安装一些依赖包：
```bash
sudo apt-get install python-dev python-pip libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev
```
- python-dev：外部引用python时需要的开发包
- python-pip：python包安装工具
- libxml2-dev：C语言的XML程式库,能简单方便的提供对XML文件的各种操作,并且支持XPATH查询,及部分的支持XSLT转换等功能

```bash
sudo apt-get install Scrapy
```

## WPS
官网下载下载[安装包](http://kdl.cc.ksosoft.com/wps-community/download/a21/wps-office_10.1.0.5672~a21_amd64.deb)

```bash
sudo dpkg -i wps-office_10.1.0.5672~a21_i386.deb
```

## PDF阅读器——Okular
支持多类文档，并且注释功能强大
```bash
$ sudo apt-get install okular
```

## bt客户端
```bash
sudo apt-get install deluge
```

## jekyll
```bash
sudo apt install jekyll
```

## SMplayer
```bash
sudo apt-get install smplayer
```
### 中文设置
options-preferences-interface-language-zh_CN

## Ubuntu软件中心闪退
```bash
sudo apt-get update
sudo apt-get dist-upgrade
sudo apt-get install --reinstall software-center
```
dist-upgrade会比较灵活地处理包的依赖关系，而upgrade则不会，如果依赖包出了问题，upgrade会停止更新。

## 垃圾清理
```bash
sudo apt-get autoremove
sudo apt-get autoclean
uname -r #查看当前内核
dpkg --get-selections|grep linux #查看系统中的内核文件
sudo apt-get purge <image/header> # 删除掉小版本号的image和header文件
sudo apt-get remove libreoffice-common # 删除libreoffice
sudo apt-get remove unity-webapps-common # 删除Amazon的链接
sudo apt-get remove thunderbird totem rhythmbox empathy brasero simple-scan gnome-mahjongg aisleriot gnome-mines cheese transmission-common gnome-orca webbrowser-app gnome-sudoku landscape-client-ui-install onboard deja-dup # 删掉基本不用的自带软件
```

## 安装pip
因为我比较喜欢python3.x，所以我只直接安装pip3
```bash
sudo apt-get install python3-pip
sudo -H pip3 install --upgrade pip
```
安装目录在`/usr/local/lib/python3.x/dist-package`
接下来安装几个常用的包
```bash
sudo -H pip3 install pip-autoremove
sudo -H pip3 install numpy
sudo -H pip3 install matplotlib
sudo -H pip3 install jupyter notebook
```

---

