---
layout: post
title: 使用混合高斯模型对背景建模
date: 2017-05-18
category: 机器学习
tags:
- machinelearning
keywords:

---


## 一、原理

用GMM对背景建模的基本思想是把每一个像素点所呈现的颜色用K个高斯分布的叠加来表示，通常K取3-5之间。将像素点所呈现的颜色X认为是随机变量，则在每时刻t=1,…,T所得到视频帧图像的像素值只是随机变量X的采样值（观值）。

在进行前景检测前，先对背景进行训练，对每一帧图像中每个背景采用一个混合高斯模型进行模拟，背景一旦提取出来，前景的检测就简单了，检查像素是否与背景的高斯模型匹配，匹配是背景，不匹配就是前景。

所以关键就是混合高斯背景模型的建立。

GMM之所以能够将前景和背景分开是基于如下两点事实的：

(1)在长期观测的场景中，背景占大多数时间，更多的数据是支持背景分布的

(2)即使是相对颜色一致的运动物体也会比背景产生更多变化，况且一般情况下物体都是带有不同颜色的。

## 二、算法流程
1. 参数初始化：定义对每个像素建立几个单高斯组成混合高斯模型，一般去3到5，我取4，变量定义为C=4。另外每个高斯分布需要用三个变量表示，分别是权重w，均值mean和方差pixel\_sd。对图像的每个像素都需要建立C个高斯分布，所以这三个高斯分布参数变量是三个height\*width\*C大小的三维矩阵。初始化时，令mean在像素取值范围内去随机数，w取1/C，pixel\_sd人工进行初始化，我取值为9。另外几个参数后面提到再详细说明。
2. 一次读取一幅图像（假设像素是单通道，多通道的图像分别计算），对每个像素计算与本像素各个高斯的均值的差的绝对值，然后计算这个差值是否小于对应高斯的方差的D倍，这个是为了容忍噪音的，否则当北京训练趋于稳定的时候，方差会很小，很容易就与当前高斯模型不匹配。D通常定义为2.5。对于匹配的高斯模型参数进行如下调整（其中p是alpha/w，alpha是人为定义的学习速率，用于更新权重，p用于更新高斯模型，除以w的作用是使得权重越大的模型越稳定，而权重过小的新定义的模型可以更快的收敛）： 
![](/img/ComputerVisionGMM1.png)

对于所有的高斯模型的权重进行如下更新：
![](/img/ComputerVisionGMM2.png)

另一种参考文章里的更好的更新方式：
![](/img/ComputerVisionGMM2.1.png)

M是match的意思，也就是说如果当前像素与对应高斯匹配，M=1，否则M=0。

3. 我们发现进行上述更新后，匹配到的高斯权重会变大，没有被匹配的高斯权重会变变小，所以更新完成后，权重值和可能不唯一，所以要进行权重的归一化。
4. 然后对每个像素的所有高斯进行rank的计算，rank=w/pixel\_sd，也就是说rank分高意味着权重大、方差小。如果某个像素点的所有高斯都没有被匹配，就说明那个像素的模型建立得不好，就把rank最小的高斯模型换成一个匹配当前像素值的高斯，即mean设为当前高斯像素值，方差用人工定义的值初始化，w不变。
5. 然后进行北京的选择，这里需要定义一个阈值thresh，表示所有高斯模型中有多少比例构成北京，按照rank顺序将w进行累加，知道前B个高斯的权重满足thresh，就完成北京的选择。

## 三、实验

代码如下：

