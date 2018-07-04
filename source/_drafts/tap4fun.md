


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

from sklearn import preprocessing
from sklearn.model_selection import learning_curve, cross_val_score
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve, auc
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier as GBC
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.decomposition import TruncatedSVD

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

def compute_scores(X, method):
    if method == 'pca':
        pca = PCA(svd_solver='full')
        pca_scores = []
        for n in n_components:
            pca.n_components = n
            pca_scores.append(np.mean(cross_val_score(pca, X)))
        return pca_scores



def preprocessPara():
    global header, coltype, train
    global assets_column, soldiers_column, special_column, bd_column, sr_column, pv_column, imp_column, all_column

    header = subprocess.getoutput('head -1 tap_fun_train.csv')[1:].split(",")
    header = header[:1] + header[2:] # drop register_time

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


    train = pd.read_csv("tap_fun_train.csv",  dtype=coltype, usecols=header, index_col='user_id', nrows=2)
    assets_column = train.columns[0:10]
    soldiers_column = train.columns[10:22]
    special_column = train.columns[22:32]
    bd_column = train.columns[32:48]
    sr_column = train.columns[48:97]
    pv_column = train.columns[97:103]
    imp_column = train.columns[103:106]
    all_column = assets_column.append(soldiers_column).append(special_column).append(bd_column).append(sr_column).append(pv_column).append(imp_column)

def preprocessData(filename, zero_index):
    train = pd.read_csv(filename,  dtype=coltype, usecols=header, index_col='user_id', skiprows=lambda x: zero_index[x-1])
    assert np.sum(get_zero_index(train)) == 0
    y = train.prediction_pay_price
    target = (y > 0).astype("int8") 
    train.drop(['prediction_pay_price'], axis=1, inplace=True)
    return train, y, target

def get_zero_index(data):
    zero_index = np.all(data[assets_column.append(imp_column)]==0, axis=1)
    return zero_index

def featuresImportance(model):
    feat_imp = pd.Series(model.feature_importances_, all_column).sort_values(ascending=False)
    feat_imp.plot(kind='bar', title='Feature Importances')
    plt.ylabel('Feature Importance Score')
    plt.show()



preprocessPara()

try:
    zero_index = joblib.load("zero_index.pkl")
except FileNotFoundError as e:
    data = pd.read_csv("tap_fun_train.csv",  dtype=coltype, usecols=header, index_col='user_id')
    zero_index = get_zero_index(data)
    #joblib.dump(zero_index, "zero_index.pkl")

train, y, target = preprocessData("tap_fun_train.csv", zero_index)
vali_zero_index = get_zero_index(pd.read_csv("tap_fun_validation.csv",  dtype=coltype, usecols=header, index_col='user_id'))
vali, vali_y, vali_target = preprocessData("tap_fun_validation.csv", vali_zero_index)


# ------------------------------pipeline 1--------------------------------------
pay_scaler = preprocessing.MinMaxScaler()
X = pay_scaler.fit_transform(train)
#joblib.dump(pay_scaler, "pay_scaler.pkl")

pay_clf = ExtraTreesClassifier(n_estimators=10, max_depth=None, min_samples_split=2, random_state=0)
pay_clf = LR(class_weight='balanced', verbose=1)
pay_clf = ExtraTreesClassifier(n_estimators=10, max_depth=None, min_samples_split=20, random_state=0, class_weight="balanced", verbose=1, max_features=10)

# 尝试自动估计GBM最优参数

param = dict(learning_rate=0.1, min_samples_split=500, min_samples_leaf=50, max_depth=8, max_features='sqrt', subsample=0.8, random_state=0)


param_test1 = {'n_estimators':range(20,81,10)}
param_test2 = {'max_depth':range(5,16,2), 'min_samples_split':range(200,1001,200)}
param_test3 = {'min_samples_leaf':range(30,71,10)}
param_test4 = {'max_features':range(7,20,2)}
param_test5 = {'subsample':[0.6,0.7,0.75,0.8,0.85,0.9]}

