from flask import Flask, render_template, request
import numpy as np
import pickle
import psycopg2
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline

# model = None
with open('model.pkl','rb') as pickle_file:
    model = pickle.load(pickle_file)

def create_app():   
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template('home.html')


    @app.route('/predict', methods=['POST'])
    def main():
        data0 = request.form['브랜드']
        data1 = request.form['옷의 종류']
        data2 = request.form['추천 수']
        data3 = request.form['1일 랭킹']
        data4 = request.form['1주 랭킹']
        data5 = request.form['1달 랭킹']
        data6 = request.form['3달 랭킹']
        data7 = request.form['1년 랭킹']
        data_con = [[data0,data1,data2,data3,data4,data5,data6,data7],[data0,data1,data2,data3,data4,data5,data6,data7]]
        data_columns = ['brand_name','kind','recommend','1d','1w','1m','3m','1y']
        df = pd.DataFrame(data_con, columns=data_columns)
        y_pred = model.predict(df.iloc[0:1])
        
        
        con = psycopg2.connect(
        host = 'arjuna.db.elephantsql.com',
        database = 'jufgneai',
        user = 'jufgneai',
        password = 'GSJ9LWjCYj-1kKjmwpH4GaqdWl-ApwS0'
        )
        cur = con.cursor()
        rank = (int(data3)+int(data4)+int(data5)+int(data6)+int(data7))/5
        if data1 == 'TOP':
            item_name = '001'
        elif data1 == 'OUTER':
            item_name = '002'
        elif data1 == 'PANTS':
            item_name = '003'
        elif data1 == 'BAG':
            item_name = '004'
        elif data1 == 'SHOES':
            item_name = '005'
        elif data1 == 'ACCESSORY':
            item_name = '011'
        elif data1 == 'SPORTS':
            item_name = '017'
        else:
            item_name = '018'
        cur.execute("INSERT INTO rank values('{}','{}','{}','{}','{}','{}','{}')".format(int(rank),data0,item_name,data1,int(y_pred), int(data2),'1d'))
        con.commit()
    
        
        return render_template('result.html',data = f'예상 가격은 {int(y_pred)}원 입니다.')
    
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    # @app.route('/dashboard2')
    # def dashboard2():
    #     return render_template('dashboard2.html')
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port = 5001,debug=True)
    