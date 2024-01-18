import hashlib
import json
import random
from datetime import datetime
# from mysql.connector import cursor

from app import app, dao, login, utils
from flask import render_template, request, redirect, url_for, jsonify, session, flash, abort
from flask_login import login_user, logout_user, current_user, login_required
import cloudinary.uploader

from app.dao import vnpay
from app.models import UserRole, Receipt


@app.route('/')
def home():
    kw = request.args.get('kw')
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')
    room_type = request.args.get('roomType')

    if checkin and checkout:
        checkin = datetime.strptime(checkin, "%Y-%m-%dT%H:%M")
        checkout = datetime.strptime(checkout, "%Y-%m-%dT%H:%M")

    room_types = dao.get_room_types()
    rooms_info = dao.get_rooms_info(kw=kw, checkin=checkin, checkout=checkout, room_type=room_type)
    return render_template('index.html',
                           room_types=room_types,
                           rooms_info=rooms_info)


@app.route('/user-register', methods=['get', 'post'])
def user_register():
    role_cus = dao.get_customer_role()
    err_msg = ''
    if request.method.__eq__('POST'):
        customer_type = str(request.form.get('customer_type'))
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        email = request.form.get('email')
        phone = request.form.get('phone')
        gender = request.form.get('gender') == "Man"
        id_num = request.form.get('idNum')
        avatar_path = None

        if password.strip().__eq__(confirm.strip()):
            try:
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']

                utils.add_user(customer_type=customer_type,
                               name=name,
                               gender=gender,
                               username=username,
                               password=password,
                               email=email,
                               phone=phone,
                               avatar=avatar_path,
                               id_num=id_num)
                return render_template('login.html',
                                       done_register='Registration successful, please log in to experience!')
            except Exception as ex:
                if '1062' in (str(ex)):
                    err_msg = 'Username, email or phone already existed!'
                else:
                    err_msg = str(ex)
        else:
            err_msg = 'Confirmed password is MISMATCH!'

    return render_template('register.html',
                           role_cus=role_cus, err_msg=err_msg)


@app.route('/login', methods=['get', 'post'])
def user_signin():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)

            if current_user.role == UserRole.ADMIN:
                return redirect('/admin')
            elif current_user.role == UserRole.RECEPTIONIST:
                return redirect(url_for('room_renting'))
            else:
                return redirect(url_for('home'))
        else:
            err_msg = 'Username or Password is incorrect!!!'

    return render_template('login.html', err_msg=err_msg)


@app.route('/forgot-password', methods=['get', 'post'])
def user_reset_password():
    notice = ''
    err_msg = ''
    done_otp = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')

        user = utils.get_user_by_username(username)

        if user:
            session['send_otp'] = send_otp(user)
            session['username'] = username
            print(session['send_otp'])
            print(session['username'])

            return render_template("forgotPassword.html", code_otp=session['send_otp'], done_otp='1')
        else:
            err_msg = 'Username not found, please try again!!'

    return render_template('forgotPassword.html', err_msg=err_msg)


def send_otp(user):
    otp_send = str(random.randint(100000, 999999))

    subject = "Password Reset Request for Your Dau Cung Duoc Hotel Account"

    message = "OTP Code: " + otp_send

    dao.send_gmail(user.email, subject, message)

    return otp_send


@app.route('/forgot-password1', methods=['get', 'post'])
def user_confirm_password():
    err_msg = ''
    if request.method.__eq__('POST'):
        otp = str(request.form.get('otp'))
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        try:
            if otp.__eq__(session['send_otp']):
                if str(password).strip().__eq__(str(confirm).strip()):
                    u = utils.get_user_by_username(session['username'])
                    u.password = str(hashlib.md5(str(password).encode('utf-8')).hexdigest())
                    db.session.add(u)
                    db.session.commit()
                    return render_template('login.html', change_pass='Password changed successfully!!!')

                else:
                    return render_template("forgotPassword.html",
                                           err_msg='Confirmed password is MISMATCH!',
                                           done_otp='1')
            else:
                return render_template("forgotPassword.html",
                                       err_msg='OTP code is incorrect!',
                                       done_otp='1')
        except Exception as ex:
            err_msg = str(ex)

    return render_template('forgotPassword.html', err_msg=err_msg)


