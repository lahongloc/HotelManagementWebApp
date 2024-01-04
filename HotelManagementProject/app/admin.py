from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from app.models import *
from app import app, db


class MyRoomTypeView(ModelView):
    column_list = ['name', 'rooms']


class MyRoomView(ModelView):
    column_list = ['name', 'image', 'room_type']


admin = Admin(app=app,
              name='Hotel management page',
              template_mode='bootstrap4')

admin.add_view(MyRoomTypeView(RoomType, db.session))
admin.add_view(MyRoomView(Room, db.session))
