from flask import Flask, Blueprint, render_template, request
import pymongo

import requests
from bs4 import BeautifulSoup

import pandas as pd

from pymongo import MongoClient
from flask_pymongo import PyMongo

from sklearn.linear_model import LinearRegression
#pymongo setting

HOST = 'cluster0.p6ldj.mongodb.net'
USER = 'Evan'
PASSWORD = 'Evan123'
DATABASE_NAME = 'myFirstDatabase'
COLLECTION_NAME = 'landprice'
MONGO_URI = f"mongodb+srv://{USER}:{PASSWORD}@{HOST}/{DATABASE_NAME}?retryWrites=true&w=majority"

app = Flask(__name__)
app.config["MONGO_URI"] = f"mongodb+srv://{USER}:{PASSWORD}@{HOST}/{DATABASE_NAME}?retryWrites=true&w=majority"
mongo = PyMongo(app)

bp = Blueprint('result',__name__,url_prefix='/')

# searchForm 데이터를 받아서 다시 result.html에 전송함
@bp.route('/searchForm', methods =['POST'])
def search_form():
    
    if request.method == 'POST':
        data = request.form
    else :
        data = {}

    location = []
    price = []
    year = []
    jdic = {}
    dic_list = []
    for i in range(int(data['year'])-20,int(data['year'])+1): # 20년치 데이터를 불러온다.
        api = f"http://openapi.seoul.go.kr:8088/507173467279303031303147666f6e59/xml/IndividuallyPostedLandPriceService/1/5/{data['gu']}/{data['dong']}/{data['first_num']}/{data['second_num']}/1/{i}"
        page = requests.get(api)

        soup = BeautifulSoup(page.content, 'html.parser')
        if soup.message.contents[0] == "해당하는 데이터가 없습니다." :
            print(f"{i}년 정보 없음")
            continue
        
        # list들에 데이터 추가
        location.append(data['gu']+' '+data['dong']+' '+data['first_num']+'-'+data['second_num'])
        price.append(soup.jiga.contents[0])
        year.append(i)

        # MongoDB에 넣기위해 json 처리화 과정
        jdic = {'location' : data['gu']+' '+data['dong']+' '+data['first_num']+'-'+data['second_num'],\
             'price' : soup.jiga.contents[0],
             'year':i}
        dic_list.append(jdic)

        # print(soup.jiga.contents[0])
    # pandas dataframe화
    dic = {'Location':location,'Price':price,'Year':year}
    df = pd.DataFrame(dic).sort_values(by=['Year'],ascending=False)
    
    # df를 HTML 테이블 테그로 변환
    df_html = df.to_html(escape=False, justify='center')

    # MongoDB 연결

    board = mongo.db.board

    json_data = {"Data":dic_list}

    board.insert_one(json_data)

    # 선형회귀모형
    model = LinearRegression()

    feature = ['Year']
    target = ['Price']
    X_train = df[feature]
    y_train = df[target]

    model.fit(X_train, y_train)
    
    from sklearn.metrics import mean_absolute_error 
    y_pred = model.predict(X_train)
    mae = mean_absolute_error(y_train, y_pred)
    
    input_year = int(data['year'])
    df2 = pd.DataFrame({'Year':[input_year+1]})
    pred = model.predict(df2)
    mae = int(mae)

    return render_template('result.html', data=data, df_html=df_html, pred=int(pred), input_year=input_year, mae=mae)