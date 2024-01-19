import hashlib
import hmac
import threading
import urllib
from datetime import datetime

from flask_login import current_user, AnonymousUserMixin
from sqlalchemy import func, Numeric, extract, or_, and_, case, desc, text
from sqlalchemy.orm import aliased

from app.models import *
from app import app, utils

import smtplib


def send_message_twilio(message):
    from twilio.rest import Client

    account_sid = 'AC34dbe9c496f4108ac74cda4a50ab4b94'
    auth_token = '112ca59ebefd2a224813f7339cf368aa'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='+17178976092',
        body=str(message),
        to='+84869311727'
    )


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

                # print(full_user_info)
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


def get_rooms_info(room_id=None, kw=None, checkin=None, checkout=None, room_type=None, page=1, is_paginated=None):
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

        new_rooms_info = []
        if checkin and checkout:
            for r in rooms_info.all():
                if utils.check_reservation(checkin_time=checkin, checkout_time=checkout, room_id=r.id):
                    new_rooms_info.append(r)
            return new_rooms_info

        start = page * app.config['PAGE_SIZE'] - app.config['PAGE_SIZE']
        end = start + app.config['PAGE_SIZE']
        if is_paginated:
            return rooms_info.slice(start, end).all(), Room.query.count()

        return rooms_info.all()


def get_comment(room_id=None):
    if room_id:
        with app.app_context():
            comments = db.session.query(User.avatar, User.username, Comment.content, Comment.created_date) \
                .join(Customer, Customer.id.__eq__(User.id)) \
                .join(Comment, Comment.customer_id.__eq__(Customer.id)) \
                .filter(Comment.room_id.__eq__(room_id)).order_by(desc(Comment.created_date)).all()
            return comments


def add_comment(content=None, room_id=None):
    if content and room_id:
        with app.app_context():
            # customers_id = db.session.query(Customer.id).join(User, current_user.id == Customer.id).first()
            customer = Customer.query.filter(Customer.id.__eq__(current_user.id)).first()
            comment = Comment(customer=customer, content=content, room_id=room_id)
            db.session.add(comment)
            db.session.commit()


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
            .join(User, User.id == Administrator.id)

        return room_regulation.all()


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
            content = """
Dear {0},

Congratulations! Your booking at Elite Hotel is confirmed. We look forward to hosting you and providing a memorable stay.

Best regards,

Elite Hotel
            """.format(current_user.username)
            if current_user.role == UserRole.CUSTOMER:
                send_gmail(current_user.email, 'Your request to book room has been processed successfully!', content)
            if current_user.role == UserRole.RECEPTIONIST:
                emails = db.session.query(User.email) \
                    .join(Customer, Customer.id.__eq__(User.id)) \
                    .join(ReservationDetail, ReservationDetail.customer_id.__eq__(Customer.customer_id)) \
                    .filter(ReservationDetail.reservation_id.__eq__(added_reservation_id)).all()
                for e in emails:
                    send_gmail(e.email, 'Your request to book room has been processed successfully!', content)
                    break


def create_room_rental(reservation_id=None):
    if reservation_id:
        try:
            with app.app_context():
                reservation = Reservation.query.get(reservation_id)
                rr = RoomRental(reservation_id=reservation_id, receptionist_id=current_user.id,
                                checkout_date=reservation.checkout_date, deposit=reservation.deposit)
                reservation.is_checkin = True
                db.session.add(rr)
                db.session.commit()
        except Exception as ex:
            print(str(ex))


def create_receipt(room_rental_id=None, room_id=None, is_calculate=None):
    if room_rental_id and room_id:
        with app.app_context():
            deposit_rate = RoomRegulation.query.filter(
                RoomRegulation.room_type_id.__eq__(Room.query.get(room_id).room_type_id)).first().deposit_rate
            room_rental = RoomRental.query.get(room_rental_id)
            # calculate the total price from the room rental 's deposit and the deposit rate
            total_price = (room_rental.deposit / deposit_rate) - room_rental.deposit
            if is_calculate:
                return total_price
            else:
                rc = Receipt(rental_room_id=room_rental.id, total_price=total_price, receptionist_id=current_user.id)
                room_rental.is_paid = True
                db.session.add(rc)
                db.session.commit()

                emails = get_user_emails_by_room_rental_id(room_rental_id=room_rental.id)
                # Tạo các đối tượng Thread để thực hiện công việc đồng thời
                twilio_thread = threading.Thread(target=send_message_twilio,
                                                 args=(
                                                     "Thanks for using services at Elite-hotel and see you next time!",))
                content = (f'You have paid {rc.total_price} VND for your room at '
                           f'Elite-hotel, thanks for all!')
                gmail_thread = threading.Thread(target=send_gmail,
                                                args=(
                                                    emails[0],
                                                    f"YOU HAVE PAID {total_price} FOR YOUR RECEIPT AT ELITE-HOTEL!",
                                                    content))

                # Bắt đầu thực hiện các luồng
                twilio_thread.start()
                gmail_thread.start()

                # Chờ tất cả các luồng hoàn thành
                twilio_thread.join()
                gmail_thread.join()


