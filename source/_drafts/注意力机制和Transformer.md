[把Transformer模型掰开揉碎，深度理解它的工作原理](https://zhuanlan.zhihu.com/p/54356280)

编码器部分讲得很细致。对于《Attention is All You Need》中的Transformer中的“多头”注意力（“multi-headed” attention）、位置编码向量与残差连接有比较清晰的解释。

关键点：

- 多头注意力扩展了模型专注于不同位置的能力。即同一个单词在不同的注意头中可能会关注本句中不同的位置。
- 多头注意力给出了注意力层的多个“表示子空间”（representation subspaces）。接下来我们将看到，对于“多头”注意机制，我们有多个查询/键/值权重矩阵集。
- 原始论文里描述了位置编码的公式。这不是唯一可能的位置编码方法。然而，它的优点是能够扩展到未知的序列长度(例如，当我们训练出的模型需要翻译远比训练集里的句子更长的句子时)。

[通俗易懂！使用Excel和TF实现Transformer ](https://mp.weixin.qq.com/s?__biz=MzI0ODcxODk5OA==&mid=2247505978&idx=2&sn=709e15361deb0a153d133ffd58c9e7d9&chksm=e99eebc3dee962d517f7457a3c6458919ec6bae11fef3e723bc1522700adc45689194e1341e8&mpshare=1&scene=1&srcid=&pass_ticket=dy6dZXLF%2FzFylhF1Gr9hEgqTV9eLLpFyUW8HFkh7pO6r3aW%2BVEQumUn5WxtWdND6#rd)

一片国产文章，可以说比上面那篇还细致，尤其是解码器中的masked multi-head self attention 和 encoder-decoder attention两个步骤讲的比上一篇文章清楚。而且还配套tf代码和计算实例，很不错。关于`tf.split`和`tf.concat`那块可能是计算细节，没太看仔细。基本看完这篇就能看懂transformer了。

[深度学习中的注意力模型（2017版）](https://zhuanlan.zhihu.com/p/37601161)

张俊林出品。

[一文解读NLP中的注意力机制](https://mp.weixin.qq.com/s?__biz=MzI3MTA0MTk1MA==&mid=2652038546&idx=3&sn=9c11a88ae73d89bda734721cb8c3d5c1&chksm=f1219163c6561875fc9d8417adeeb893a5811ee61362c88d58212c8207432b2e8a2d08847b59&mpshare=1&scene=1&srcid=&pass_ticket=dy6dZXLF%2FzFylhF1Gr9hEgqTV9eLLpFyUW8HFkh7pO6r3aW%2BVEQumUn5WxtWdND6#rd)

类似于上一篇，但是讲的更实在更细致。是一篇从seq2seq讲到Self-Attention的文章，关于attention的改进也有些许提及。是一篇简单的综述类型的文章。

[放弃幻想，全面拥抱Transformer：自然语言处理三大特征抽取器（CNN/RNN/TF）比较](https://zhuanlan.zhihu.com/p/54743941)

依然是张俊林出品，是18年微信里的一篇爆文。整体的介绍了NLP中特征抽取器的发展。

关键点：

- RNN的最大的问题在于其并行计算的难度。对于这一问题，学界尝试的解决办法有二：一是改变隐层之间的全连接关系，二是打断隐层之间的连接并加深层次，但是这种思路本质上和CNN殊途同归。
- NLP领域最早的CNN尝试是Kim在2014年的工作，架构是单层的一维卷积 + 句子方向上的池化 + 全连接。这个传统版本的CNN架构一看就是从CV领域套过来的。效果当时在主要领域上没法与RNN匹敌，为啥嘞？“最根本的症结所在还是老革命遇到了新问题，主要是到了新环境没有针对新环境的特性做出针对性的改变，所以面临水土不服的问题。”
- 问题一在于单层CNN无法捕获长距离的特征，因此两种改进手段是：带孔DNN和深层CNN。简单的多层CNN在三层以上就不好优化了，因此人们会考虑把Skip Connection及各种Norm等参数优化技术引入，这才能慢慢把CNN的网络深度做起来。
- Kim版本的CNN的第二个问题是池化层直接把位置信息消掉了。“CNN的卷积核是能保留特征之间的相对位置的，道理很简单，滑动窗口从左到右滑动，捕获到的特征也是如此顺序排列，所以它在结构上已经记录了相对位置信息了。......所以在NLP领域里，目前CNN的一个发展趋势是抛弃Pooling层，靠全卷积层来叠加网络深度，这背后是有原因的（当然图像领域也是这个趋势）。”在介绍到后面时也会发现，Transformer中会很注重位置信息。
- “卷积核里引入GLU门控非线性函数也有重要帮助，限于篇幅，这里不展开说了，GLU貌似是NLP里CNN模型必备的构件，值得掌握。”
- 这篇文章中给了三篇Transformer的参考文章，都是国外的，由浅入深。第一篇的中文版就是本文列表中的第一篇文章。
- “Transformer原始论文一直重点在说Self Attention，但是目前来看，能让Transformer效果好的，不仅仅是Self attention，这个Block里所有元素，包括Multi-head self attention，Skip connection，LayerNorm，FF一起在发挥作用。”
- CNN的卷积层其实也是保留了位置相对信息的，所以什么也不做问题也不大。对于Transformer来说，为了能够保留输入句子单词之间的相对位置信息，必须要做点什么。因为输入的第一层网络是Muli-head self attention层，我们知道，Self attention会让当前输入单词和句子中任意单词发生关系，然后集成到一个embedding向量里，但是当所有信息到了embedding后，位置信息并没有被编码进去。
- “单从任务综合效果方面来说，Transformer明显优于CNN，CNN略微优于RNN。速度方面Transformer和CNN明显占优，RNN在这方面劣势非常明显。这两者再综合起来，如果我给的排序结果是Transformer>CNN>RNN。”
- 上述的比较方式都是三种模型的base形态，RNN和CNN如果加深或者加上attention机制也不会有什么质的飞跃。不过文中提到一种“寄居蟹”策略，可以极大的提升RNN和CNN的效果，就是把Transformer中的基础block中的self-sttention层换成Bi-RNN层或者CNN层。但是和Transformer比还是有一些差距。
- Transformer的局限性：注意力只能处理固定长度的文本字符串。在输入系统之前，文本必须被分割成一定数量的段或块。另外，这种文本块会导致上下文碎片化。例如，如果一个句子从中间分隔，那么大量的上下文就会丢失。换言之，在不考虑句子或任何其他语义边界的情况下对文本进行分隔。为解决该问题，Transformer-XL是一种尝试。


[一文解读NLP中的注意力机制](https://mp.weixin.qq.com/s?__biz=MzI3MTA0MTk1MA==&mid=2652038546&idx=3&sn=9c11a88ae73d89bda734721cb8c3d5c1&chksm=f1219163c6561875fc9d8417adeeb893a5811ee61362c88d58212c8207432b2e8a2d08847b59&mpshare=1&scene=1&srcid=&pass_ticket=dy6dZXLF%2FzFylhF1Gr9hEgqTV9eLLpFyUW8HFkh7pO6r3aW%2BVEQumUn5WxtWdND6#rd)

- Bahdanau等人发表了论文《Neural Machine Translation by Jointly Learning to Align and Translate》，该论文使用类似attention的机制在机器翻译任务上将翻译和对齐同时进行，这个工作目前是最被认可为是第一个提出attention机制应用到NLP领域中的工作。
- 深度学习中的注意力可以广义地解释为重要性权重的向量：为了预测一个元素，例如句子中的单词，使用注意力向量来估计它与其他元素的相关程度有多强，并将其值的总和作为目标的近似值。
- Bahdanau等人在其文章的摘要中也说到编码器生成的这个context向量可能是提高这种基本encoder-decoder架构性能的瓶颈。为了缓解中间向量context很难将Source序列所有重要信息压缩进来的问题，特别是对于那些很长的句子。提出在机器翻译任务上在 encoder–decoder 做出了如下扩展：**将翻译和对齐联合学习**。这个操作在生成Target序列的每个词时，用到的中间语义向量context是Source序列通过**encoder的隐藏层的加权和**，而传统的做法是只用encoder最后一个时刻输出作为context，这样就能保证在解码不同词的时候，Source序列对现在解码词的贡献是不一样的。
