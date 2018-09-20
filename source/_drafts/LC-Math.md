

### 415. Add Strings

### 728. Self Dividing Numbers

### 231. Power of Two

### 69. Sqrt(x) *(bangbang)*
使用牛顿法求解 $$$f(x)=0$$$ 问题，这里的$$$f(x)=x^2-a$$$，这里的$$$a$$$就是问题的输入。因此根据牛顿法迭代公式：
$$x=x-\frac{f(x)}{f'(x)}$$
得到该问题的求解公式：
$$x=\frac{1}{2}(x+\frac{a}{x})$$
