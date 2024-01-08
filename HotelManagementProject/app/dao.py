import hashlib
from datetime import datetime

from flask_login import current_user, AnonymousUserMixin

from app.models import *
from app import app, utils

import smtplib


def get_customer_info():
    if current_user:
        with app.app_context():
            customer_info = db.session.query(Customer.id, Customer.customer_id, Customer.identification, Customer.name,
                                             CustomerType.type) \
                .join(Customer, Customer.customer_type_id.__eq__(CustomerType.id))
            customer_info = customer_info.filter(Customer.id.__eq__(current_user.id)).first()
            return customer_info


# print(get_customer_info())


def get_room_types():
    with app.app_context():
        room_types = RoomType.query.all()
        return room_types


def get_user_by_id(user_id=None):
    with app.app_context():
        user = User.query.get(id)
        return user


def get_rooms():
    with app.app_context():
        rooms = Room.query.all()
        return rooms


def get_rooms_info(room_id=None):
    with app.app_context():
        rooms_info = db.session.query(Room.name, Room.id, Room.image, RoomType.name.label('room_type'),
                                      RoomRegulation.price,
                                      RoomRegulation.room_quantity,
                                      RoomRegulation.capacity) \
            .join(Room, Room.room_type_id.__eq__(RoomType.id)) \
            .join(RoomRegulation, RoomRegulation.room_type_id.__eq__(RoomType.id))

        if room_id:
            rooms_info = rooms_info.filter(Room.id.__eq__(room_id)).first()
            return rooms_info

        return rooms_info.all()


def get_user_role():
    r = []
    for u in UserRole:
        a = str(u).split('.')
        r.append(a[1])
    return r


def get_customer_role():
    r = []
    for t in CustomerType.query.all():
        r.append(t.type)
    return r


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


## --- SMTP Gmail --- ###
def send_gmail(receive_email=None, subject=None, message=None):
    if receive_email and subject and message:
        email = 'kitj317@gmail.com'
        receive_email = str(receive_email)

        subject = str(subject)
        message = str(message)

        text = f"Subject: {subject}\n\n{message}"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(email, "jczp aylv xjzn ufje")

        server.sendmail(email, receive_email, text)

        print("Email has been sent to " + receive_email)
    else:
        print('Empty email???')


def get_room_regulation():
    # if current_user.is_authenticated and current_user.role.__eq__(UserRole.ADMIN):
    with app.app_context():
        room_regulation = db.session.query(RoomType.name.label('rome_type_name'),
                                           User.username.label('user_name'),
                                           RoomRegulation.room_quantity,
                                           RoomRegulation.capacity,
                                           RoomRegulation.price) \
            .join(Administrator, Administrator.id == RoomRegulation.admin_id) \
            .join(RoomType, RoomType.id == RoomRegulation.room_type_id) \
            .join(User, User.id == Administrator.id) \
            .group_by(RoomRegulation.room_quantity,
                      RoomRegulation.capacity,
                      RoomRegulation.price,
                      RoomType.name.label('rome_type_name'),
                      User.username.label('user_name')) \
            .all()

        # print(room_regulation)
        return room_regulation


def get_customer_type_regulation():
    # if current_user.is_authenticated and current_user.role.__eq__(UserRole.ADMIN):
    with app.app_context():
        customer_type_regulation = db.session.query(CustomerTypeRegulation.id,
                                                    CustomerType.type.label('customer_type'),
                                                    Administrator.name.label('name_admin'),
                                                    CustomerTypeRegulation.rate) \
            .join(Administrator, Administrator.id == CustomerTypeRegulation.admin_id) \
            .join(CustomerType, CustomerType.id == CustomerTypeRegulation.customer_type_id) \
            .group_by(CustomerTypeRegulation.id,
                      CustomerType.type.label('customer_type'),
                      Administrator.name.label('name_admin'),
                      CustomerTypeRegulation.rate) \
            .all()

        # print(customer_type_regulation)
        return customer_type_regulation


def add_customers(customers=None, room_id=None, checkin_time=None, checkout_time=None, total_price=None):
    added_customers_ids = []
    added_reservation_id = None
    if customers and room_id and checkin_time and checkout_time and total_price:
        # 1. create reservation and save this reservation_id for creating reservation_detail
        checkin_time = datetime.strptime(str(checkin_time), "%Y-%m-%dT%H:%M")
        checkout_time = datetime.strptime(str(checkout_time), "%Y-%m-%dT%H:%M")
        with app.app_context():
            r = Reservation(room_id=room_id,
                            checkin_date=checkin_time,
                            checkout_date=checkout_time,
                            total_price=total_price)
            if current_user.role == UserRole.CUSTOMER:
                r.customer_id = get_customer_info().customer_id
            elif current_user.role == UserRole.RECEPTIONIST:
                r.receptionist_id = current_user.id
            db.session.add(r)
            db.session.commit()
            # save the reservation_id
            added_reservation_id = r.id
        is_customers_added = True
        # 2. add customers who will use the room to db
        try:
            if added_reservation_id:
                for cus in customers:
                    customer_id = find_customer_by_identification(customers[str(cus)]['customerIdNum'])
                    if customer_id:
                        added_customers_ids.append(customer_id)
                    else:
                        c = Customer(name=customers[str(cus)]['customerName'],
                                     identification=customers[str(cus)]['customerIdNum'])
                        c.customer_type_id = get_id_of_customer_type(customers[str(cus)]['customerType'])
                        db.session.add(c)
                        db.session.commit()
                        added_customers_ids.append(c.customer_id)
        except Exception as ex:
            is_customers_added = False
            print(str(ex))
        # 3. add reservation_detail
        if added_reservation_id and is_customers_added:
            for i in added_customers_ids:
                rd = ReservationDetail(customer_id=i, reservation_id=added_reservation_id)
                db.session.add(rd)
                db.session.commit()


def find_customer_by_identification(identification=None):
    if identification:
        with app.app_context():
            customer = Customer.query.filter(Customer.identification.__eq__(str(identification).strip())).first()
            if customer:
                return customer.customer_id


def get_id_of_customer_type(type=None):
    if type:
        with app.app_context():
            type_id = CustomerType.query.filter(CustomerType.type.__eq__(str(type).strip())).first()
            return type_id.id