``` bash
clear all
close all
clc
% ----------------------- 使用第一帧获取图片大小 -----------------------

addpath('./data');
img_dir = dir('./data/*.jpg');
fr = imread(img_dir(1).name);           % 读第一幅图片
[height,width] = size(fr(:,:,3)); 

% ----------------------- 变量初始化 -----------------------------------

tolerance = 1;
C_max = 4;                       % 组成混合高斯模型的最多单高斯数目
D = 2.5;                     % 阀值（一般为2.5个标准差）
alpha = 0.01;               % 学习速率（一般为0到1）
thresh = 0.6;               % 前景阀值（0.25到0.47）
sd_init = 9;                 % 初始化标准差

% -------------------------初始化均值,权值和方差----------------------------
 
pixel_depth = 8;                        %  像素深度为8位
pixel_range = 2^pixel_depth - 1;         %  灰度范围

w=ones(height, width, C_max)/C_max;
pixel_sd=ones(height, width, C_max)*sd_init;
mean=rand(height, width, C_max)*pixel_range;
bg=zeros(height, width,3);
% -------------------------用于调试-------------------------
mean_history=zeros(C_max, 200);
pixel_sd_history=zeros(C_max, 200);
w_history=zeros(C_max, 200);
sort_history = zeros(C_max, 200);
match_history = zeros(C_max, 200);
%--------------------- 处理每一帧 -----------------------------------
for c =1:3
    for n = 1:150,


        % ----------------- diff ------------------
        fr = imread(img_dir(n).name);       

        % 把图像赋值C_max层，便于后面的矢量化操作
        pixel=zeros(height,width,C_max);
        for i = 1:C_max
            pixel(:,:,i) = fr(:,:,c);
        end

        % 计算像素差的绝对值
        u_diff = abs(double(pixel) - double(mean));



        % 获得针对每个像素各个高斯分布的c_max层的match矩阵，为1的元素是匹配到的高斯成分
        match = (u_diff <= (D*pixel_sd+tolerance)) ;
        for i = 1:C_max
            match_history(i,n) = sum(sum(match(:,:,i)))/(576*720);
        end
        % 根据match更新各个高斯分布参数
        p = ones(height,width,C_max)*alpha./w;
        w = w*(1-alpha)+match*alpha;
        delta = pixel.*match + (1-match).*mean;
        mean = (1-p).*mean + p.*delta;
        delta = sqrt((1-p).*pixel_sd.^2 + p.*(double(pixel) - mean).^2);
        pixel_sd = match.*delta +(1-match).*pixel_sd;

        % 获得针对每个像素各个高斯分布的c_max层的match矩阵
        % 为1的元素是说明对应位置的像素没有任何一个高斯成分被匹配到，需要把评分最小的高斯成分进行替换
        unmatch=sum(match,3)==0;


        % 计算排序的rank矩阵
        rank=w./pixel_sd;
        [min_rank,min_rank_index] = min(rank,[],3);

        % 根据min_rank_index生成与w和pixel_sd大小一致的索引old_index，索引矩阵素为1的位置是需要被替换掉的高斯分量
        old_index=ones(height,width,C_max);
        for i =1:C_max
            old_index(:,:,i) = ((old_index(:,:,i)*i).*unmatch) == min_rank_index;   
        end

        % 对需要替换的高斯分量进行替换
        mean = (1-old_index).*mean + old_index.*double(pixel);
        pixel_sd=(1-old_index).*pixel_sd + old_index.*(ones(height,width,C_max)*sd_init);

        % 权值归一化   
        sum_w=sum(w,3);
        for i=1:C_max
            w(:,:,i) = w(:,:,i)./sum_w;
        end


        rank=real(w./pixel_sd);    % 不知道为什么算出来时虚数，但是虚部为零，用real处理一下
        [sort_rank, sort_rank_index] = sort(rank, 3, 'descend');
        background = zeros(height,width);
        now_thresh = zeros(height,width);
        bg_match = zeros(height,width,C_max);
        for i = 1:C_max
            [x,y]=meshgrid(1:width,1:height);
            now_index = (sort_rank_index(:,:,i)-1)*height*width+(x-1)*height+y;
            bg_match(:,:,i) = now_thresh<=thresh;
            now_thresh = now_thresh + w(now_index);
            background = background + mean(now_index).*w(now_index).*bg_match(:,:,i);
            sort_history(i,n) = sum(sum(sort_rank_index(:,:,i)));
        end

        bg_match = (1-match).*(1-bg_match);
        bg_match = sum(bg_match,3)>0;



        % -------------统计---------------
        for i = 1:C_max
            w_history(i,n) = sum(sum(w(:,:,i)))/(576*720);
            mean_history(i,n) = sum(sum(mean(:,:,i)))/(576*720);
            pixel_sd_history(i,n) = sum(sum(pixel_sd(:,:,i)))/(576*720);

        end

        
        imshow(uint8(background))
        drawnow
        n

    end
    bg(:,:,c)=background;
end
imwrite(uint8(bg),'bg2.jpg')
```

视频截图：
![](/img/ComputerVisionGMM5.jpg)

选择150张图片进行背景建模，分通道提取单色背景，然后将三个颜色进行叠加，背景如下： 
![](/img/ComputerVisionGMM3.png)

## 四、调参
1. 矢量化编程

开始的时候使用for循环对每张图片每个像素进行上述计算，在matlab上一次处理200张图片需要2个小时左右，这使得尝试新参数变得很困难，因为一个下午满打满算也只能尝试两三组参数。

后来在深度学习相关资料上看到了矢量化编程的概念，就是在python或者matlab等类似较高层语言上进行数学计算的时候，尽量不要使用for循环，要利用内建的适量运算来达到并行，然后按照矢量化的方法进行重写之后，一次运行需要5到10分钟左右。

具体方法是一幅图像看成一个height\*width\*C\_max的图像，然后直接对这个三维数组进行运算，如果涉及到匹配与不匹配的运算不同的情况，添加一个同样大小的match数组来表明当前位时候需要计算。

2. 关于调参
![第一个高斯的命中率](/img/ComputerVisionGMM4.png)


  如上图示第一个高斯配匹配的命中率，其他几个高斯分布大致如此不过第一个的命中率最高。关于阈值，基本上最大的高斯分布的阈值在0.3-0.5左右，如果阈值过小，会只取到一个高斯，阈值过大又会取到不属于背景的部分。最后经过尝试thresh=0.6


参考：[前景检测算法GMM](https://www.cnblogs.com/tornadomeet/archive/2012/06/02/2531565.html)

