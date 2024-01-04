from app.models import *
from app import app


def get_room_types():
    with app.app_context():
        room_types = RoomType.query.all()
        return room_types


def get_rooms():
    with app.app_context():
        rooms = Room.query.all()
        return rooms


def get_rooms_info(room_id=None):
    with app.app_context():
        rooms_info = db.session.query(Room.name, Room.id, Room.image, RoomType.name.label('room_type'), RoomRegulation.price,
                                      RoomRegulation.room_quantity) \
            .join(Room, Room.room_type_id.__eq__(RoomType.id)) \
            .join(RoomRegulation, RoomRegulation.room_type_id.__eq__(RoomType.id))

        if room_id:
            rooms_info = rooms_info.filter(Room.id.__eq__(room_id)).first()
            return rooms_info

        return rooms_info.all()


print(get_rooms_info(room_id=2))
