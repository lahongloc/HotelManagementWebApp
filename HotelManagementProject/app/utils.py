import hashlib
from datetime import datetime

from app import db, dao, app, login
from app.models import User, CustomerType, Room, RoomRegulation, RoomType, Customer, Reservation, CustomerTypeRegulation


def check_login(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_user(customer_type=None, name=None, username=None, password=None, phone=None, id_num=None, **kwargs):
    if customer_type and name and username and password and phone and id_num:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        with app.app_context():
            user = User(username=username, gender=kwargs.get('gender'), password=password,
                        email=kwargs.get('email'), phone=phone, avatar=kwargs.get('avatar'))
            db.session.add(user)
            db.session.commit()
            # print('add user - done')

            for ct in CustomerType.query.all():
                if customer_type.strip().__eq__(ct.type.strip()):
                    customer = Customer(id=user.id, name=name, customer_type_id=ct.id, identification=id_num)
                    db.session.add(customer)
                    db.session.commit()


def get_user_by_username(username):
    return User.query.filter(User.username.__eq__(username.strip())).first()


def get_user_by_email(email):
    return User.query.get(email)


def get_user_by_phone(phone):
    return User.query.get(phone)


# def add_user(customer_type=None, name=None, username=None, password=None, phone=None, **kwargs):
#     if customer_type and name and username and password and phone:
#         password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
#         with app.app_context():
#             user = User(name=name, username=username, gender=kwargs.get('gender'), password=password,
#                         email=kwargs.get('email'), phone=phone, avatar=kwargs.get('avatar'))
#
#             # print('add user_type - done')


def calculate_total_reservation_price(reservation_info=None, room_id=None):
    if reservation_info and room_id:
        customers = reservation_info[room_id]['users']

        num_customers = len(customers)
        num_foreign_customers = 0
        for i in range(1, len(customers) + 1):
            if customers[i]['customerType'] == 'FOREIGN':
                num_foreign_customers += 1

        with app.app_context():
            room_price = db.session.query(Room.name, RoomType.name, RoomRegulation.price, RoomRegulation.surcharge,
                                          RoomRegulation.capacity) \
                .join(Room, Room.room_type_id.__eq__(RoomType.id)) \
                .join(RoomRegulation, RoomRegulation.room_type_id.__eq__(RoomType.id)).filter(
                Room.id.__eq__(room_id)).first()

            total_price = room_price.price
            if num_customers == room_price.capacity:
                total_price += total_price * room_price.surcharge
            if num_foreign_customers > 0:
                customer_rate = db.session.query(CustomerType.type, CustomerTypeRegulation.rate) \
                    .join(CustomerTypeRegulation, CustomerTypeRegulation.customer_type_id.__eq__(CustomerType.id)) \
                    .filter(CustomerType.type.__eq__('FOREIGN')).first()
                total_price *= customer_rate.rate

            reservation_info[room_id]['total_price'] = total_price
            return reservation_info


def check_reservation(checkin_time=None, checkout_time=None, room_id=None):
    if checkin_time and checkout_time and room_id:
        is_valid = True
        with app.app_context():
            reservation = db.session.query(Reservation.checkin_date, Reservation.checkout_date).filter(
                Reservation.room_id.__eq__(room_id)).all()
            for dt in reservation:
                if (dt[0] <= checkin_time <= dt[1]) or (dt[0] <= checkout_time <= dt[1]) or (
                        dt[0] >= checkin_time and dt[1] <= checkout_time):
                    is_valid = False

        return is_valid


def get_cus_type_by_identification(identification=None):
    if identification:
        with app.app_context():
            cus_type = db.session.query(Customer.identification, Customer.name, Customer.customer_id, CustomerType.type) \
                .join(CustomerType, CustomerType.id.__eq__(Customer.customer_type_id)) \
                .filter(Customer.identification.__eq__(identification.strip())).first()
            if cus_type:
                return cus_type


