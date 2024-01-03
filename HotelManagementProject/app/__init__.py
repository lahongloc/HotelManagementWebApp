from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = '56%^&*987^&*(098&*((*&^&*&'
app.config['SQLALCHEMY_DATABASE_URI'] = str.format('mysql+pymysql://root:{}@localhost/hoteldb?charset=utf8mb4',
                                                   '123456')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app=app)
