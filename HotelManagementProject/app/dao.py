from app.models import *
from app import app


def get_room_types():
    with app.app_context():
        room_types = RoomType.query.all()
        return room_types