gsearch1 = GridSearchCV(estimator = GBC(**param), param_grid = param_test1, scoring='roc_auc',n_jobs=4,iid=False, cv=5, verbose=1)
gsearch1.fit(X, target)
print(gsearch1.best_params_, gsearch1.best_score_)

param.update(gsearch1.best_params_)
for i in param_test2.keys():
    param.pop(i)

gsearch2 = GridSearchCV(estimator = GBC(**param), param_grid = param_test2, scoring='roc_auc',n_jobs=4,iid=False, cv=5, verbose=1)
gsearch2.fit(X, target)
print(gsearch2.best_params_, gsearch2.best_score_)


gsearch3 = GridSearchCV(estimator = GBC(learning_rate=0.2, n_estimators=60,max_depth=9,max_features='sqrt', subsample=0.8, random_state=10, min_samples_split=800), param_grid = param_test3, scoring='roc_auc',n_jobs=4,iid=False, cv=5)
gsearch3.fit(X, target)
print(gsearch3.best_params_, gsearch3.best_score_)


gsearch4 = GridSearchCV(estimator = GBC(learning_rate=0.2, n_estimators=60,max_depth=9, min_samples_split=800, min_samples_leaf=50, subsample=0.8, random_state=10),
param_grid = param_test4, scoring='roc_auc',n_jobs=4,iid=False, cv=5)
gsearch4.fit(X, target)
print(gsearch4.best_params_, gsearch4.best_score_)


gsearch5 = GridSearchCV(estimator = GBC(learning_rate=0.2, n_estimators=60,max_depth=9,min_samples_split=800, min_samples_leaf=50, random_state=10,max_features=15),
param_grid = param_test5, scoring='roc_auc',n_jobs=4,iid=False, cv=5)
gsearch5.fit(X, target)
print(gsearch5.best_params_, gsearch5.best_score_)

pay_clf.fit(X, target)
#joblib.dump(pay_clf, "pay_clf.pkl")
pred = pay_clf.predict(X)
vali_pred = pay_clf.predict(pay_scaler.transform(vali))
accuracy_score(pred, target)
accuracy_score(vali_pred, vali_target)
confusion_matrix(vali_target, vali_pred, [1,0])


 



# ------------------------------pipeline 2--------------------------------------
# 大佬用户分类模型(大佬：潜在7～45内持续消费的人。非大佬消费者：7天内消费完不再消费了。)
# 在45天内会消费的预测用户中找大佬，而不是在45天内会消费的真实用户中找大佬
payuser_X = train[pred==1].copy()
payuser_y = y[pred==1].copy()
dalao_index = y[pred==1] > payuser_X.pay_price # bool index
#for i in range(1,20):
#      print(payuser_X[dalao_index].iloc[i:i+1,:].pay_price)
#      print(y[pred==1][dalao_index][i:i+1])
#      print()
dalao_target = dalao_index.astype("int8")
dalao_scaler1 = preprocessing.StandardScaler()
payuser_X = dalao_scaler1.fit_transform(payuser_X)
joblib.dump(dalao_scaler1, "dalao_scaler1.pkl")



# 数据少了，先降维
n_components = [10,20,30,50,60,65,75,80]
pca_scores = compute_scores(payuser_X, 'pca')
pca = PCA(n_components= n_components[np.argmax(pca_scores)], whiten=True)

# 可视化降维结果
# plt.plot(n_components,pca_scores); plt.show()
reduced_payuser_X = pca.fit_transform(payuser_X)
joblib.dump(pca, "dalao_reducer1.pkl")

# 采用GBM模型进行分类，进行参数搜索
# GBM参数调优
param = dict(learning_rate=0.1, min_samples_split=500,min_samples_leaf=50,max_depth=8,max_features='sqrt',subsample=0.8,random_state=10)

