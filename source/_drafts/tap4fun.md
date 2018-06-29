


# 数据探索性分析


# 优化数据存储

```python
import matplotlib
matplotlib.use('Agg')


import bottleneck
import pandas as pd
import numpy as np
import subprocess
from collections import ChainMap
from matplotlib import pyplot as plt
from sklearn.externals import joblib

# 一些工具函数
def plot_learning_curve(train_sizes, train_scores, test_scores):
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    plt.show()


header = subprocess.getoutput('head -1 tap_fun_train.csv')[1:].split(",")
header = header[2:] # drop user_id and register_time

# 根据预处理脚本得到每个字段的最大值确定其数据类型
coltype = dict(ChainMap(
    {i:"uint8" for i in filter(lambda x:x.endswith("level"), header)},
    {i:"uint16" for i in filter(lambda x:x.endswith("count"), header)},
    {i:"uint32" for i in filter(lambda x:x.endswith("value"), header)}
))
coltype['avg_online_minutes'] = 'float32' # 防止精度太低没用float16
coltype['pay_price'] = 'float32'
coltype['prediction_pay_price'] = 'float32'
coltype['user_id'] = 'uint32'


train = pd.read_csv("tap_fun_train.csv",  dtype=coltype, usecols=header, nrows=10)
assets_index = train.columns[0:10]
soldiers_index = train.columns[10:22]
special_index = train.columns[22:32]
bd_index = train.columns[32:48]
sr_index = train.columns[48:97]
pv_index = train.columns[97:103]
imp_index = train.columns[103:106]
all_index = assets_index.append(soldiers_index).append(special_index).append(bd_index).append(sr_index).append(pv_index).append(imp_index)
# zero_index 是前七天啥都没干的人的索引
# zero_index = np.all(train[all_index]==0, axis=1)
zero_index = np.all(train[assets_index.append(imp_index)]==0, axis=1)
zero_train = train[zero_index].prediction_pay_price
# 查看这些人花钱最多的前十个人花了多少钱
zero_train = train[zero_index].prediction_pay_price
bottleneck.partition(zero_train.values, kth=len(zero_train)-10)[len(zero_train)-10:]
# 确认可以不考虑，剥离掉这部分用户的影响

#useful_index = np.not_equal(np.array([True]*len(zero_index)), zero_index)
#features_std = train[useful_index].std()
#features_std = np.array(sorted(zip(features_std.index.tolist(), features_std.tolist()), key=lambda x:x[1]))

# del train
zero_index = joblib.load("zero_index.pkl")
train = pd.read_csv("tap_fun_train.csv",  dtype=coltype, usecols=header, skiprows=lambda x: zero_index[x-1])
y = train.prediction_pay_price
train.drop(['prediction_pay_price'], axis=1, inplace=True)


# 特征规格化
from sklearn import preprocessing
scaler = preprocessing.MinMaxScaler()
X = scaler.fit_transform(train)
target = (y > 0).astype("int8")

# 氪金用户分类模型部分
from sklearn.model_selection import learning_curve, cross_val_score
from sklearn.ensemble import ExtraTreesClassifier

clf = ExtraTreesClassifier(n_estimators=10, max_depth=None, min_samples_split=2, random_state=0)
train_sizes, train_scores, validation_scores = learning_curve(
                                                   estimator = ExtraTreesClassifier(n_estimators=10, max_depth=None, min_samples_split=2, random_state=0), 
                                                   X = X,
                                                   y = target, 
                                                   train_sizes = [10,100,1000,10000,100000,500000,1000000,1815501], 
                                                   cv = 5,
                                                   scoring = 'accuracy')



plot_learning_curve(train_sizes, train_scores, validation_scores)

scores = cross_val_score(clf, X, target)
print(scores) # array([0.99738915, 0.99767337, 0.99753985])
clf.fit(X, y)
# top 10 important features
print(sorted(zip(header,feature_importances_), key = lambda x:x[1])[-10:]) 
# classification model accuracy : 0.9998
accuracy_score(clf.predict(X), target) 

pred = clf.predict(X)
index = np.array(list(map(lambda x:x[0], filter(lambda x:x[1]==True, enumerate(pred==1)))))
# 查看分类结果
for i in index:
     print(i)
     print(train.iloc[i,:][['pay_price','pay_count','prediction_pay_price']])
     if i > 500 :
         break


# 大佬用户分类模型(大佬：潜在7～45内持续消费的人。非大佬消费者：7天内消费完不再消费了。)
# 在45天内会消费的预测用户中找大佬，而不是在45天内会消费的真实用户中找大佬
payuser_X = train[pred==1].copy()
dalao_index = y[pred==1] > payuser_X.pay_price # bool index
for i in range(1,20):
      print(payuser_X[dalao_index].iloc[i:i+1,:].pay_price)
      print(y[pred==1][dalao_index][i:i+1])
      print()
dalao_target = dalao_index.astype("int8")
```



[简单又实用的pandas技巧：如何将内存占用降低90%](https://www.jiqizhixin.com/articles/2018-03-07-3)
[在 Python 中高效堆叠模型](https://www.jiqizhixin.com/articles/2018-01-14-8)
[利用学习曲线诊断模型的偏差和方差](https://www.jiqizhixin.com/articles/2018-01-23)
