import hashlib
from datetime import datetime

from flask_login import current_user, AnonymousUserMixin

from app.models import *
from app import app

import smtplib


def get_customer_info():
    if current_user.is_authenticated:
        with app.app_context():
            customer_info = db.session.query(Customer.id, Customer.customer_id, Customer.identification, Customer.name,
                                             CustomerType.type) \
                .join(Customer, Customer.customer_type_id.__eq__(CustomerType.id))
            customer_info = customer_info.filter(Customer.id.__eq__(current_user.id)).first()
            return customer_info


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


def add_customers(customers=None, room_id=None, checkin_time=None, checkout_time=None, total_price=None):
    try:
        if customers and room_id and checkin_time and checkout_time and total_price:
            added_customers_ids = []
            added_reservation_id = None
            # add reservation
            if current_user.role.__eq__(UserRole.CUSTOMER):
                checkin_time = datetime.strptime(str(checkin_time), "%Y-%m-%dT%H:%M")
                checkout_time = datetime.strptime(str(checkout_time), "%Y-%m-%dT%H:%M")
                with app.app_context():
                    r = Reservation(customer_id=get_customer_info().customer_id, room_id=room_id,
                                    checkin_date=checkin_time,
                                    checkout_date=checkout_time,
                                    total_price=total_price)
                    db.session.add(r)
                    db.session.commit()
                    added_reservation_id = r.id

            # add customers paying for the reservation into db
            for i in range(2, len(customers) + 1):
                cus_type = 1
                if customers[str(i)]['customerType'] == 'FOREIGN':
                    cus_type = 2
                with app.app_context():
                    c = Customer(name=customers[str(i)]['customerName'],
                                 identification=customers[str(i)]['customerIdNum'], customer_type_id=cus_type)
                    db.session.add(c)
                    db.session.commit()
                    added_customers_ids.append(c.customer_id)

            # add reservation details
            current_user_rd = ReservationDetail(customer_id=get_customer_info().customer_id,
                                                reservation_id=added_reservation_id)
            db.session.add(current_user_rd)
            db.session.commit()
            for cus_id in added_customers_ids:
                rd = ReservationDetail(customer_id=cus_id, reservation_id=added_reservation_id)
                db.session.add(rd)
                db.session.commit()

            return True
    except Exception as ex:
        print(str(ex))

# def add_reservation():