@app.route('/personal-page', methods=['get', 'post'])
def personal_page():
    err_msg = ''
    avatar_path = None
    try:
        if request.method.__eq__('POST'):
            username = request.form.get('username')
            name = request.form.get('name')
            email = request.form.get('email')
            avatar = request.files.get('avatar')
            gender = request.form.get('gender') == "Man"
            phone = request.form.get('phone')
            identification = request.form.get('identification')
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']
            u = utils.get_user_by_username(current_user.username)

            u.gender = gender
            if email:
                u.email = email
            if avatar:
                u.avatar = avatar_path
            if phone:
                u.phone = phone

            c = utils.get_customer_by_user()

            if name:
                c.name = name
            if identification:
                c.identification = identification

            db.session.add_all([u, c])
            db.session.commit()
            return render_template('personalPage.html', full_user_info=dao.get_full_user_info())
        else:
            full_user_info = dao.get_full_user_info()
            return render_template('personalPage.html', full_user_info=full_user_info)
    except Exception as ex:
        err_msg = str(ex)

    return render_template('personalPage.html', err_msg=err_msg, full_user_info=dao.get_full_user_info())


@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    return data


@app.route('/rooms/<room_id>')
def room_details(room_id):
    room = dao.get_rooms_info(room_id=room_id)
    return render_template('roomDetail.html', room=room)


@app.route("/booking-room/<room_id>", methods=['post', 'get'])
def room_booking(room_id):
    err_msg = ''
    room = dao.get_rooms_info(room_id=room_id)

    customer_info = dao.get_customer_info()
    role_cus = dao.get_customer_role()

    total_price = None
    if request.method.__eq__('POST'):
        reservation_info = {room_id: {
            'users': {},
            'total_price': 0.0,
            'checkin_time': request.form.get('checkin'),
            'checkout_time': request.form.get('checkout')
        }}

        user = {}
        count = 0
        user_counter = 0
        customers_list = request.form.to_dict()
        customers_list.popitem()
        customers_list.popitem()
        for i in customers_list:
            user[str(i)[:-1]] = request.form.get(i)
            count += 1
            if count == 3:
                count = 0
                user_counter += 1
                reservation_info[room_id]['users'][user_counter] = user
                user = {}

        checkin_time = datetime.strptime(str(reservation_info[str(room_id)]['checkin_time']), "%Y-%m-%dT%H:%M")
        checkout_time = datetime.strptime(str(reservation_info[str(room_id)]['checkout_time']), "%Y-%m-%dT%H:%M")
        is_valid = utils.check_reservation(checkin_time=checkin_time, checkout_time=checkout_time, room_id=room_id)
        # print(reservation_info)
        if is_valid:
            session['reservation_info'] = utils.calculate_total_reservation_price(reservation_info=reservation_info,
                                                                                  room_id=room_id)
            return redirect(url_for('pay_for_reservation', room_id=room_id))
        else:
            err_msg = 'This time is not available for this room. Please choose another time period!'

    return render_template('booking.html',
                           room=room,
                           customer_info=customer_info,
                           role_cus=role_cus,
                           total_price=total_price,
                           err_msg=err_msg,
                           is_booking=True)


@app.route('/reservation-paying')
def pay_for_reservation():
    room_id = str(request.args.get('room_id'))
    room_info = dao.get_rooms_info(room_id=room_id)
    return render_template('payReservation.html', room_info=room_info, room_id=room_id)


@app.route('/api/reservation-paying', methods=['POST'])
def api_of_reservation_pay():
    data = request.json
    code = 200
    try:
        customers = data.get('reservationInfo')[str(data['room_id'])]['users']
        checkin_time = data.get('reservationInfo')[str(data['room_id'])]['checkin_time']
        checkout_time = data.get('reservationInfo')[str(data['room_id'])]['checkout_time']
        total_price = data.get('reservationInfo')[str(data['room_id'])]['total_price']

        is_paid = dao.add_customers(customers=customers,
                                    room_id=data['room_id'],
                                    checkin_time=checkin_time,
                                    checkout_time=checkout_time,
                                    total_price=total_price)
        if not is_paid:
            code = 400
    except Exception as ex:
        print(str(ex))
        code = 400
    return jsonify({
        'code': code
    })


@app.route('/api/check-cus-type', methods=['POST'])
def handle_check_cus_type():
    try:
        data = request.json
        cus_info = None
        err_msg = 200
        try:
            cus_info = utils.get_cus_type_by_identification(identification=str(data.get('identification')))
        except Exception as ex:
            print(str(ex))
            err_msg = 400
        if not cus_info:
            err_msg = 400
        return jsonify({
            'cusType': cus_info.type,
            'cusName': cus_info.name,
            'code': err_msg
        })
    except Exception as ex:
        print(str(ex))
        return jsonify({
            'code': 400
        })


