import math

from flask import render_template, request, redirect, session, jsonify
from appQLKS import app, login
import dao
from flask_login import login_user, logout_user
from appQLKS.models import UserRoles


@app.route("/")
def index():
    room_type = dao.load_room_types()

    page = request.args.get('page', 1)
    room_type_id = request.args.get('room_type_id')
    kw = request.args.get('kw')
    rooms = dao.load_rooms(room_type_id=room_type_id, kw=kw, page=int(page))

    page_size = app.config["PAGE_SIZE"]
    total_room = dao.count_rooms()

    return render_template('index.html', room_types=room_type, rooms=rooms, pages=math.ceil(total_room / page_size))


@app.route("/register", methods=['get', 'post'])
def register_view():
    err_msg = ''

    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if not password.__eq__(confirm):
            err_msg = 'Mật khẩu không khớp!'
        else:
            data = request.form.copy()

            del data['confirm']
            avatar = request.files.get('avatar')
            dao.add_user(avatar=avatar, **data)
            return redirect('/login')

    return render_template('register.html', err_msg=err_msg)


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            return redirect('/')

    return render_template('login.html')


@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username=username, password=password, role=UserRoles.ADMIN)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@app.route("/hotel_homepage")
def hotel_homepage():
    return render_template('hotel_homepage.html')


@app.route('/booking')
def booking():
    return render_template('form_datphong.html')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        from appQLKS import admin

        app.run(debug=True)