param_test1 = {'n_estimators':range(20,81,10)}
gsearch1 = GridSearchCV(estimator = GBC(**param), param_grid = param_test1, scoring='roc_auc',n_jobs=4,iid=False, cv=5)
gsearch1.fit(reduced_payuser_X, dalao_target)
print(gsearch1.best_params_, gsearch1.best_score_)

param_test2 = {'max_depth':range(5,16,2), 'min_samples_split':range(200,1001,200)}
gsearch2 = GridSearchCV(estimator = GBC(learning_rate=0.2, n_estimators=60, max_features='sqrt', subsample=0.8, random_state=10), param_grid = param_test2, scoring='roc_auc',n_jobs=4,iid=False, cv=5)
gsearch2.fit(reduced_payuser_X, dalao_target)
print(gsearch2.best_params_, gsearch2.best_score_)

param_test3 = {'min_samples_leaf':range(30,71,10)}
gsearch3 = GridSearchCV(estimator = GBC(learning_rate=0.2, n_estimators=60,max_depth=9,max_features='sqrt', subsample=0.8, random_state=10, min_samples_split=800), param_grid = param_test3, scoring='roc_auc',n_jobs=4,iid=False, cv=5)
gsearch3.fit(reduced_payuser_X, dalao_target)
print(gsearch3.best_params_, gsearch3.best_score_)

param_test4 = {'max_features':range(7,20,2)}
gsearch4 = GridSearchCV(estimator = GBC(learning_rate=0.2, n_estimators=60,max_depth=9, min_samples_split=800, min_samples_leaf=50, subsample=0.8, random_state=10),
param_grid = param_test4, scoring='roc_auc',n_jobs=4,iid=False, cv=5)
gsearch4.fit(reduced_payuser_X, dalao_target)
print(gsearch4.best_params_, gsearch4.best_score_)

param_test5 = {'subsample':[0.6,0.7,0.75,0.8,0.85,0.9]}
gsearch5 = GridSearchCV(estimator = GBC(learning_rate=0.2, n_estimators=60,max_depth=9,min_samples_split=800, min_samples_leaf=50, random_state=10,max_features=15),
param_grid = param_test5, scoring='roc_auc',n_jobs=4,iid=False, cv=5)
gsearch5.fit(reduced_payuser_X, dalao_target)
print(gsearch5.best_params_, gsearch5.best_score_)


dalao_clf = GBC(learning_rate=0.01, n_estimators=1500,max_depth=9,min_samples_split=800, min_samples_leaf=50, random_state=10,max_features=15, subsample=0.8)
# cross_val_score(estimator=dalao_clf, X=reduced_payuser_X, y=dalao_target, cv=5, n_jobs=4, verbose=True, scoring="roc_auc")
dalao_clf.fit(reduced_payuser_X, dalao_target)
dalao_pred = dalao_clf.predict(reduced_payuser_X)
accuracy_score(dalao_pred, dalao_target)
joblib.dump(dalao_clf, "dalao_clf.pkl")

# 对大佬的目标值建立回归模型，这部分还可以仔细打磨
dalao_scaler2 = preprocessing.MinMaxScaler()
dalao_X = dalao_scaler2.fit_transform(payuser_X[dalao_index])
joblib.dump(dalao_scaler2, "dalao_scaler2.pkl")
dalao_y = payuser_y[dalao_index]
pca = PCA(n_components= n_components[np.argmax(pca_scores)])
reduced_dalao_X = pca.fit_transform(dalao_X)
joblib.dump(dalao_reducer2, "dalao_reducer2.pkl")

# 先随便试试一个简单的模型
# 就用的岭回归



