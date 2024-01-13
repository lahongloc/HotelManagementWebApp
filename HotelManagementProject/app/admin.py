from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose, AdminIndexView
from app.models import Room, RoomType, UserRole, RoomRegulation, CustomerTypeRegulation
from app import app, db
from flask_login import current_user, logout_user
from flask import redirect
import dao


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return (current_user.is_authenticated and
                current_user.role.__eq__(UserRole.ADMIN))


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/')

    def is_accessible(self):
        return current_user.is_authenticated


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html',
                           room_regulation=dao.get_room_regulation(),
                           customer_type_regulation=dao.get_customer_type_regulation())

class MonthSaleStatisticView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/monthSaleStatistic.html',
                           monthSaleStatistic=dao.month_sale_statistic())

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN


class MyRoomTypeView(AuthenticatedModelView):
    column_searchable_list = ['name']
    column_filters = ['name']
    column_editable_list = ['name']
    can_export = True
    can_view_details = True
    column_display_pk = True
    column_labels = {
        'name': 'Loại phòng',
        'rooms': 'Danh sách Phòng'
    }
    column_list = ['name', 'rooms']


class MyRoomView(AuthenticatedModelView):
    column_searchable_list = ['name']
    column_filters = ['name', 'room_type']
    column_editable_list = ['name', 'image']
    can_export = True
    can_view_details = True
    column_display_pk = True
    column_labels = {
        'name': 'Phòng',
        'room_type': 'Loại Phòng',
        'image': 'Ảnh Phòng'
    }
    column_list = ['name', 'image', 'room_type']


admin = Admin(app=app,
              name='Hotel management page',
              template_mode='bootstrap4',
              index_view=MyAdminIndexView())


class MyRoomRegulation(AuthenticatedModelView):
    column_searchable_list = ['room_type_id']
    column_filters = ['room_type_id', 'room_quantity', 'capacity', 'price', 'surcharge']
    column_editable_list = ['room_quantity', 'capacity', 'price', 'surcharge']
    can_export = True
    can_view_details = True
    column_display_pk = True
    column_labels = {
        'admin_id': 'Mã Admin',
        'room_type_id': 'Mã Loại phòng',
        'room_quantity': 'Số lượng phòng tối đa',
        'price': 'Đơn giá',
        'capacity': 'Số lượng khách tối đa',
        'surcharge': 'Phụ thu theo số lượng khách'
    }
    column_list = ['admin_id', 'room_type_id', 'room_quantity', 'capacity', 'price', 'surcharge']


class MyCustomerTypeRegulation(AuthenticatedModelView):
    column_searchable_list = ['admin_id']
    column_filters = ['admin_id', 'customer_type_id', 'rate']
    column_editable_list = ['rate']
    can_export = True
    can_view_details = True
    column_display_pk = True
    column_labels = {
        'admin_id': 'Mã Admin',
        'rate': 'Hệ số khách nước ngoài',
        'capacity': 'Số lượng khách tối đa'
    }
    column_list = ['admin_id', 'customer_type_id', 'rate']


admin.add_view(MyRoomTypeView(RoomType, db.session))
admin.add_view(MyRoomView(Room, db.session))
admin.add_view(MyRoomRegulation(RoomRegulation, db.session))
admin.add_view(MyCustomerTypeRegulation(CustomerTypeRegulation, db.session))
admin.add_view(LogoutView(name='Logout'))
admin.add_view(MonthSaleStatisticView(name='Month Sale Statistic'))