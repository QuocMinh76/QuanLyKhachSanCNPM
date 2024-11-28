from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
import cloudinary
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key = 'aweut9n8*@$*djhfjsadhfsdqefsfgasedq23i'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/saledb?charset=utf8mb4" % quote("Admin@123") #school
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/saledb?charset=utf8mb4" % quote("1234") #home
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app)

cloudinary.config(cloud_name='dhhpxhskj',
                  api_key='398599846358987',
                  api_secret='jNqe-OCxgo98G-K6_OAL0nuvyEk')

login = LoginManager(app)