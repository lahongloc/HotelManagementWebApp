from urllib.parse import quote

import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
login = LoginManager(app)

app.secret_key = '56%^&*987^&*(098&*((*&^&*&'
app.config['SQLALCHEMY_DATABASE_URI'] = str.format('mysql+pymysql://root:{}@localhost/{dbname}?charset=utf8mb4',
                                                   'dbpassword')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 4

db = SQLAlchemy(app=app)

cloudinary.config(
    cloud_name='{cloud_name}',
    api_key='{api_key}',
    api_secret='{api_secret}'
)

# Các thông số cần thiết từ tài khoản VNPay Sandbox
vnpay_config = {
    'vnp_TmnCode': '{vnp_TmnCode}',
    'vnp_HashSecret': '{vnp_HashSecret}',
    'vnp_Url': '{vnp_Url}',
}
