import math

import pytz
from flask import render_template, request, redirect, session, jsonify
from appQLKS import app, login
import dao
from flask_login import login_user, logout_user, login_required
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

    return render_template('index.html', room_types=room_type, rooms=rooms,
                           pages=math.ceil(total_room / page_size))


@app.route("/rooms/<room_id>")
def room_details(room_id):
    page = request.args.get('page', 1)

    comments = dao.load_comments(room_id=room_id, page=int(page))

    page_size = app.config["COMMENT_PAGE_SIZE"]
    total_comment = dao.count_comments_of_room(room_id)

    return render_template('room_detail.html', room=dao.get_room_by_id(room_id),
                           comments=comments, pages=math.ceil(total_comment / page_size))


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

            next = request.args.get('next')
            return redirect('/' if next is None else next)

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


@app.route("/rent")
def rent():
    return render_template('rent.html')


@app.route('/booking')
def booking():
    # Lấy danh sách loại phòng
    room_types = dao.load_room_types()

    return render_template('booking.html', room_types=room_types)


@app.route('/booking_confirm')
def booking_confirm():

    return render_template('booking_confirm.html')


@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    room_type_id = request.args.get('room_type_id')
    rooms = dao.get_rooms_by_type(room_type_id)

    room_list = []
    for room, type_name in rooms:
        room_data = {
            "id": room.id,
            "name": room.name,
            "description": room.description,
            "image": room.image,
            "status": "Available" if room.available else "Unavailable",
            "price": room.roomPrice,
            "type": room.roomType_id,
            "type_name": type_name
        }
        room_list.append(room_data)

    return jsonify(room_list)


@app.route("/api/rooms/<room_id>/comments", methods=['post'])
@login_required
def add_comment(room_id):
    c = dao.add_comment(content=request.json.get('content'), room_id=room_id)

    created_date_utc = c.created_date.astimezone(pytz.utc)

    return jsonify({
        "id": c.id,
        "content": c.content,
        "created_date": created_date_utc,
        "user": {
            "avatar": c.user.avatar,
            "name": c.user.name
        }
    })


@app.route("/thanhtoan")
def thanh_toan():
    return render_template('thanhtoan.html')


@app.route('/find_order')
def find_booking_order():
    kw = request.args.get('kw')

    orders = dao.load_booking_orders(kw)

    return render_template('find_booking_order.html', orders=orders)


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        from appQLKS import admin

        app.run(debug=True)
