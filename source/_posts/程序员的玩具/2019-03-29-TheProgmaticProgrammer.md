---
layout: post
date: 2019-03-29
title: 《程序员修炼之道》
category: 程序员的玩具
tags: 
- reading
keywords: 
description: 
---

1. Care about your craft. 关心你的技艺。
2. Think！About your work. 思考你的工作。
3. Provide Options, Don't make lame excuses. 提供各种选项，不要找蹩脚的借口。
4. Don't live with broken windows. 不要容忍破窗户。
5. Be a Catalyst for Charge. 主动的去催生变化。“请求原谅比获取许可更容易。”
6. Remember the big picture. 不要像青蛙一样，只注意眼前的事就会被温水煮熟，要关注大图景。

<!-- more -->

7. Make Quality a Requirements Issue. 
8. Invest Regularly in your knowledge portfolio. 学习和投资一样：定期执行、多元化、平衡风险与收益、低买高卖、重新评估与再平衡。
9. Critically analyze what you read and hear. 怀疑并求证。
10. It is Both What you say and the way you say it. 形式和实质一样重要。首先要弄清自己想说什么，然后要弄清听众想听什么，最后用良好的形式对接这两者。有效的交流可以提升自己的影响力（这可比写博客有效多了）。
11. DRY: Don't Repeat Yourself. 系统中的每一项知识都必须具有单一、无歧义的、权威的表示。举例子一，代码和注释其实也是一种重复，低级的信息应该存放在代码中并使代码自身具有自解释性，高级的指导思想存在于注释中，这样可以使得不用修改代码的一点细节就修改注释。不可信的注释比没有注释更可怕。文档、测试用例同理。在举一个例子二，类中的一些属性如果可以通过其他属性计算得到就不要额外存储，比如长度。但是往往为了效率，我们在需要频繁获取长度的时候就会存储长度而不是每次计算。为了平衡这两者，我们可以使用缓存并使用额外的标记表示缓存是否过期，然后对长度的访问应该通过访问器（accessor,类似于python中的property）将细节隐藏。总的来说，这是非常重要的一个原则，有时很容易注意到（比如我们在写数据库接口的时候很容易想到不将数据库schema硬编码在代码中），但是有时又很难注意到（比如在文档中会重复代码的逻辑，或者架构图，从这个角度看，markdwn对图片的引用比word要好。）
12. Make easy to reuse.
13. Eliminate effects between unrelated things. 保持正交性、解耦性。要经常问问自己，改动一个模块，其他的地方会怎样的受到影响。正交性的一个尝试是面向切片编程————AOP。另外，良好解耦的模块可以被良好的测试，而能否单独的对一个模块进行测试也是检查该模块是否与系统解耦的一个手段。
14. There are no final dicision. 比如不要假定就用某个数据库了，如果把数据库抽象为“数据持久化”的某种服务，那么就可以中途切换数据库。
15. Use tracer bullets to find the target. 意思就是要及时反馈。包括构建机器学习项目，也是需要首先可以跑通一个完整的流程，之后再调优它。
16. Prototype for learn. 原型系统和曳光弹不太一样，后者强调要先有一个完整的闭环的系统，然后可以对其进行迭代，而前者不一定能用，只是为了确定想法、验证思路或者是学习经验。比如在建新楼之前会用纸板打一个建筑的模型对其进行压力、稳定性等方面的测试，这就是一个原型系统。
17. Program close to the problem domain. 
18. Estimate to avoid surprise. 一个有效但经常被忽略的方法：去问已经做过这件事的人。而且正如第 10 条备忘提示的那样，在回答问题之前，先理解问题。
19. Iterate the schedule with the code.
20. Keep knowledge in plain text. 纯文本相比二进制有两个缺点，空间更多、计算代价更大。但是安全性不是二进制的优点，如果担心安全性，就对纯文本加密，如果担心完整性，就加上哈希。
21. Use the power of commands shells. 
22. Use a single editor well. 好的编辑器具备的能力：（1）可配置。包括字体、颜色、窗口分割以及按键绑定。（2）可扩展。可以支持多种语言，这通常可以使用插件或者扩展的方式做到。（3）可编程。可以通过宏或者内置的脚本语言完成复杂的工作。除此之外还应具有：编译、调试、高亮、自动缩进、重构、函数跳转等功能。
23. Always use source code control. 把整个项目置于源码控制系统下有一个好处就是，可以自动化的进行某些任务。比如，在每天午夜，检查有无最近更新，如果有的话进行测试等工作。
24. Fix the problem, not the blame.
25. Don't panic. 这是用于调试 bug 的第一准则，也是解决问题的第一准则。
26. "Select" isn't broken. 
27. Don't assume it. Prove it.
28. Learn a text manipulation language. shell程序员喜欢使用shell本身加上sed与awk。而python和perl也是处理文本的尖刀利器。
29. Write code that can write code. 分为主动代码生成器和被动代码生成器。被动代码生成器很好理解，比如一些代码片或者根据uml图生成类模板的工具，代码生成后直接拷贝到编辑器中，这段代码就和生成器没有关系了。而主动代码生成器则是按需生成，用过就扔的。比如，前面提到的数据库模式的例子，我们通常会写一些读取数据库配置的代码获得数据库模式并且根据模式设计接口，而主动代码生成器也许可以自动根据数据库模式以及用户设定信息生成接口代码。
30. You can't write perfect software. 每个想要写出好代码的人都知道防御性编程。使用严苛的测试、在代码中插入断言、在数据库中添加约束。这一条备忘更进一步：好的程序员应该连自己也不信任。
31. Design with contracts. 合约包括：前条件、后条件、类不变项。比如计算平方根的函数，需要的前条件是保证输入参数一定非负，因此，在sqrt函数内部可以假定参数一定正确。除此之外，循环不变量是“合约”的一种。另外，实现“is-a”关系的公有继承也是一种“合约”，具体来说，是**Liskov替换原则**：“子类必须要能通过基类的接口使用，而使用者无需知道其区别。” 但是对于具体的行为能否满足合约，大部分编译器都无法检查是否完成了具体的行为，只能检查函数的签名（signature）。因此，合约可以写在注释中。从语言的角度，Eiffel和Sather支持合约，而C++、java等常见语言有一些额外的工具帮助语言提供合约功能。合约有助于程序“早崩溃”，比如eiffel在sqrt接收到负数时会抛出运行时异常、C++则回返回NaN并在之后对返回值的使用中使得程序崩溃。
32. Crash early. Java在内的很多语言已经采取了这一哲学。在意料之外的某件事情在runtime系统中发生时，他会抛出RuntimeException。如果没有被捕获，该异常会渗透到程序的顶部，致使其终止，并显示栈踪迹。 C 中没有异常机制，因此大多数处理方法是自定义一个名为`check`的宏。但是注意，有时简单的退出运行中的程序并不合适，因为申请的资源尚未释放，日志信息尚未写入等等，这部分内容之后讨论，但是总的原则要记住：当runtimeexception出现时，意味着不可能发生的事情已经发生，此时让它死掉比让它继续“为祸世间”要好。
33. If it can not happen, use assertions to ensure that it won't. 首先，传递给断言的代码不应有副作用。其次，断言可能在编译时被关闭，因此必须执行的代码不要放在断言中。再次，不要用断言代替真正的错误处理，断言检查的是绝不会发生的事情，而可能但不被期望的事情要用异常机制捕获。或者也可以在断言失败后跳转到错误处理点，然后释放资源。
34. Use exceptions for exceptional problems. 异常机制不应参与到正常的程序流程中，可以问问自己：如果把所有的异常处理代码全部拿走，程序能否正确运行？如果答案是否定的，那么这时的异常机制可能被错误的使用了。这背后的原因是考虑到，异常表示即时的、非局部的、可能级联的控制权转移，如果让这种机制参与到正常处理流程中，可读性和封装性会大大降低：例程和调用者被异常处理紧密的结合了起来（当你使用一个可能抛出异常的函数时，必须要自己写代码将异常继续抛出或者是原地捕获）。
35. Finish what you start. 狭义的，这是指处理程序申请的资源，即“谁申请谁负责”。举个例子，一个文件处理类，将打开文件和关闭文件的代码分别放在两个函数中，文件句柄作为类成员存在，这意味着两个函数被紧密的耦合在了一起。而且，这种情况是普遍的，任意共享全局变量的多个函数都会存在紧耦合的情况，这种情况很容易发生，我自己就写出过到处使用全局变量的机器学习任务的代码，最后每个函数仿佛都具有“副作用”。对于多个资源的分配，有两个简单的原则：（1）以分配相反的顺序释放资源。（2）多个地方分配同一组资源的时候，以统一的顺序进行以避免死锁。另外还有几个技巧：（1）利用对象自身的构造函数与析构函数，将一组资源封装在对象中很有效。（2）同时涉及到资源分配与异常的地方需要注意，异常使得正常的资源释放会遇到困难，这类问题没有解决的万金油，要具体问题具体分析。比如C++中，正常流程和异常流程中都写了释放资源的代码，这显然违反了DRY原则，因此，可以利用语言自身的特性避免这种“未配平”的资源，一种方式是不要动态申请资源，而是在栈上申请资源，然后利用对象离开作用域时自动释放资源。如果一定要使用指针，可以自己写一个资源类将资源指针封装起来，并在析构函数中释放资源，实际上，C++中的智能指针就是做这个用的。Java的话则提供了`finally`子句做这些事情。
36. Minimize coupling between modules. 得墨忒耳定律：对象 O 的 M 方法，可以访问/调用如下的：（1）对象 O 本身；（2）M 方法的传入参数；（3）M 方法中创建或实例化的任意对象；（4）对象 O 直接的组件对象；（5）在M范围内，可被O访问的全局变量。举个例子：假设我在便利店购物。付款时，我是应该将钱包交给收银员，让她打开并取出钱？还是我直接将钱递给她？再举一个例子：人可以命令一条狗行走（walk），但是不应该直接指挥狗的腿行走，应该由狗去指挥控制它的腿如何行走。实际上该法则常常表现为单次委托，而不是对一个对象进行链式调用，即`a.f1().g1().getC()`类似的形式，即“只和自己的朋友交流”。
37. Configure. Don't integrate. 
38. Put abstractions in code, details in metadata. 这种方法迫使你接触你的设计的耦合；迫使你推迟细节处理，创建更抽象更健壮的设计；使得无需编译应用就可以完成定制；可以使用相同的应用引擎搭配不同的元数据完成不同的任务。通过元数据使得设计具有“可撤销性”。注意当前的大多数大数据分布式框架都有大量的配置文件存储元数据。
39. Analyze workflow to improve concurrency. 
40. Design using services.
41. Always design for concurrency.
42. Seperate views from models. MVC模型。分离后的对象之间的通信可以采取发布订阅的方式，观察者模式中使用了这一思想。MVC狭义上是用于GUI的，但是这一编程技术的思想可以用于更广泛的领域。模型表示对象的抽象数据模型；视图是解释模型的方法，他订阅模型中的变化与来自控制器的逻辑事件；控制器用于控制视图，并向模型提供新数据的途径，它既向模型也向视图发布事件。
43. Use blackboards to coordinate workflow. 
44. Don't program by coincidence.
45. Estimate the order of your algorithms.
46. Test your estimates. 注意最好的并非总是最适合的。意思是假设任务是对于数十个元素排序，那么简单的插入排序可能比快排还要快，而且调试起来更加简单。
47. Refactor early. Refactor often. 关于重构的一些简单原则：（1）不要试图在重构的同时增加功能。（2）在重构前确保拥有良好的测试，并且尽可能频繁的运行测试以证明重构有效。（3）采取短小而深思熟虑的步骤，比如增删某个字段或融合两个方法。确保这些局部改动之间可以通过预设的测试。最后，如果你担心重构是否是必要的，看看第四条备忘录：不要容忍破窗户。
48. Design to test. 如备忘录31描述的，应该使用合约进行设计。这条备忘录强调的是设计合约的同时应该设计测试该合约的代码。易于使用的测试代码还有另外的好处：（1）测试代码实际上是如何使用该模块的样例代码。（2）可以在未来的重构中验证重构的有效性。当软件部署后在使用调试器有些困难，这时可以使用的手段是日志或者web系统（比如hadoop系列工具都会在指定窗口上展示工作状态。）
49. Test your software, or your users will.
50. Don't use wizard code you don't understand.
51. Don't gather requirements ———— Dig for them. 看我的研究生组就知道了。我们甚至不是在搜集需求，而是在制造需求。
52. Work with a user to think like a user.
53. Abstractions live longer than details.
54. Use a project glossary. 统一词汇。
55. Don't think outside the box. Find the box. 决定自己解决问题的真正约束是哪些，而不要自缚手脚。然后优先考虑最重要的约束，再考虑其次的。更重要的是：关注于本质问题，不要被外围问题转移注意，即所谓“本质复杂度”优于“偶然复杂度”。
56. Listen to nagging doubts. Start when you are ready. 要准备好，而不是要拖延。
57. Some things are better done than described. 
58. Don't be a slave to formal methods.
59. Expensive tools do not produce better designs.
60. Organize around functionality, not job functions.
61. Don't use manual procedures. 通常`cron`、`makefile`等工具都有助于使你充分的利用起晚上的时间。
62. Test early. Test often. Test automatically.
63. Coding ain't done till all the test run. 回归测试是指将当前测试的输出与先前的只进行对比检查哪些地方存在变动。
64. Use saboteurs to test your testing. 
65. Test state coverage, not node converage.
66. Find bug once.
67. Treat English as just another programming language. `literal programming`是一种流派，把编程和写作融为一体。
68. Build documentation in. Don't bolt it on.
69. Gently exceed your users' expectations.
70. Sign your work.