def get_user_emails_by_room_rental_id(room_rental_id=None):
    if room_rental_id:
        emails = []
        with app.app_context():
            is_from_reservation = RoomRental.query.filter(RoomRental.id.__eq__(room_rental_id)).first().room_id
            if not is_from_reservation:
                user = db.session.query(User.email) \
                    .join(Customer, Customer.id.__eq__(User.id)) \
                    .join(Reservation, Reservation.customer_id.__eq__(Customer.customer_id)) \
                    .join(RoomRental, RoomRental.reservation_id.__eq__(Reservation.id)) \
                    .filter(RoomRental.id.__eq__(room_rental_id)).first()
                emails.append(user.email)
            else:
                customers = db.session.query(User.id, Customer.customer_id, User.email) \
                    .join(Customer, Customer.id.__eq__(User.id)) \
                    .join(RoomRentalDetail, RoomRentalDetail.customer_id.__eq__(Customer.customer_id)) \
                    .join(RoomRental, RoomRental.id.__eq__(RoomRentalDetail.room_rental_id)) \
                    .filter(RoomRental.id.__eq__(room_rental_id)).all()
                for c in customers:
                    emails.append(c.email)
        return emails


def receptionist_room_rental(room_rental_info=None, checkout_time=None, room_id=None):
    if room_rental_info and checkout_time and room_id:
        added_customers_ids = []
        added_room_rental = None
        # print(room_rental_info[str(room_id)]['users'])
        # add customers
        try:
            # print(room_rental_info[room_id])
            for i in range(1, len(room_rental_info[room_id]['users']) + 1):
                cus_identification = room_rental_info[room_id]['users'][i]['customerIdNum']
                customer_id = find_customer_by_identification(identification=cus_identification)
                if customer_id:
                    added_customers_ids.append(customer_id)
                else:
                    c = Customer(name=room_rental_info[room_id]['users'][i]['customerName'],
                                 identification=room_rental_info[room_id]['users'][i]['customerIdNum'])
                    c.customer_type_id = get_id_of_customer_type(
                        room_rental_info[room_id]['users'][i]['customerType'])
                    db.session.add(c)
                    db.session.commit()
                    added_customers_ids.append(c.customer_id)
        except Exception as ex:
            print(str(ex))
            print('hehe')
            return False

        #     add room rental
        try:
            if added_customers_ids:
                rr = RoomRental(receptionist_id=current_user.id, room_id=room_id, checkout_date=checkout_time,
                                deposit=room_rental_info[room_id]['total_price'])
                db.session.add(rr)
                db.session.commit()
                added_room_rental = rr.id
        except Exception as ex:
            print(str(ex))
            print('haah')
            return False

        #     add room rental detail
        try:
            if added_customers_ids and added_room_rental:
                for c in added_customers_ids:
                    rrd = RoomRentalDetail(customer_id=c, room_rental_id=added_room_rental)
                    db.session.add(rrd)
                    db.session.commit()
        except Exception as ex:
            print('hoho')
            print(str(ex))
            return False
    return True


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


def month_sale_statistic(month=None, year=None, kw=None, from_date=None, to_date=None, **kwargs):
    with app.app_context():
        if not kw and not from_date and not to_date and not month and not year:
            count_receipt = Receipt.query.count()
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
        else:
            count_receipt = Receipt.query.filter(
                extract('year', Receipt.created_date) == year).count()

        month_sale_statistic = db.session.query(RoomType.name,
                                                func.coalesce(func.sum(Receipt.total_price), 0),
                                                func.coalesce(func.count(Receipt.id), 0),
                                                func.cast((func.count(Receipt.id) / count_receipt) * 100
                                                          , Numeric(5, 2))) \
            .join(Room, Room.room_type_id.__eq__(RoomType.id), isouter=True) \
            .join(RoomRental, RoomRental.room_id.__eq__(Room.id), isouter=True) \
            .join(Receipt, Receipt.rental_room_id.__eq__(RoomRental.id), isouter=True) \
            .group_by(RoomType.name) \
            .order_by(RoomType.id)

        if month:
            month_sale_statistic = month_sale_statistic.filter(
                extract('month', Receipt.created_date) == month)

        if year:
            month_sale_statistic = month_sale_statistic.filter(
                extract('year', Receipt.created_date) == year)

        if kw:
            month_sale_statistic = month_sale_statistic.filter(
                RoomType.name.contains(kw))

        if from_date:
            month_sale_statistic = month_sale_statistic.filter(
                Receipt.created_date.__ge__(from_date))

        if to_date:
            month_sale_statistic = month_sale_statistic.filter(
                Receipt.created_date.__le__(to_date))

        return month_sale_statistic.all()


def room_utilization_report(month=None, year=None, room_name=None, **kwargs):
    with app.app_context():
        checkout_date_column = RoomRental.checkout_date  # Định rõ cột 'checkout_date' để sử dụng trong câu truy vấn

        room_rental = RoomRental.query
        if month and year and room_name:
            room_rental = room_rental.join(Room, Room.id.__eq__(RoomRental.room_id)) \
                .filter(extract('month', checkout_date_column) == month and
                        extract('year', checkout_date_column) == year and
                        Room.name.__eq__(room_name))
        elif month:
            room_rental = room_rental.filter(extract('month', checkout_date_column) == month)
            if year:
                room_rental = room_rental.filter(extract('year', checkout_date_column) == year)
        elif year:
            room_rental = room_rental.filter(extract('year', checkout_date_column) == year)

        count = room_rental.count()

        result = db.session.query(
            Room.name,
            func.sum(extract('day', RoomRental.checkout_date) - extract('day', RoomRental.checkin_date)),
            func.cast((func.count() / count) * 100
                      , Numeric(5, 2))
        ).join(RoomRental, RoomRental.room_id.__eq__(Room.id)).group_by(Room.name).order_by(Room.id)

        if month:
            # Thống kê theo tháng
            result = result.filter(extract('month', checkout_date_column) == month)
        if year:
            # Thống kê theo năm
            result = result.filter(extract('year', checkout_date_column) == year)
        if room_name:
            # Thống kê theo tên phòng
            result = result.filter(Room.name == room_name)

        return result.all()


print(room_utilization_report())
