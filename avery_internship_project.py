import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()

from sklearn.model_selection import train_test_split

from sklearn.linear_model import LogisticRegression

from sklearn import metrics
from sklearn.metrics import confusion_matrix, classification_report,accuracy_score,precision_score,recall_score,f1_score

from sklearn import tree
from sklearn.tree import DecisionTreeClassifier

from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier

import scipy.stats as stats

from sklearn.model_selection import GridSearchCV


import warnings
warnings.filterwarnings('ignore')

hm=pd.read_csv("data.csv")

# Copying data to another variable to avoid any changes to original data
data=hm.copy()

cols = data.select_dtypes(['object']).columns.tolist()

#adding target variable to this list as this is an classification problem and the target variable is categorical
cols.append('Overdose')

# Changing the data type of object type column to category. hint use astype() function
for i in cols:
    data[i] = data[i].astype('category')

def treat_outliers(df,col):
    '''
    treats outliers in a varaible
    col: str, name of the numerical varaible
    df: data frame
    col: name of the column
    '''
    
    Q1=data[col].quantile(0.25) # 25th quantile
    Q3=data[col].quantile(0.75)  # 75th quantile
    IQR=Q3 - Q1   # IQR Range
    Lower_Whisker =  Q1 - 1.5*IQR  #define lower whisker
    Upper_Whisker = Q3 + 1.5 * IQR  # define upper Whisker
    df[col] = np.clip(df[col], Lower_Whisker, Upper_Whisker) # all the values samller than Lower_Whisker will be assigned value of Lower_whisker 
                                                            # and all the values above upper_whishker will be assigned value of upper_Whisker 
    return df

def treat_outliers_all(df, col_list):
    '''
    treat outlier in all numerical varaibles
    col_list: list of numerical varaibles
    df: data frame
    '''
    for c in col_list:
        df = treat_outliers(df,c)
        
    return df

df_raw = data.copy()

numerical_col = df_raw.select_dtypes(include=np.number).columns.tolist()# getting list of numerical columns

df = treat_outliers_all(df_raw,numerical_col)

def add_binary_flag(df,col):
    '''
    df: It is the dataframe
    col: it is column which has missing values
    It returns a dataframe which has binary falg for missing values in column col
    '''
    new_col = str(col)
    new_col += '_missing_values_flag'
    df[new_col] = df[col].isna()
    return df

missing_col = [col for col in df.columns if df[col].isnull().any()]

for colmn in missing_col:
    add_binary_flag(df,colmn)

# Drop the dependent variable from the dataframe and create the X(independent variable) matrix
X = data.drop(columns=['Overdose', 'Binary_Overdose'])

# Create dummy variables for the categorical variables - Hint: use the get_dummies() function
X = pd.get_dummies(X, drop_first=True)

# Create y(dependent varibale)
y = data['Binary_Overdose']

# Split the data into training and test set
X_train,X_test,y_train,y_test=train_test_split(X, y, test_size=0.30, random_state=1, stratify=y)

#creating metric function 
def metrics_score(actual, predicted):
    print(classification_report(actual, predicted))
    cm = confusion_matrix(actual, predicted)
    plt.figure(figsize=(8,5))
    sns.heatmap(cm, annot=True,  fmt='.2f', xticklabels=['No Overdose', 'Overdose'], yticklabels=['No Overdose', 'Overdose'])
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.show()

#Defining Decision tree model with class weights class_weight={0: 0.2, 1: 0.8}
dt = DecisionTreeClassifier(class_weight={0:0.2,1:0.8}, random_state=1)

#fitting Decision tree model
dt.fit(X_train, y_train)

# Checking performance on the training data based on the tuned model
y_train_pred_dt_ets=dt.predict(X_train)
metrics_score(y_train,y_train_pred_dt_ets)

# Checking performance on the testing data based on the tuned model
y_test_pred_dt_est=dt.predict(X_test)
metrics_score(y_test,y_test_pred_dt_est)

