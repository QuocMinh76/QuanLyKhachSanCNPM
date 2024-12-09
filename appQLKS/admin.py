from appQLKS import db, app
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect
from appQLKS.models import UserRoles, Room, RoomType

admin = Admin(app, name='hotelbookingapp', template_mode='bootstrap4')


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRoles.ADMIN)


class RoomTypeView(AuthenticatedView):
    can_export = True
    column_searchable_list = ['id', 'name']
    column_filters = ['id', 'name']
    can_view_details = True
    column_list = ['name', 'rooms']


class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AuthenticatedBaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


admin.add_view(RoomTypeView(RoomType, db.session))
admin.add_view(ModelView(Room, db.session))
admin.add_view(LogoutView(name='Đăng xuất'))