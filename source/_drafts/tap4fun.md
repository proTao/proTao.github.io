


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

def compute_scores(X):
    pca = PCA(svd_solver='full')

    pca_scores = []
    for n in n_components:
        pca.n_components = n
        pca_scores.append(np.mean(cross_val_score(pca, X)))

    return pca_scores

def modelfit(alg, X, y, performCV=True, printFeatureImportance=True, cv_folds=5):
    #Fit the algorithm on the data
    alg.fit(dtrain[predictors], dtrain['Disbursed'])

    #Predict training set:
    dtrain_predictions = alg.predict(dtrain[predictors])
    dtrain_predprob = alg.predict_proba(dtrain[predictors])[:,1]

    #Perform cross-validation:
    if performCV:
        cv_score = cross_validation.cross_val_score(alg, dtrain[predictors], dtrain['Disbursed'], cv=cv_folds, scoring='roc_auc')

    #Print model report:
    print "\nModel Report"
    print "Accuracy : %.4g" % metrics.accuracy_score(dtrain['Disbursed'].values, dtrain_predictions)
    print "AUC Score (Train): %f" % metrics.roc_auc_score(dtrain['Disbursed'], dtrain_predprob)

    if performCV:
        print "CV Score : Mean - %.7g | Std - %.7g | Min - %.7g | Max - %.7g" % (np.mean(cv_score),np.std(cv_score),np.min(cv_score),np.max(cv_score))

    #Print Feature Importance:
    if printFeatureImportance:
        feat_imp = pd.Series(alg.feature_importances_, predictors).sort_values(ascending=False)
        feat_imp.plot(kind='bar', title='Feature Importances')
        plt.ylabel('Feature Importance Score')


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
pay_scaler = preprocessing.MinMaxScaler()
X = pay_scaler.fit_transform(train)
joblib.dump(pay_scaler, "pay_scaler.pkl")
target = (y > 0).astype("int8") # 支付的用户的目标值是1

# 氪金用户分类模型部分
from sklearn.model_selection import learning_curve, cross_val_score
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score


train_sizes, train_scores, validation_scores = learning_curve(
                                                   estimator = ExtraTreesClassifier(n_estimators=10, max_depth=None, min_samples_split=2, random_state=0), 
                                                   X = X,
                                                   y = target, 
                                                   train_sizes = [10,100,1000,10000,100000,500000,1000000,1815501], 
                                                   cv = 5,
                                                   scoring = 'accuracy')



plot_learning_curve(train_sizes, train_scores, validation_scores)

print(cross_val_score(clf, X, target)) # array([0.99738915, 0.99767337, 0.99753985])

pay_clf = ExtraTreesClassifier(n_estimators=10, max_depth=None, min_samples_split=2, random_state=0)
pay_clf.fit(X, target)
joblib.dump(pay_clf, "pay_clf.pkl")
# top 10 important features
# 这段图形化特征重要性的代码可以改善
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
payuser_y = y[pred==1].copy()
dalao_index = y[pred==1] > payuser_X.pay_price # bool index
for i in range(1,20):
      print(payuser_X[dalao_index].iloc[i:i+1,:].pay_price)
      print(y[pred==1][dalao_index][i:i+1])
      print()
dalao_target = dalao_index.astype("int8")
pay_scaler = preprocessing.MinMaxScaler()
payuser_X = pay_scaler.fit_transform(payuser_X)
joblib.dump(pay_scaler, "pay_scaler.pkl")
del pay_scaler


# 数据少了，先降维
from sklearn.decomposition import PCA
n_components = [30,50,60,65,75,80,85,90]
pca_scores = compute_scores(payuser_X)
# 可视化降维结果
# plt.plot(n_components,pca_scores); plt.show()
pca = PCA(n_components= n_components[np.argmax(pca_scores)])
reduced_payuser_X = pca.fit_transform(payuser_X)

# 采用GBM模型进行分类，进行参数搜索
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier as GBC

# GBM参数调优
param_test1 = {'n_estimators':range(20,81,10)}
gsearch1 = GridSearchCV(estimator = GBC(learning_rate=0.1, min_samples_split=500,min_samples_leaf=50,max_depth=8,max_features='sqrt',subsample=0.8,random_state=10), param_grid = param_test1, scoring='roc_auc',n_jobs=4,iid=False, cv=5)
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

# 对大佬的目标值建立回归模型
dalao_X = preprocessing.MinMaxScaler().fit_transform(payuser_X[dalao_index])
dalao_y = payuser_y[dalao_index]
pca = PCA(n_components= n_components[np.argmax(pca_scores)])
reduced_dalao_X = pca.fit_transform(dalao_X)

from sklearn.ensemble import GradientBoostingRegressor as GBR
param_test1 = {'n_estimators':range(20,81,10)}
gsearch1 = GridSearchCV(estimator = GBR(learning_rate=0.1, min_samples_split=500,min_samples_leaf=50, max_depth=8,max_features='sqrt',subsample=0.8,random_state=10), param_grid = param_test1, scoring='neg_mean_squared_error',n_jobs=4,iid=False, cv=5)
gsearch1.fit(reduced_dalao_X, dalao_y)
print(gsearch1.best_params_, gsearch1.best_scores_)

param_test2 = {'max_depth':range(5,16,2), 'min_samples_split':range(200,1001,200)}
gsearch2 = GridSearchCV(estimator = GBR(learning_rate=0.1, min_samples_leaf=50, n_estimators=70, max_features='sqrt',subsample=0.8,random_state=10), param_grid = param_test1, scoring='neg_mean_squared_error',n_jobs=4,iid=False, cv=5)
gsearch2.fit(reduced_dalao_X, dalao_y)
print(gsearch2.best_params_, gsearch2.best_scores_)

# 先随便试试一个简单的模型
# 就用的岭回归

# 进行预测
question = pd.read_csv("tap_fun_test.csv",  dtype=coltype, usecols=header[:-1])
question_zero_index = np.all(question[assets_index.append(imp_index)]==0, axis=1)
answer = pd.Series(index=question.index)
answer[question_zero_index] = 0
question = pd.read_csv("tap_fun_test.csv",  dtype=coltype, usecols=header[:-1], skiprows=lambda x: question_zero_index[x-1])

# 对于是否氪金的分类，加载scaler与clf
pay_clf = joblib.load("pay_clf.pkl")
pay_scaler = joblib.load("pay_scaler.pkl")
question = pd.DataFrame(pay_scaler.transform(question),  columns=train.columns)
pred = pay_clf.predict(question)

```



[简单又实用的pandas技巧：如何将内存占用降低90%](https://www.jiqizhixin.com/articles/2018-03-07-3)
[在 Python 中高效堆叠模型](https://www.jiqizhixin.com/articles/2018-01-14-8)
[利用学习曲线诊断模型的偏差和方差](https://www.jiqizhixin.com/articles/2018-01-23)
[](https://blog.csdn.net/han_xiaoyang/article/details/52663170)
