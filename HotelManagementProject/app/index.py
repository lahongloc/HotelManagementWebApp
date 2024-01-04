from app import app, dao
from flask import render_template, request


@app.route('/')
def home():
    room_types = dao.get_room_types()
    rooms_info = dao.get_rooms_info()
    return render_template('index.html',
                           room_types=room_types,
                           rooms_info=rooms_info)


@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    return data


@app.route('/rooms/<room_id>')
def room_details(room_id):
    room = dao.get_rooms_info(room_id=room_id)
    return render_template('roomDetail.html', room=room)


@app.route("/booking-room/<room_id>")
def room_booking(room_id):
    room = dao.get_rooms_info(room_id=room_id)
    return render_template('booking.html', room=room)


if __name__ == "__main__":
    from app.admin import *

    app.run(debug=True)
