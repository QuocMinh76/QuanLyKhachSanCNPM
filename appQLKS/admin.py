from appQLKS import db, app
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect
from appQLKS.models import RoomType, Room, CustomerType, UserRoles


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRoles.ADMIN)


class RoomTypeView(ModelView):
    can_export = True
    column_list = ['id', 'name', 'basePrice', 'maxCust', 'overMaxRate', 'rooms']
    column_searchable_list = ['name']
    column_filters = ['name']
    can_view_details = True


class RoomView(ModelView):
    column_list = ['id', 'name', 'description', 'roomPrice', 'available', 'image', 'roomType_id']
    column_searchable_list = ['name']
    column_filters = ['name']
    can_view_details = True


class CustomerTypeView(ModelView):
    column_list = ['id', 'cust_type', 'cust_rate']
    column_searchable_list = ['cust_type']
    column_filters = ['cust_type']
    can_view_details = True


class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AuthenticatedBaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


class StatsView(AuthenticatedBaseView):
    @expose("/")
    def index(self):
        return self.render('admin/stats.html')


admin = Admin(app, name='Hotel Admin Page', template_mode='bootstrap4')
admin.add_view(RoomTypeView(RoomType, db.session, name='Loại phòng'))
admin.add_view(RoomView(Room, db.session, name='Phòng'))
admin.add_view(CustomerTypeView(CustomerType, db.session, name='Loại KH'))
admin.add_view(StatsView(name='Thống kê - Báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))
