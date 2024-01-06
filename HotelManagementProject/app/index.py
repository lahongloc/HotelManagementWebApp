from app import app, dao, login, utils
from flask import render_template, request, redirect, url_for, jsonify, session
from flask_login import login_user, logout_user, current_user, AnonymousUserMixin
import cloudinary.uploader


@app.route('/')
def home():
    room_types = dao.get_room_types()
    rooms_info = dao.get_rooms_info()
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
                err_msg = ''
                return render_template('login.html')
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
            return redirect(url_for('home'))
        else:
            err_msg = 'Username or Password is incorrect!!!'

    return render_template('login.html', err_msg=err_msg)


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
    room = dao.get_rooms_info(room_id=room_id)

    customer_type = dao.get_customer_type()
    role_cus = dao.get_customer_role()
    total_price = None
    if request.method.__eq__('POST'):
        reservation_info = {room_id: {
            'users': {},
            'total_price': 0.0
        }}

        user = {}
        count = 0
        user_counter = 0
        customer_info = request.form.to_dict()
        customer_info.popitem()
        customer_info.popitem()
        for i in customer_info:
            user[i] = request.form.get(i)
            count += 1
            if count == 3:
                count = 0
                user_counter += 1
                reservation_info[room_id]['users'][f'user{user_counter}'] = user
                user = {}
        session['reservation_info'] = utils.calculate_total_reservation_price(reservation_info=reservation_info,
                                                                              room_id=room_id)
        return redirect(url_for('pay_for_reservation', room_id=room_id))

    return render_template('booking.html',
                           room=room,
                           customer_type=customer_type,
                           role_cus=role_cus,
                           total_price=total_price)


@app.routegit ('/reservation-paying')
def pay_for_reservation():
    room_id = str(request.args.get('room_id'))
    return render_template('payReservation.html', room_id=room_id)


@app.context_processor
def common_response():
    return {
        'reservation_info': session.get('reservation_info')
    }


if __name__ == "__main__":
    from app.admin import *

    app.run(debug=True)