# 进行预测
def answer(inputfile, persistence=True):
    question = pd.read_csv(inputfile,  dtype=coltype, usecols=header[:-1], index_col='user_id')
    question_zero_index = (question[assets_column.append(imp_column)]==0).all(axis=1)
    answer = pd.Series(index=question.index)
    answer[question_zero_index] = 0
    question = pd.read_csv(inputfile,  dtype=coltype, usecols=header[:-1], index_col='user_id', skiprows=lambda x: question_zero_index.values[x-1])

    # 对于是否氪金的分类，加载scaler与clf
    pay_clf = joblib.load("pay_clf.pkl")
    pay_scaler = joblib.load("pay_scaler.pkl")
    question_X = pd.DataFrame(pay_scaler.transform(question),  columns=train.columns, index=question.index)
    pay_pred_answer = pd.Series(pay_clf.predict(question_X), index=question.index)
    answer[pay_pred_answer[pay_pred_answer == 0].index] = 0

    # 对于是否大佬的分类，加载scaler、clf和reducer，后面优化为pipeline
    question_payuser = question[pay_pred_answer == 1].copy()
    dalao_clf = joblib.load("dalao_clf.pkl")
    dalao_scaler1 = joblib.load("dalao_scaler1.pkl")
    dalao_reducer1 = joblib.load("dalao_reducer1.pkl")
    dalao_pred_answer = dalao_clf.predict(dalao_reducer1.transform(dalao_scaler1.transform(question_payuser)))
    dalao_pred_answer = pd.Series(dalao_pred_answer, index=question_payuser.index)
    answer[dalao_pred_answer[dalao_pred_answer == 0].index] = question_payuser[dalao_pred_answer == 0].pay_price

    # 对于大佬进行数值预测
    question_dalao = question_payuser[dalao_pred_answer == 1].copy()
    model = joblib.load("model.pkl")
    dalao_scaler2 = joblib.load("dalao_scaler2.pkl")
    dalao_reducer2 = joblib.load("dalao_reducer2.pkl")
    dalao_pred_answer = model.predict(dalao_reducer2.transform(dalao_scaler2.transform(question_dalao)))
    dalao_pred_answer = pd.Series(dalao_pred_answer, index=question_dalao.index)
    dalao_pred_answer[dalao_pred_answer < 0] = 0
    answer[answer.isna()] = dalao_pred_answer

    if persistence:
        answer.name = 'prediction_pay_price'
        answer.to_csv("answer_20180702.csv", header=True, encoding='utf8', index=True)
    else:
        return answer

def validation(inputfile):
    pred_answer = answer("tap_fun_validation.csv", persistence=False)
    standard_answer = pd.read_csv("tap_fun_validation.csv",  dtype=coltype, usecols=header[:1]+header[-1:], index_col='user_id')
    return mse(pred_answer, standard_answer) ** 0.5
```


探索过程
```python
# 查看这些人花钱最多的前十个人花了多少钱
# 确认可以不考虑，剥离掉这部分用户的影响
zero_train = train[zero_index].prediction_pay_price
bottleneck.partition(zero_train.values, kth=len(zero_train)-10)[len(zero_train)-10:]



train_sizes, train_scores, validation_scores = learning_curve(
                                                   estimator = ExtraTreesClassifier(n_estimators=10, max_depth=None, min_samples_split=2, random_state=0), 
                                                   X = X,
                                                   y = target, 
                                                   train_sizes = [10,100,1000,10000,100000,500000,1000000,1815501], 
                                                   cv = 5,
                                                   scoring = 'accuracy')



plot_learning_curve(train_sizes, train_scores, validation_scores)
print(cross_val_score(clf, X, target)) # array([0.99738915, 0.99767337, 0.99753985])

# 查看pay_clf分类结果
index = np.array(list(map(lambda x:x[0], filter(lambda x:x[1]==True, enumerate(pred==1)))))
for i in index:
     print(i)
     print(train.iloc[i,:][['pay_price','pay_count','prediction_pay_price']])
     if i > 500 :
         break
```



[简单又实用的pandas技巧：如何将内存占用降低90%](https://www.jiqizhixin.com/articles/2018-03-07-3)
[在 Python 中高效堆叠模型](https://www.jiqizhixin.com/articles/2018-01-14-8)
[利用学习曲线诊断模型的偏差和方差](https://www.jiqizhixin.com/articles/2018-01-23)
[](https://blog.csdn.net/han_xiaoyang/article/details/52663170)
