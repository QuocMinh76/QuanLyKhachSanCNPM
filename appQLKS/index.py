import math
import pytz
from flask import render_template, request, redirect, session, jsonify
from appQLKS import app, login
import dao
from flask_login import login_user, logout_user, login_required
from appQLKS.models import UserRoles
from datetime import datetime


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


@app.route('/booking')
@login_required
def booking():
    # Lấy danh sách loại phòng
    room_types = dao.load_room_types()
    cust_types = dao.load_customer_type()
    current_date = datetime.now()

    return render_template('booking.html', room_types=room_types,
                           cust_types=cust_types, date=current_date)


@app.route('/booking_confirm')
@login_required
def booking_confirm():
    return render_template('booking_confirm.html')


@app.route('/process_booking', methods=['POST'])
@login_required
def process_booking():
    user_id = request.form.get('id')
    checkin = request.form.get('checkin')
    checkout = request.form.get('checkout')
    selected_rooms = request.form.get('selected_rooms')
    customers = request.form.get('customers')

    try:
        dao.process_booking_order(
            user_id=user_id,
            checkin=checkin,
            checkout=checkout,
            customers=customers,
            selected_rooms=selected_rooms
        )
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return "Invalid input data", 400
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your booking", 500

    return redirect('/')


@app.route("/rent/<order_id>")
def rent(order_id):
    booking_order = dao.get_booking_order_details(order_id)
    custs = []
    rooms = []

    for room_info in booking_order.booking_room_info:
        room = dao.get_room_by_id(room_info.room_id)
        rooms.append(room)

    for cust_info in booking_order.booking_cust_info:
        cust = dao.get_customer_by_id(cust_info.cust_id)
        custs.append(cust)

    # Create a dictionary mapping room ID to maxCust for each room
    room_data = {room.id: room.roomType.maxCust for room in rooms}

    return render_template('rent.html', order=booking_order, customers=custs,
                           rooms=rooms, num_cust=len(custs), num_room=len(rooms), room_data=room_data)


@app.route('/process_renting', methods=['POST'])
@login_required
def process_renting():
    order_id = request.form.get('id')
    checkin_date = request.form.get('checkin_date')
    checkout_date = request.form.get('checkout_date')

    room_cust_data = request.form.get('cust_room')

    try:
        dao.process_renting_order(
            order_id=order_id,
            checkin=checkin_date,
            checkout=checkout_date,
            rooms_custs=room_cust_data
        )
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return "Invalid input data", 400
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing the renting order", 500

    return redirect('/')


@app.route("/invoice/<order_id>")
def invoice(order_id):
    booking_order = dao.get_booking_order_details(order_id)
    renting_order = dao.get_renting_order_details(order_id)

    num_room = len(booking_order.booking_room_info)
    num_cust = len(booking_order.booking_cust_info)

    renting_details = renting_order.details
    print(renting_details)

    return render_template('invoice.html', b_order=booking_order, r_order=renting_order,
                           details=renting_details, num_cust=num_cust, num_room=num_room)


@app.route('/find_order')
def find_booking_order():
    kw = request.args.get('kw')

    orders = dao.load_booking_orders(kw)

    return render_template('find_booking_order.html', orders=orders)


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


@app.route('/api/customer_types', methods=['GET'])
def get_customer_types():
    cust_types = dao.load_customer_type()
    # Convert the list of customer types into a dictionary that can be easily used in JavaScript
    response = jsonify([{'id': type.id, 'name': type.name} for type in cust_types])
    response.headers['Content-Type'] = 'application/json'  # Set content type explicitly
    return response


@app.route("/find_rent")
def find_rent():
    kw = request.args.get('kw')

    orders = dao.load_renting_orders(kw)

    return render_template('find_rent.html', orders=orders)


@app.route("/find_rent_print")
def find_rent_print():
    kw = request.args.get('kw')

    orders = dao.load_renting_orders(kw)

    return render_template('find_rent_print.html', orders=orders)


@app.route("/customer_orders")
def customer_orders():
    return render_template('customer_orders.html')


@app.route("/customer_order_details")
def customer_order_details():
    return render_template('customer_order_details.html')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        from appQLKS import admin

        app.run(debug=True)
