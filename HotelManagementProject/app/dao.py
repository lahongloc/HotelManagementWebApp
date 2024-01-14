import hashlib
import hmac
import urllib
from datetime import datetime

from flask_login import current_user, AnonymousUserMixin
from sqlalchemy import func, Numeric, extract

from app.models import *
from app import app, utils

import smtplib


def send_message_twilio(message):
    from twilio.rest import Client

    account_sid = 'AC34dbe9c496f4108ac74cda4a50ab4b94'
    auth_token = '112ca59ebefd2a224813f7339cf368aa'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        _from='+17178976092',
        body='Loc Yeu Ly Lammmmmmmm',
        to='+84869311727'
    )

    print(message.sid)


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


def get_rooms_info(room_id=None, kw=None, checkin=None, checkout=None, room_type=None):
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
        if kw:
            rooms_info = rooms_info.filter(Room.name.contains(kw))
        if room_type:
            rooms_info = rooms_info.filter(RoomType.id.__eq__(room_type))

        new_rooms_info = []
        if checkin and checkout:
            for r in rooms_info.all():
                if utils.check_reservation(checkin_time=checkin, checkout_time=checkout, room_id=r.id):
                    new_rooms_info.append(r)
            return new_rooms_info

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
                                           RoomRegulation.price,
                                           RoomRegulation.surcharge * 100) \
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
                            deposit=total_price)
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


class vnpay:
    requestData = {}
    responseData = {}

    def get_payment_url(self, vnpay_payment_url, secret_key):
        # Dữ liệu thanh toán được sắp xếp dưới dạng danh sách các cặp khóa-giá trị theo thứ tự tăng dần của khóa.
        inputData = sorted(self.requestData.items())
        # Duyệt qua danh sách đã sắp xếp và tạo chuỗi query sử dụng urllib.parse.quote_plus để mã hóa giá trị
        queryString = ''
        hasData = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                queryString = key + '=' + urllib.parse.quote_plus(str(val))

        # Sử dụng phương thức __hmacsha512 để tạo mã hash từ chuỗi query và khóa bí mật
        hashValue = self.__hmacsha512(secret_key, queryString)
        return vnpay_payment_url + "?" + queryString + '&vnp_SecureHash=' + hashValue

    def validate_response(self, secret_key):
        # Lấy giá trị của vnp_SecureHash từ self.responseData.
        vnp_SecureHash = self.responseData['vnp_SecureHash']
        # Loại bỏ các tham số liên quan đến mã hash
        if 'vnp_SecureHash' in self.responseData.keys():
            self.responseData.pop('vnp_SecureHash')

        if 'vnp_SecureHashType' in self.responseData.keys():
            self.responseData.pop('vnp_SecureHashType')
        # Sắp xếp dữ liệu (inputData)
        inputData = sorted(self.responseData.items())

        hasData = ''
        seq = 0
        for key, val in inputData:
            if str(key).startswith('vnp_'):
                if seq == 1:
                    hasData = hasData + "&" + str(key) + '=' + urllib.parse.quote_plus(str(val))
                else:
                    seq = 1
                    hasData = str(key) + '=' + urllib.parse.quote_plus(str(val))
        # Tạo mã hash
        hashValue = self.__hmacsha512(secret_key, hasData)

        print(
            'Validate debug, HashData:' + hasData + "\n HashValue:" + hashValue + "\nInputHash:" + vnp_SecureHash)

        return vnp_SecureHash == hashValue

    # tạo mã hash dựa trên thuật toán HMAC-SHA-512
    @staticmethod
    def __hmacsha512(key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def month_sale_statistic(month=None, year=None, kw=None, from_date=None, to_date=None):
    with app.app_context():
        if not kw and not from_date and not to_date and not month and not year:
            count_receipt = Receipt.query.count()
        elif from_date and to_date:
            count_receipt = Receipt.query.filter(
                Receipt.created_date.__ge__(from_date),
                Receipt.created_date.__le__(to_date)).count()
        elif from_date:
            count_receipt = Receipt.query.filter(
                Receipt.created_date.__ge__(from_date)).count()
        elif to_date:
            count_receipt = Receipt.query.filter(
                Receipt.created_date.__le__(to_date)).count()
        elif kw:
            count_receipt = Receipt.query.count()
        elif month:
            count_receipt = Receipt.query.filter(
                extract('month', Receipt.created_date) == month)
            if year:
                count_receipt = count_receipt.filter(
                    extract('year', Receipt.created_date) == year)
            count_receipt = count_receipt.count()

        month_sale_statistic = db.session.query(RoomType.name,
                                                func.sum(Receipt.total_price),
                                                func.count(RoomRental.id),
                                                func.cast((func.count(RoomRental.id) / count_receipt) * 100
                                                          , Numeric(5, 2))) \
            .outerjoin(RoomRental, RoomRental.id.__eq__(Receipt.rental_room_id)) \
            .outerjoin(Reservation, Reservation.id.__eq__(RoomRental.reservation_id)) \
            .outerjoin(Room, Room.id.__eq__(
            Reservation.room_id)  # Phải là OR vì Thuê Phòng CÓ THỂ KHÔNG thông qua Phiếu Đặt Phòng
                       or Room.id.__eq__(RoomRental.room_id)) \
            .outerjoin(RoomType, RoomType.id.__eq__(Room.room_type_id)) \
            .group_by(RoomType.name) \
            .order_by(RoomType.id)

        if month:
            month_sale_statistic = month_sale_statistic.filter(
                extract('month', Receipt.created_date) == month) \
                .group_by(extract('month', Receipt.created_date))

        if year:
            month_sale_statistic = month_sale_statistic.filter(
                extract('year', Receipt.created_date) == year)

        if kw:
            month_sale_statistic = month_sale_statistic.filter(RoomType.name.contains(kw))

        if from_date:
            month_sale_statistic = month_sale_statistic.filter(Receipt.created_date.__ge__(from_date))

        if to_date:
            month_sale_statistic = month_sale_statistic.filter(Receipt.created_date.__le__(to_date))

        return month_sale_statistic.all()

# def year_month_sale_statistic(month=None, year=None):
#     with app.app_context():
#         result = db.session.query(extract('month', Receipt.created_date),
#                                   extract('year', Receipt.created_date),
#                                   func.sum(Receipt.total_price)) \
#             .group_by(extract('month', Receipt.created_date),
#                       extract('year', Receipt.created_date))
#         if year:
#             result = result.filter(extract('year', Receipt.created_date) == year)
#
#         if month:
#             result = result.filter(extract('month', Receipt.created_date) == month)
#
#         return result.all()
