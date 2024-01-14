import hashlib
from datetime import datetime

from flask_login import current_user, AnonymousUserMixin
from sqlalchemy import desc

from app.models import *
from app import app, utils

import smtplib


def get_customer_info():
    if current_user.is_authenticated:
        with app.app_context():
            customer_info = db.session.query(Customer.id, Customer.customer_id, Customer.identification, Customer.name,
                                             CustomerType.type) \
                .join(Customer, Customer.customer_type_id.__eq__(CustomerType.id))
            customer_info = customer_info.filter(Customer.id.__eq__(current_user.id)).first()
            return customer_info


def get_full_user_info():
    if current_user.is_authenticated:
        with app.app_context():
            if current_user.role == UserRole.CUSTOMER:
                full_user_info = db.session.query(User.username, User.password, User.email, User.phone, User.avatar,
                                                  User.gender,
                                                  Customer.name, Customer.identification, CustomerType.type) \
                    .join(User, User.id == Customer.id) \
                    .join(CustomerType, CustomerType.id == Customer.customer_type_id) \
                    .group_by(User.username, User.password, User.email, User.phone, User.avatar, User.gender,
                              Customer.name, Customer.identification,
                              CustomerType.type)
                full_user_info = full_user_info.filter(Customer.id.__eq__(current_user.id)).first()

                print(full_user_info)
                return full_user_info


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
                                      RoomRegulation.capacity,
                                      RoomRegulation.distance) \
            .join(Room, Room.room_type_id.__eq__(RoomType.id)) \
            .join(RoomRegulation, RoomRegulation.room_type_id.__eq__(RoomType.id)) \
            .order_by(Room.id)

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


def create_room_rental(reservation_id=None):
    if reservation_id:
        try:
            with app.app_context():
                rr = RoomRental(reservation_id=reservation_id, receptionist_id=current_user.id)
                Reservation.query.filter(Reservation.id.__eq__(reservation_id)).first().is_checkin = True
                db.session.add(rr)
                db.session.commit()
        except Exception as ex:
            print(str(ex))


def receptionist_room_rental(room_rental_info=None, checkout_time=None, room_id=None):
    if room_rental_info and checkout_time and room_id:
        added_customers_ids = []
        added_room_rental = None
        # print(room_rental_info[str(room_id)]['users'])
        # add customers
        try:
            for i in range(1, len(room_rental_info[str(room_id)]['users']) + 1):
                cus_identification = room_rental_info[str(room_id)]['users'][i]['customerIdNum']
                customer_id = find_customer_by_identification(identification=cus_identification)
                if customer_id:
                    added_customers_ids.append(customer_id)
                else:
                    c = Customer(name=room_rental_info[str(room_id)]['users'][i]['customerName'],
                                 identification=room_rental_info[str(room_id)]['users'][i]['customerIdNum'])
                    c.customer_type_id = get_id_of_customer_type(
                        room_rental_info[str(room_id)]['users'][i]['customerType'])
                    db.session.add(c)
                    db.session.commit()
                    added_customers_ids.append(c.customer_id)
        except Exception as ex:
            print(str(ex))

        #     add room rental
        try:
            if added_customers_ids:
                rr = RoomRental(receptionist_id=current_user.id, room_id=room_id, checkout_date=checkout_time)
                db.session.add(rr)
                db.session.commit()
                added_room_rental = rr.id
        except Exception as ex:
            print(str(ex))

        #     add room rental detail
        try:
            if added_customers_ids and added_room_rental:
                for c in added_customers_ids:
                    rrd = RoomRentalDetail(customer_id=c, room_rental_id=added_room_rental)
                    db.session.add(rrd)
                    db.session.commit()
        except Exception as ex:
            print(str(ex))


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
