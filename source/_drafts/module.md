
## 10.1 构建一个模块的层级包
封装成包是很简单的。在文件系统上组织你的代码,并确保每个目录都定义了一个 `__init__.py` 文件。
```bash
mytools/
├── datastructure
│   ├── Indexheap.py
│   ├── __init__.py
│   ├── rbtree.py
│   ├── treetools.py
│   └── unionfind.py
├── __init__.py
├── Q_rsqrt.py
└── sample
    ├── gaussian_sampling.py
    ├── gibbs_sampling_BayesNet.py
    ├── gibbs_sampling.py
    ├── __init__.py
    ├── metropolis_hastings.py
    ├── reject_sampling.py
    └──  roulette_sampling.py
```

此时：

- [x] 支持`import mytools`
- [ ] 在上一句的基础上支持`mytools.datastructure`
- [x] 支持`from mytools import datastructure`
- [x] 在上一句的基础上支持`mytools.datastructure`
- [ ] 支持`from mytools.sample import gaussian_sampling`

## 10.2 控制模块被全部导入的内容
在`module.py`文件中加入`__all__`列表。

