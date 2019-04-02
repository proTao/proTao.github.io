---
layout: post
date: 2018-06-30
title: [译]Counting Objects in C++
category: C++
tags:
- C++
- translation
---

[Counting Objects in C++](http://www.ieee.org.cn/dispbbs.asp?boardID=61&ID=15406)

在c++中对给定类分配的所有对象进行计数并不困难，除非您必须处理分散注意力的问题。

有时候简单的事情很简单，但它们仍然很微妙。例如，假设您有一个类Widget，并且希望有一种方法能够在运行时查明存在多少Widget对象。一种既容易实现又给出正确答案的方法是在Widget中创建静态计数器，每次调用Widget构造函数时递增计数器，每次调用Widget析构函数时递减计数器。您还需要一个静态成员函数`how many`来报告当前有多少Widget。如果Widget什么也不做，只是跟踪它的类型存在的数量，那么它看起来或多或少是这样的。

```CPP
class Widget {
public:
    Widget() { ++count; }
    Widget(const Widget&) { ++count; }
    ~Widget() { --count; }

    static size_t howMany()
    { return count; }

private:
    static size_t count;
};

// obligatory definition of count. This
// goes in an implementation file
size_t Widget::count = 0;
```

这很好。惟一稍微有点棘手的是要记住实现复制构造函数，因为编译器默认生成的小部件复制构造函数不知道如何增加计数。

如果您必须仅为小部件执行此操作，那么您就完成了，但是您可能希望为几个类实现对象计数。一遍又一遍地做同样的事情会变得乏味，单调会导致错误。为了避免这种单调，最好以某种方式打包上述对象计数代码，以便在任何需要它的类中重用它。理想的方案是:
- 易于使用——对于想要使用它的类作者来说，只需要很少的工作。理想情况下，它们做的事不应该多于一件，也就是说，不应该只说“我想计算这种类型的对象”。
- 高效——不要对使用包的客户端类施加不必要的空间或时间惩罚。
- 万无一失——几乎不可能意外地得出一个错误的数字。(我们不会担心恶意客户端，那些故意想搞乱统计的客户端。在c++中，这样的客户总是可以找到一种方法来做他们的坏事。

让我们暂停一下，考虑一下如何实现满足上述目标的可重用对象计数工具。这可能比你想象的要难。如果它像它看起来应该的那样简单，你就不会在这本杂志上读到关于它的文章。在您仔细考虑对象计数问题的解决方案时，请允许我切换到看似无关的主题。该主题是构造函数抛出异常时new和delete之间的关系。当你要求c++动态分配一个对象，你使用一个新的表达式，如:

```CPP
class ABCD { ... }; // ABCD = "A Big Complex Datatype"
ABCD *p = new ABCD; // a new expression
```

这个`new`表达式——它的意思被嵌入到语言中，并且它的行为是你无法改变的——做了两件事。首先，它调用一个名为operator new的内存分配函数。该函数负责寻找足够的内存来容纳ABCD对象。如果对运算符new的调用成功，那么新表达式将在运算符new找到的内存上调用ABCD构造函数。但是，我们不能假设代码永远执行的一帆风顺。假设操作符new抛出std::bad_alloc异常。这种类型的异常表明动态分配内存的尝试失败了。在上面的`new`表达式中，有两个函数可能导致该异常。第一个是调用运算符new，该运算符应该能够找到足够的内存来容纳ABCD对象。第二个是ABCD构造函数的后续调用，该构造函数将原始内存转换为有效的ABCD对象。

如果异常来自对运算符new的调用，则没有分配内存。但是，如果对运算符new的调用成功，并且ABCD构造函数的调用导致异常，则必须回收运算符new分配的内存。如果不是，则程序有内存泄漏。客户端(请求创建ABCD对象的代码)不可能确定哪个函数导致异常。多年来，这一直是c\+\+语言规范草案中的一个漏洞，但在1995年3月，c\+\+标准委员会通过了该规则：如果在新表达式期间，操作符new的调用成功，随后的构造函数调用抛出异常，则运行时系统必须自动释放操作符new分配的内存。此释放由操作符delete执行，该操作符与操作符new类似。`new`和`delete`之间的这种关系会影响我们自动计算对象实例化的次数。


## Counting Objects
很可能，您对对象计数问题的解决方案涉及到对象计数类的开发。您的类可能看起来和前面展示的Widget类非常像，甚至完全一致。

```CPP
 // see below for a discussion of why
// this isn't quite right

class Counter {
public:
    Counter() { ++count; }
    Counter(const Counter&) { ++count; }
    ~Counter() { --count; }
    static size_t howMany()
        { return count; }

private:
    static size_t count;
};
// This still goes in an
// implementation file
size_t Counter::count = 0;
```

这里的思想是，需要计算现有对象数量的类的作者只需使用 Counter 来管理簿记。有两种明显的方法可以做到这一点。一种方法是将计数器对象定义为类数据成员，如:

```CPP
// embed a Counter to count objects
class Widget {
public:
    .....  // all the usual public
           // Widget stuff
    static size_t howMany()
    { return Counter::howMany(); }
private:
    .....  // all the usual private
           // Widget stuff
    Counter c;
};
```

另一种方法是通过继承 Counter 类：

```CPP
// inherit from Counter to count objects
class Widget: public Counter {
    .....  // all the usual public
           // Widget stuff
private:
    .....  // all the usual private
           // Widget stuff
};
```

这两种方法都有优点和缺点。但在我们研究它们之前，我们需要观察到，这两种方法在目前的形式下都行不通。这个问题与计数器内部的静态对象计数有关。因为真正负责计数的静态数值变量只有一个，但是我们需要为每个使用Counter的类都提供一个。例如，如果我们想同时计算类小部件和类ABCD，我们需要两个静态size_t对象，而不是一个。使Counter::count非静态并不能解决问题，因为我们需要每个类一个计数器，而不是每个对象一个计数器。我们可以通过使用所有c++中最著名但命名古怪的技巧之一来获得我们想要的行为:我们将Counter转换成一个模板，并且每个使用Counter的类都用它自己作为模板参数来实例化模板。

我再说一遍。**计数器成为模板**:

```CPP
template<typename T>
class Counter {
public:
    Counter() { ++count; }
    Counter(const Counter&) { ++count; }
    ~Counter() { --count; }

    static size_t howMany()
    { return count; }

private:
    static size_t count;
};

template<typename T>
size_t
Counter<T>::count = 0; // this now can go in header
```

第一种可选的使用方式可以这样：
```CPP
// embed a Counter to count objects
class Widget {
public:
    .....
    static size_t howMany()
    {return Counter<Widget>::howMany();}
private:
    .....
    Counter<Widget> c;
};
```

第二种就像这样：

```CPP
// inherit from Counter to count objects
class Widget: public Counter<Widget> {
    .....
};
```

注意，在这两种情况下，我们如何使用`Counter<Widget>`替换`Counter`。如前所述，每个使用Counter的类都以自身作为参数实例化模板。Jim Coplien首先公开了这样一种策略:通过传递自身作为模板参数来实例化模板供自己使用。他展示了它在许多语言中使用(不仅仅是c++)，并将其称为“a curiously recurring template pattern”[1]。我不认为Jim是有意的，但是他对模式的描述已经成为了它的名字。这太糟糕了，因为模式名称很重要，而这个名称不能传递关于它做什么或如何使用它的信息。模式的命名和其他任何东西一样都是艺术，我不太擅长它，但是我可能会把这个模式称为“Do It For Me”之类的东西。基本上，从计数器生成的每个类都为请求计数器实例化的类提供服务(它计算存在多少对象)。因此类`Counter<Widget>`计数Widget，而类`Counter<ABCD>`计数ABCD。

现在Counter是一个模板，"embed"设计方式和“inherit”设计方式都可以工作，因此我们可以评估它们的相对优势和劣势。我们的设计标准之一是客户端应该很容易获得对象计数功能，上面的代码表明基于继承的设计比基于嵌入的设计更容易。这是因为前者只需要将Counter作为基类提出来，而后者则需要定义一个计数器数据成员，并且客户机需要重新实现`howmany`成员来调用Counter的`howmany`[2]。这不是很多额外的工作(客户机howManys是简单的内联函数)，但是做一件事显然要比必须做两件事容易。因此，让我们首先将注意力转向使用继承的设计。

## Using Public Inheritance

基于继承的设计是可行的，因为c++保证每次构造或销毁派生类对象时，它的基类部分也将**首先构造，最后销毁**。因此，使Counter成为基类可以确保每当从其继承的类创建或销毁对象时，都会调用计数器构造函数或析构函数。

但是，每当基类的主题出现时，虚拟析构函数的主题也会出现。Counter类是否应该有一个虚析构函数?c++面向对象设计的既定原则要求它应该这样做。如果它没有虚拟析构函数，通过基类指针删除派生类对象会产生未定义的(通常是不希望的)结果:

```CPP
class Widget: public Counter<Widget>
{ ... };
Counter<Widget> *pw =
    new Widget;  // get base class ptr
                 // to derived class object
......
delete pw; // yields undefined results
           // if the base class lacks
           // a virtual destructor
```

这种行为违反了我们的标准，即对象计数设计本质上是万无一失的，因为上面的代码没有任何不合理之处。这是给Counter一个虚拟析构函数的有力论据。


然而，另一个标准是最大效率(没有对计数对象施加不必要的速度或空间惩罚)，现在我们遇到了麻烦。麻烦在于,因为存在一个虚拟析构函数，对于Counter来说意味着每个Counter类型的对象(或一个派生类对象)将包含一个虚表指针。如果Widget本身没有虚函数[3]的话，这意味着继承Counter将增加Widget的大小。我们不想那样。

避免它的唯一方法是防止客户端通过基类指针删除派生类对象（这样的话我们就没有了对虚析构函数的需求）。实现这一目的的合理方法似乎是在Counter中声明私有运算符`delete`:

```CPP
template<typename T>
class Counter {
public:
    .....
private:
    void operator delete(void*);
    .....
};
```

此时下面的语句不能通过编译。

```CPP
class Widget: public Counter<Widget> { ... };
Counter<Widget> *pw = new Widget;  ......
delete pw; // Error. Can't call private
// operator delete
```

不幸的是——这是真正有趣的部分——`new`表达式也不应该编译!
```CPP
Counter<Widget> *pw =
    new Widget;  // this should not
                 // compile because
                 // operator delete is
                 // private
```

还记得我在前面讨论new、delete和异常时提到，如果后续的构造函数调用失败，c++的运行时系统负责释放由操作员new分配的内存。还记得吗，操作符delete是执行回收的函数。但是我们在Counter中声明了私有运算符 delete ，这使得通过new在堆上创建对象变得无效!是的，这是违反直觉的，如果编译器还不支持这个规则，不要感到惊讶，但是我所描述的行为是正确的。此外，没有其他明显的方法可以防止通过Counter指针删除派生类对象，而且我们已经拒绝了计数器中的虚拟析构函数的概念。**因此，我建议放弃这种设计，转而使用计数器数据成员。**

## Using a Data Member

我们已经看到基于计数器数据成员的设计有一个缺点:客户机必须定义计数器数据成员并编写调用计数器的howMany函数的内联版本howMany。这比我们希望强加给客户的工作量稍微多一点，但也不是不可管理的。然而，还有另一个缺点。向类中添加计数器数据成员通常会增加该类类型的对象的大小。

乍一看，这算不上什么启示。毕竟，向类中添加数据成员会使这种类型的对象变大，这有多么令人惊讶呢? 但这事可能没你想的那么简单。看看计数器的定义:

```CPP
template<typename T>
class Counter {
public:
    Counter();
    Counter(const Counter&);
    ~Counter();

    static size_t howMany();
private:
    static size_t count;
};
```

注意，它没有非静态数据成员。这意味着Counter类型的每个对象不包含任何内容。我们是否希望计数器类型的对象的大小为0 ?我们可以，但这对我们没有好处。c++在这一点上非常清楚。所有对象的大小至少为一个字节，即使对象没有非静态数据成员。根据定义，sizeof将为从Counter模板实例化的每个类返回正数。因此，每个包含Counter对象的客户端类将比不包含Counter的客户端类包含更多的数据。

(有趣的是，这并不意味着有Counter的类的大小一定比不包含Counter的相同类的大小大。这是因为可能会涉及到对齐限制。例如，如果Widget是一个类，它包含两个字节的数据，但是需要四个字节对齐，那么Widget类型的每个对象将包含两个字节的填充，并且sizeof(Widget)将返回4。如果编译器通过在Counter中插入一个char来满足对象大小至少为1的要求，那么即使Widget包含Counter对象，sizeof(Widget)仍然可能生成4。该对象将简单地替换Widget已经包含的填充字节之一。然而，这并不是一个非常常见的场景，在设计打包对象计数功能的方法时，我们当然不能对其进行计划。

## Using Private Inheritance

再重新回头看看基于继承的代码，这导致需要考虑计数器中的虚拟析构函数:

```CPP
class Widget: public Counter<Widget>
{ ... };
Counter<Widget> *pw = new Widget;
......
delete
pw;  // yields undefined results
     // if Counter lacks a virtual
     // destructor
```

早些时候，我们试图通过阻止delete表达式编译来阻止这个操作序列，但是我们发现这也导致了`new`表达式的编译。但我们还可以曲线救国。我们可以禁止将`Widget*`指针(这是new返回的)隐式转换为`Counter<Widget>*`指针。换句话说，我们可以防止派生类指针向基类指针的隐式转换，我们所要做的就是用私有继承代替公共继承：

```CPP
class Widget: private Counter<Widget>
{ ... };
Counter<Widget> *pw =
    new Widget;  // error! no implicit
                 // conversion from
                 // Widget* to
                 // Counter<Widget>*
```

此外，我们可能会发现，与Widget的自身的大小相比，使用Counter作为基类不会增加Widget的大小。是的，我知道我刚刚告诉你没有一个类是零大小的，但是，这不是我想表达的意思。我说的是没有对象是零大小的。c++标准明确指出，派生对象的基类部分的大小可能为零。事实上，许多编译器实现了所谓的**空基优化** ( empty base optimization ) [4]。


因此，如果Widget包含Counter，则Widget的大小有增无减，Counter数据成员本身就是一个对象，因此它必须具有非零大小。但是如果Widget从Counter继承，编译器可以保持Widget的大小与以前相同。这为空间紧张且涉及空类的设计提供了一条有趣的经验法则:**当两者都可以使用时，优先考虑私有继承而非组合**。

最后这个设计几乎是完美的。如果编译器实现了空基优化，则它满足效率标准，因为从Counter继承不会向继承类中添加每个对象的数据，而且所有计数器成员函数都是内联的。它实现了万无一失的标准，因为计数操作是由计数器成员函数自动处理的，这些函数是由c++自动调用的，并且私有继承的使用防止了隐式转换（隐式转换允许将派生类对象当作基类对象来操作）。(好吧，这并不是万无一失的:Widget的作者可能会愚蠢地用Widget以外的类型实例化计数器，例如`Counter<Gidget>`。对于这种可能性，我选择视而不见。）


这个设计对于客户来说当然很容易使用，但是有些人可能会抱怨说它本可以更容易使用。私有继承的使用意味着有多少类在继承类时将成为私有的，因此此类类必须包含一个using声明，以使有多少类对其客户端公开:

```CPP
class Widget: private Counter<Widget> {
public:
    // make howMany public
    using Counter<Widget>::howMany;

    ..... // rest of Widget is unchanged
};

class ABCD: private Counter<ABCD> {
public:
    // make howMany public
    using Counter<ABCD>::howMany;

    ..... // rest of ABCD is unchanged
};
```
对于不支持名称空间的编译器，也可以通过使用旧的(现在已弃用)访问声明替换using声明来实现同样的事情:

```CPP
class Widget: private Counter<Widget> {
public:
    // make howMany public
    Counter<Widget>::howMany;

    .....  // rest of Widget is unchanged
};
```

因此，需要对自己的对象计数的客户类以及想要使计数作为自身接口的一部分的客户类必须做两件事:将Counter声明为基类，并使`howmany`[5]是可访问的。


然而，使用继承确实会导致两个值得注意的情况。首先是**二义性**。假设我们希望对Widget进行计数，并且希望计数可用于更一般的用途。如上所示，我们从Counter继承了Widget，并在Widget中提供了共有的`howmany`。现在假设我们有一个从Widget共有继承的类SpecialWidget，并且我们希望为SpecialWidget客户提供Widget客户喜欢的相同功能。没问题，我们只是让SpecialWidget从Counter继承。

此时二义性出现了。SpecialWidget应该提供哪个`howmany`？从Widget继承的还是从Counter继承的? 当然，我们真正想要的是来自Counter的那个，但是如果不真的在代码中显式写出SpecialWidget::howMany，就无法确保这一点。幸运的是，它是一个简单的内联函数:

class SpecialWidget: public Widget,
    private Counter<SpecialWidget> {
public:
    .....
    static size_t howMany()
    { return Counter<SpecialWidget>::howMany(); }
    .....
};

关于使用继承来计数对象的第二个观察结果是，从Widget::howMany返回的值不仅包括Widget对象的数量，还包括从Widget派生的类的对象。如果Widget派生的惟一类是SpecialWidget，并且有5个独立的Widget对象和3个独立的SpecialWidget，那么Widget::howMany将返回8个。毕竟，构建每个SpecialWidget还需要构建基本Widget部件。

## summary
以下几点是你需要记住的:
- 自动计数对象并不困难，但也不是完全简单。使用“Do It For Me”模式(Coplien的“a curiously recurring template pattern”)可以生成正确数量的计数器。使用私有继承可以在不增加对象大小的情况下提供对象计数功能。
- 当客户端可以选择继承空类还是包含此类对象的对象作为数据成员时，私有继承的实现方式更可取，因为它允许更紧凑的对象。
- 因为c++在堆对象构造失败时尽量避免内存泄漏，所以需要访问操作符new的代码通常也需要访问相应的操作符delete。
- Counter类模板并不关心您是继承它还是包含它的类型的对象。不管怎样，它看起来是一样的。因此,客户可以自由选择继承或组合,甚至在一个应用程序的不同部分使用不同的策略。

## Notes and References

[1] James O. Coplien. "The Column Without a Name: A Curiously Recurring Template Pattern," C++ Report, February 1995.

[2] An alternative is to omit `Widget::howMany` and make clients call `Counter<Widget>::howMany` directly. For the purposes of this article, however, we'll assume we want howMany to be part of the Widget interface.

[3] Scott Meyers. More Effective C++ (Addison-Wesley, 1996), pp. 113-122.

[4] Nathan Myers. "The Empty Member C++ Optimization," Dr. Dobb's Journal, August 1997. Also available at http://www.cantrip.org/emptyopt.html.

[5] Simple variations on this design make it possible for Widget to use `Counter<Widget>` to count objects without making the count available to Widget clients, not even by calling `Counter<Widget>::howMany` directly. Exercise for the reader with too much free time: come up with one or more such variations.
