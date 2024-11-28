from appQLKS import db, app
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect

admin = Admin(app, name='hotelbookingapp', template_mode='bootstrap4')