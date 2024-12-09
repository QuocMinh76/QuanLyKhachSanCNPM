from appQLKS import db, app
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect
from appQLKS.models import RoomType, Room


class RoomTypeAdmin(ModelView):
    column_list = ['id', 'name', 'basePrice', 'maxCust', 'overMaxRate']
    column_searchable_list = ['name']
    column_filters = ['name']


class RoomAdmin(ModelView):
    column_list = ['id', 'name', 'description', 'available', 'roomType_id']
    column_searchable_list = ['name']
    column_filters = ['name']


admin = Admin(app, name='hotelbookingapp', template_mode='bootstrap4')

admin.add_view(RoomTypeAdmin(RoomType, db.session))
admin.add_view(RoomAdmin(Room, db.session))
