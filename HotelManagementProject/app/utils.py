import hashlib

from app import db, dao, app, login
from app.models import *


def check_login(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_user(customer_type=None, name=None, username=None, password=None, phone=None, **kwargs):
    if customer_type and name and username and password and phone:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        with app.app_context():
            user = User(name=name, username=username, gender=kwargs.get('gender'), password=password, email=kwargs.get('email'), phone=phone, avatar=kwargs.get('avatar'))
            db.session.add(user)
            db.session.commit()
            # print('add user - done')

            for ct in CustomerType.query.all():
                if customer_type.strip().__eq__(ct.type.strip()):
                    customer = Customer(id=user.id, customer_type_id=ct.id)
                    db.session.add(customer)
                    db.session.commit()
                    # print('add user_type - done')
