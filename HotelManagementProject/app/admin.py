from datetime import datetime

from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose, AdminIndexView
from app.models import Room, RoomType, UserRole, RoomRegulation, CustomerTypeRegulation
from app import app, db
from flask_login import current_user, logout_user
from flask import redirect, request
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
        role_admin = None
        if current_user.role == UserRole.ADMIN:
            role_admin = 'ADMIN'
        return self.render('admin/index.html',
                           room_regulation=dao.get_room_regulation(),
                           customer_type_regulation=dao.get_customer_type_regulation(),
                           role_admin=role_admin)


class RoomUtilizationReportView(BaseView):
    @expose('/')
    def index(self):
        name = request.args.get('name')
        month = request.args.get('month')
        year = request.args.get('year')

        room_utilization_report = dao.room_utilization_report(name=name, month=month, year=year)

        return self.render('admin/RoomUtilizationReport.html',
                           room_utilization_report=room_utilization_report)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN


class MonthSaleStatisticView(BaseView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        month = request.args.get('month')
        year = request.args.get('year')

        mss = dao.month_sale_statistic(kw=kw,
                                       from_date=from_date,
                                       to_date=to_date,
                                       month=month,
                                       year=year)
        total_revenue = 0
        for m in mss:
            total_revenue = total_revenue + m[1]

        if not month:
            month = '(1-12)'
        if not year:
            year = '(All)'

        return self.render('admin/monthSaleStatistic.html',
                           monthSaleStatistic=mss,
                           total_revenue=total_revenue,
                           year=year,
                           month=month)

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
admin.add_view(MonthSaleStatisticView(name='Month Sale Statistic'))
admin.add_view(RoomUtilizationReportView(name='Room Utilization Report'))
admin.add_view(LogoutView(name='Logout'))