@login_required
@app.route('/renting-room', methods=['POST', 'GET'])
def room_renting():
    err_msg = ''
    if current_user.role != UserRole.RECEPTIONIST:
        return redirect(url_for('home'))
    room_id = request.args.get('room_id', 1)
    room = dao.get_rooms_info(room_id=room_id)

    booked_rooms = None
    role_cus = dao.get_customer_role()

    room_types = dao.get_room_types()
    rooms_info = dao.get_rooms_info()
    booked_rooms_detail = dao.get_booked_rooms()
    if request.method.__eq__('POST'):
        identification = request.form.get('identification')
        booked_rooms = utils.get_booked_rooms_by_identification(identification=identification)

        room_id = request.form.get('room_id', room_id)
        data = request.form.to_dict()
        try:
            room_rental_info = {room_id: {
                'users': {},
                'total_price': 0.0,
                'checkout_time': request.form.get('checkout')
            }}
            user = {}
            count = 0
            data.popitem()
            user_counter = 0
            for i in data:
                user[str(i)[:-1]] = request.form.get(i)
                count += 1
                if count == 3:
                    count = 0
                    user_counter += 1
                    room_rental_info[room_id]['users'][user_counter] = user
                    user = {}
            # print(room_rental_info)
            checkout_time = datetime.strptime(str(room_rental_info[str(room_id)]['checkout_time']), "%Y-%m-%dT%H:%M")
            room_rental_info = utils.calculate_total_reservation_price(reservation_info=room_rental_info,
                                                                       room_id=room_id)

            if utils.check_reservation(checkout_time=checkout_time, room_id=room_id, is_renting=True):
                dao.receptionist_room_rental(room_rental_info=room_rental_info, checkout_time=checkout_time,
                                             room_id=room_id)
            else:
                err_msg = 'This time is not available for this room. Please choose another time period!'
        except Exception as ex:
            print(str(ex))

    return render_template('renting.html',
                           booked_rooms=booked_rooms,
                           booked_rooms_detail=booked_rooms_detail,
                           rooms_info=rooms_info,
                           room=room,
                           room_types=room_types,
                           role_cus=role_cus,
                           is_renting=True,
                           err_msg=err_msg)


@app.route('/api/take-room-info', methods=['POST'])
def take_room_info():
    data = request.json
    room_id = data.get('roomId')
    room = dao.get_rooms_info(room_id=room_id)
    return jsonify({
        'roomName': room.name,
        'roomType': room.room_type,
        'price': room.price
    })


@app.route('/api/room-renting', methods=['POST'])
def handel_room_renting():
    err_msg = 200
    data = request.json
    try:
        reservation_id = int(data.get('reservationId'))
        dao.create_room_rental(reservation_id=reservation_id)
    except Exception as ex:
        err_msg = 400
        print(str(ex))
    return jsonify({
        'code': err_msg
    })


@app.context_processor
def common_response():
    return {
        'reservation_info': session.get('reservation_info')
    }


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        order_desc = request.form.get('order_desc')
        rental_room_id = request.form.get('rental_room_id')
        # order_type = request.form.get('order_type')
        amount = int(request.form.get('amount')) * 100

        vnp = vnpay()
        # Xây dựng hàm cần thiết cho vnpay
        vnp.requestData['vnp_Version'] = '2.1.0'
        vnp.requestData['vnp_Command'] = 'pay'
        vnp.requestData['vnp_TmnCode'] = 'PMAKVMOW'
        vnp.requestData['vnp_Amount'] = amount
        vnp.requestData['vnp_CurrCode'] = 'VND'
        vnp.requestData['vnp_TxnRef'] = str(rental_room_id) + '-' + datetime.now().strftime('%Y%m%d%H%M%S')
        vnp.requestData['vnp_OrderInfo'] = order_desc  # Nội dung thanh toán
        vnp.requestData['vnp_OrderType'] = 'order_type'

        vnp.requestData['vnp_Locale'] = 'vn'

        vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
        vnp.requestData['vnp_IpAddr'] = "127.0.0.1"
        vnp.requestData['vnp_ReturnUrl'] = url_for('vnpay_return', _external=True)

        # Lưu thông tin cần thiết vào session
        session['rental_room_id'] = rental_room_id
        session['amount'] = amount

        vnp_payment_url = vnp.get_payment_url('https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
                                              'USYEHCIUSVVCFQYKBQBZSUASXUXRSTCS')

        return redirect(vnp_payment_url)

    return render_template('payment.html')