# Plot the decision  tree and analyze it to build the decision rule
features = list(X.columns)

plt.figure(figsize=(20,10))

tree.plot_tree(dt,feature_names=features,filled=True,fontsize=10,node_ids=True,class_names=True,max_depth=5)
plt.show()

# Choose the type of classifier. 
classifier = dt

# Grid of parameters to choose from
params = {'criterion': ['gini', 'entropy'], 'max_depth': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 'min_samples_leaf': [5, 10, 20, 25,30,35,40, 45, 50, 55, 60 ,65 ,70]}

# Type of scoring used to compare parameter combinations
score = metrics.make_scorer(recall_score, pos_label=1)

# Run the grid search
gs = GridSearchCV(dt, params, scoring=score)

# Fit the GridSearch on train dataset
gridCV = gs.fit(X_train, y_train)

# Set the clf to the best combination of parameters
dt = gridCV.best_estimator_

# Fit the best algorithm to the data. 
dt.fit(X_train, y_train)
print(dt)

# Checking performance on the training data based on the tuned model
y_train_pred_dt_tuned = dt.predict(X_train)
metrics_score(y_train,y_train_pred_dt_tuned)

# Checking performance on the testing data based on the tuned model
y_test_pred_dt_tuned = dt.predict(X_test)
metrics_score(y_test,y_test_pred_dt_tuned)

# Defining Random forest CLassifier
forest = RandomForestClassifier(n_estimators=100, random_state=100)
forest.fit(X_train,y_train)

#Checking performance on the training data
y_train_pred_rf = forest.predict(X_train)
metrics_score(y_train, y_train_pred_rf)

# Checking performance on the test data
y_test_pred_rf = forest.predict(X_test)
metrics_score(y_test, y_test_pred_rf)

# Defining Random Forest model with class weights class_weight={0: 0.2, 1: 0.8}
forest_cw = RandomForestClassifier(class_weight={0: 0.2, 1: 0.8})

# Fitting Random Forest model
forest_cw.fit(X_train, y_train)

# Checking performance on the train data
y_train_pred_rf_cw = forest.predict(X_train)
metrics_score(y_train, y_train_pred_rf_cw)

# Checking performance on the test data
y_test_pred_rf_cw = forest.predict(X_test)
metrics_score(y_test, y_test_pred_rf_cw)

# Choose the type of classifier. 
classifier = forest_cw


# Grid of parameters to choose from
params = {'n_estimators': [100, 200, 300], 'min_samples_split': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 'min_samples_leaf': [5, 10, 20, 25,30,35,40, 45, 50, 55, 60 ,65 ,70], 'max_features': ['auto', 'sqrt', 'log2', 'None']}


# Type of scoring used to compare parameter combinations
score = metrics.make_scorer(recall_score, pos_label=1)


# Run the grid search
gs = GridSearchCV(classifier, params, scoring=score, cv=5)


#fit the GridSearch on train dataset
gridCV = gs.fit(X_train, y_train)


# Set the clf to the best combination of parameters
forest_tuned = gridCV.best_estimator_


# Fit the best algorithm to the data. 
forest_tuned.fit(X_train, y_train)

# Checking performance on the training data
y_train_pred_rf_tuned = forest_tuned.predict(X_train)
metrics_score(y_train,y_train_pred_rf_tuned)

# Checking performace on test dataset
y_test_pred_rf_tuned = forest_tuned.predict(X_test)
metrics_score(y_test,y_test_pred_rf_tuned)

# importance of features in the tree building ( The importance of a feature is computed as the 
#(normalized) total reduction of the criterion brought by that feature. It is also known as the Gini importance )
# Checking performace on test dataset
importances = forest_tuned.feature_importances_
columns=X.columns
importance_df=pd.DataFrame(importances,index=columns,columns=['Importance']).sort_values(by='Importance',ascending=False)
plt.figure(figsize=(13,13))
sns.barplot(importance_df.Importance,importance_df.index)
