from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
import cloudinary
from flask_login import LoginManager

app = Flask(__name__)

#Nho doi PASSWORD thanh mat khau MySQL cua cac ban trong "SQLALCHEMY_DATABASE_URI" khi code
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hoteldb?charset=utf8mb4" % quote("1234") #minh
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hoteldb?charset=utf8mb4" % quote("Mat khau de day") #my
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hoteldb?charset=utf8mb4" % quote("Mat khau de day") #kiet


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app)

cloudinary.config(cloud_name='dhhpxhskj',
                  api_key='398599846358987',
                  api_secret='jNqe-OCxgo98G-K6_OAL0nuvyEk')

login = LoginManager(app)