@app.route('/vnpay_return', methods=['GET'])
def vnpay_return():
    vnp_TransactionNo = request.args.get('vnp_TransactionNo')
    vnp_TxnRef = request.args.get('vnp_TxnRef')
    vnp_Amount = request.args.get('vnp_Amount')
    vnp_ResponseCode = request.args.get('vnp_ResponseCode')

    if vnp_ResponseCode == '00':
        rental_room_id = session.get('rental_room_id')
        amount = session.get('amount')

        rc = Receipt(rental_room_id=rental_room_id, total_price=amount, created_date=datetime.now())
        db.session.add(rc)
        db.session.commit()

        flash('Thanh toán thành công!')
    else:
        flash('Lỗi thanh toán. Vui lòng thử lại!')

    # Xóa thông tin từ session để tránh lưu trữ không cần thiết
    session.pop('order_desc', None)
    session.pop('rental_room_id', None)
    session.pop('amount', None)

    return redirect(url_for('user_signin'))


def calculate_total_price(rental_room, roomPrice, customers):
    has_foreign_customer = any(customer['customer_type'] == 'FOREIGN' for customer in customers)
    total = rental_room.calculate_rental_days() * roomPrice
    if has_foreign_customer:
        total *= 1.5
    if len(customers) > 2:
        total *= .25
    if rental_room.deposit != None:
        total -= rental_room.deposit
    return total


@app.route('/renting-room/payment/<rental_room_id>', methods=['GET', 'POST'])
def renting_room(rental_room_id):
    if current_user.role != UserRole.RECEPTIONIST:
        return redirect(url_for('home'))
    rental_room = dao.get_rental_room_by_id(rental_room_id)
    booked_room = dao.get_room_by_id(rental_room.room_id)
    room_type = dao.get_room_type_by_id(booked_room.room_type_id)
    room_regulation = dao.get_room_regulation_by_room_type_id(room_type.id)
    customers = dao.get_rental_room_customers(rental_room_id)
    total = calculate_total_price(rental_room, room_regulation.price, customers)

    if request.method == 'POST':
        username = request.form.get('customer_pay')
        customer_pay = dao.get_customer_by_username(username)
        pay_method = request.form.get('payment_method')

        if pay_method == 'cash':
            if customer_pay:
                receipt_id = dao.create_receipt(customer_pay.id, rental_room_id, total)

                return redirect(url_for('payment_success', receipt_id=receipt_id))
        elif pay_method == 'vnpay':
            vnp = vnpay()

            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = 'PMAKVMOW'
            vnp.requestData['vnp_Amount'] = total
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = f'{rental_room_id}-{datetime.now().strftime("%Y%m%d%H%M%S")}'
            vnp.requestData['vnp_OrderInfo'] = 'Payment for rental room'
            vnp.requestData['vnp_OrderType'] = 'order_type'

            vnp.requestData['vnp_Locale'] = 'vn'

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
            vnp.requestData['vnp_IpAddr'] = "127.0.0.1"
            vnp.requestData['vnp_ReturnUrl'] = url_for('renting_room_vnpay_return', _external=True)

            session['vnp_payment_info'] = {
                'rental_room_id': rental_room_id,
                'amount': total,
            }

            dao.create_receipt(customer_pay.id, rental_room_id, total)

            vnp_payment_url = vnp.get_payment_url('https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
                                                  'your_query_secure_hash_key')

            return redirect(vnp_payment_url)

    return render_template('rctPayment.html', rental_room=rental_room,
                           booked_room=booked_room,
                           room_type=room_type.name,
                           room_regulation=room_regulation,
                           customers=customers,
                           total=total)


@app.route('/renting-room/payment/<rental_room_id>/vnpay_return', methods=['GET'])
def renting_room_vnpay_return(rental_room_id):
    vnp_TransactionNo = request.args.get('vnp_TransactionNo')
    vnp_TxnRef = request.args.get('vnp_TxnRef')
    vnp_Amount = request.args.get('vnp_Amount')
    vnp_ResponseCode = request.args.get('vnp_ResponseCode')

    if vnp_ResponseCode == '00':
        payment_info = session.get('vnp_payment_info')
        rental_room_id = payment_info.get('rental_room_id')
        amount = payment_info.get('amount')

        flash('Payment successful!')
    else:
        flash('Error when try to paying via VNPay!')

    session.pop('vnp_payment_info', None)

    return redirect(url_for('vnpay_return'))


@app.route('/payment_success/<receipt_id>')
def payment_success(receipt_id):
    receipt = dao.get_receipt_by_id(receipt_id)
    rental_room = dao.get_rental_room_by_id(receipt.rental_room_id)
    customer = dao.get_customer_by_id(receipt.customer_id)
    room = dao.get_room_by_id(rental_room.room_id)

    return render_template('paymentSuccessful.html',
                           receipt=receipt, rental_room=rental_room, customer=customer, room=room)


if __name__ == "__main__":
    from app.admin import *

    app.run(debug=True)
