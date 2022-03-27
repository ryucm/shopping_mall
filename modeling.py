import psycopg2
import pandas as pd
from sklearn.model_selection import train_test_split

from category_encoders import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer 
from sklearn.pipeline import make_pipeline

con = psycopg2.connect(
    host = 'arjuna.db.elephantsql.com',
    database = 'jufgneai',
    user = 'jufgneai',
    password = 'GSJ9LWjCYj-1kKjmwpH4GaqdWl-ApwS0'
)

cur = con.cursor()
cur.execute('SELECT rank,brand_name,item_name,kind,price,recommend,period FROM rank')

cols = [column for column in cur.fetchall()]

temp = pd.DataFrame.from_records(data= cols, columns = ['rank','brand_name','item_name','kind','price','recommend','period'])
temp
def columns_engineering(f,period):
  f.rename(columns = {'rank':period},inplace= True)
  f.drop('period',axis = 1,inplace = True)
  return f

c1 = temp[temp['period'] == '1d']
c2 = temp[temp['period'] == '1w']
c3 = temp[temp['period'] == '1m']
c4 = temp[temp['period'] == '3m']
c5 = temp[temp['period'] == '1y']

columns_engineering(c1,'1d')
columns_engineering(c2,'1w')
columns_engineering(c3,'1m')
columns_engineering(c4,'3m')
columns_engineering(c5,'1y')

me = pd.merge(c1,c2, on = ['item_name','brand_name','price','kind','recommend'],how = 'outer')
me = pd.merge(me,c3, on = ['item_name','brand_name','price','kind','recommend'],how = 'outer')
me = pd.merge(me,c4, on = ['item_name','brand_name','price','kind','recommend'],how = 'outer')
me = pd.merge(me,c5, on = ['item_name','brand_name','price','kind','recommend'],how = 'outer')
raw_data = me[['brand_name', 'item_name', 'kind', 'price','recommend','1d', '1w', '1m', '3m','1y']].fillna(0)

#스테디셀러(5)
def steady_seller(f):
  raw_data = f.copy()
  raw_data['1y'] = raw_data['1y'].apply(lambda x: 0.2 if (x>0 and x <=20) else 0.1 if (x>20 and x<=50) else 0.05 if (x>50 and x<=100) else 0.02)
  raw_data['3m'] = raw_data['3m'].apply(lambda x: 0.2 if (x>0 and x <=20) else 0.1 if (x>20 and x<=50) else 0.05 if (x>50 and x<=100) else 0.02)
  raw_data['1m'] = raw_data['1m'].apply(lambda x: 0.2 if (x>0 and x <=20) else 0.1 if (x>20 and x<=50) else 0.05 if (x>50 and x<=100) else 0.02)
  raw_data['1w'] = raw_data['1w'].apply(lambda x: 0.2 if (x>0 and x <=20) else 0.1 if (x>20 and x<=50) else 0.05 if (x>50 and x<=100) else 0.02)
  raw_data['1d'] = raw_data['1d'].apply(lambda x: 0.2 if (x>0 and x <=20) else 0.1 if (x>20 and x<=50) else 0.05 if (x>50 and x<=100) else 0.02)
  f['score'] = raw_data.loc[:,'1d':'1y'].sum(axis = 1)
  return f

steady = steady_seller(raw_data)

train_steady, test_steady = train_test_split(steady, train_size=0.80, test_size=0.20, random_state=2)
train_steady, val_steady = train_test_split(train_steady, train_size=0.80, test_size=0.20, random_state=2)

features = ['brand_name','kind','recommend','1d','1w','1m','3m','1y']
target = 'price'
X_train_steady = train_steady[features]
y_train_steady = (train_steady[target]).astype(int)
X_val_steady = val_steady[features]
y_val_steady = (val_steady[target]).astype(int)
X_test_steady = test_steady[features]


pipe = make_pipeline(
    OneHotEncoder(use_cat_names=True), 
    SimpleImputer(), 
    RandomForestRegressor(n_jobs=-1, random_state=10, oob_score=True)
)

pipe.fit(X_train_steady, y_train_steady)
print('검증 정확도: ', pipe.score(X_val_steady, y_val_steady))


import pickle

with open('model.pkl','wb') as pickle_file:
    pickle.dump(pipe, pickle_file)