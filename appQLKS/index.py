import math
import os
import pytz
from flask import render_template, request, redirect, session, jsonify, send_file, make_response, Response
from flask_admin.form.rules import HTML
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
from flask import render_template, request, redirect, session, jsonify
from appQLKS import app, login, db
import dao
from flask_login import login_user, logout_user, login_required, current_user
from appQLKS.models import UserRoles, Bill, RentingDetails, RentingOrder, RoomType
from datetime import datetime
from io import BytesIO


@app.route("/")
def index():
    room_type = dao.load_room_types()

    page = request.args.get('page', 1)
    room_type_id = request.args.get('room_type')
    kw = request.args.get('kw')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    rooms = dao.load_rooms(room_type_id=room_type_id, kw=kw, min_price=min_price,
                           max_price=max_price, page=int(page))

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
    msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)

            next = request.args.get('next')
            return redirect('/' if next is None else next)
        else:
            msg = 'Tên đăng nhập hoặc mật khẩu không đúng!'

    return render_template('login.html', msg=msg)


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

    renting_details = dao.get_renting_order_room_details(order_id)

    total_price = dao.calculate_total_price_for_renting_order(order_id)

    return render_template('invoice.html', b_order=booking_order, r_order=renting_order,
                           details=renting_details, num_cust=num_cust, num_room=num_room, total_price=total_price)


@app.route('/process_invoice', methods=['POST'])
@login_required
def process_invoice():
    order_id = request.form.get('order_id')
    checkin_date = request.form.get('checkin_date')
    checkout_date = request.form.get('checkout_date')
    total_domestic_cust = int(request.form.get('total_domestic_cust'))
    total_foreign_cust = int(request.form.get('total_foreign_cust'))
    total_price = request.form.get('total_price')

    dao.process_bill(
        order_id=order_id,
        checkin=checkin_date,
        checkout=checkout_date,
        total_domestic_cust=total_domestic_cust,
        total_foreign_cust=total_foreign_cust,
        total_price=total_price
    )

    return redirect('/')


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
    for room, type_name, max_cust in rooms:
        room_data = {
            "id": room.id,
            "name": room.name,
            "description": room.description,
            "image": room.image,
            "status": "Available" if room.available else "Unavailable",
            "price": room.roomPrice,
            "type": room.roomType_id,
            "type_name": type_name,
            "max_cust": max_cust
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


@app.route("/find_bill")
def find_bill():
    kw = request.args.get('kw')

    bills = dao.load_bills(kw)

    return render_template('find_bill.html', bills=bills)


@app.route("/customer_orders")
@login_required
def customer_orders():
    bills = dao.get_bills_of_user(current_user.id)

    return render_template('customer_orders.html', bills=bills)


@app.route("/customer_order_details/<bill_id>")
def customer_order_details(bill_id):
    bill = dao.get_bill_by_id(bill_id)
    booking_order = dao.get_booking_order_details(bill_id)

    renting_details = dao.get_renting_order_room_details(bill_id)

    total_price = dao.calculate_total_price_for_renting_order(bill_id)

    return render_template('customer_order_details.html', bill=bill,
                           num_room=len(booking_order.booking_room_info),
                           num_cust=len(booking_order.booking_cust_info),
                           details=renting_details, price=total_price)


@app.route('/api/update_rooms_status', methods=['POST'])
def update_rooms_status():
    data = request.get_json()
    print('Dữ liệu nhận được từ client:', data)

    if 'rooms' in data:
        rooms = data['rooms']
        success = True

        # Duyệt qua các phòng đã đặt và cập nhật trạng thái trong cơ sở dữ liệu
        for room in rooms:
            room_id = room.get('id')
            print(f'Cập nhật trạng thái cho phòng ID {room_id}')
            # Giả sử bạn có phương thức `update_room_status` để cập nhật trạng thái phòng trong DB
            success = dao.update_room_status(room_id, available=False)
            if not success:
                break  # Nếu có lỗi trong quá trình cập nhật, thoát vòng lặp

        if success:
            print('Cập nhật trạng thái phòng thành công.')
            return jsonify({'success': True})
        else:
            print('Lỗi trong quá trình cập nhật trạng thái phòng.')
            return jsonify({'success': False, 'message': 'Không thể cập nhật trạng thái phòng'})
    else:
        print('Dữ liệu không hợp lệ:', data)
        return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'})


@app.route('/api/monthly_statistics', methods=['GET'])
def get_monthly_statistics():
    month = request.args.get('month')
    if not month:
        return jsonify({'error': 'Month parameter is required'}), 400

    statistics = dao.get_monthly_statistics(month)
    return jsonify(statistics)


# Đăng ký font hỗ trợ Unicode (DejaVuSans)
font_path = os.path.join('static', 'fonts', 'DejaVuSerif.ttf')
pdfmetrics.registerFont(TTFont('DejaVuSerif', font_path))


@app.route('/export-pdf/<order_id>')
def export_pdf(order_id):
    order = dao.get_renting_order_by_id(order_id)
    booking_order = dao.get_booking_order_details(order_id)
    rooms = [dao.get_room_by_id(room_info.room_id) for room_info in booking_order.booking_room_info]
    custs = [dao.get_customer_by_id(cust_info.cust_id) for cust_info in booking_order.booking_cust_info]
    data = dao.get_room_cust_info_of_renting_order(order_id)

    if not order:
        return "Phiếu thuê không tồn tại", 404

    # Tạo file PDF
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Định nghĩa style chung
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName='DejaVuSerif',
        fontSize=14,
        alignment=1,  # Căn giữa
    )

    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontName='DejaVuSerif',
        fontSize=10,
        leading=12,
        wordWrap='CJK',  # Tự động xuống dòng
        alignment=1,  # Căn trái
    )

    elements = []

    # Tiêu đề
    elements.append(Paragraph("PHIẾU THUÊ PHÒNG", title_style))
    elements.append(Paragraph("<br/><br/>", content_style))
    elements.append(Paragraph("<br/><br/>", content_style))

    # Thông tin cơ bản
    basic_info_data = [
        ["Nhân viên lập phiếu", "Ngày nhận phòng", "Ngày trả phòng", "Số lượng khách thuê", "Số lượng phòng thuê"],
        [current_user.name, order.checkin_date.strftime('%d/%m/%Y'), order.checkout_date.strftime('%d/%m/%Y'),
         len(custs), len(rooms)]
    ]
    basic_info_table = Table(basic_info_data, colWidths=[140, 100, 100, 130, 130])
    basic_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSerif'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(basic_info_table)

    new_custom_style = styles['Normal']
    new_custom_style.fontName = 'DejaVuSerif'  # Sử dụng font DejaVuSerif
    new_custom_style.fontSize = 11  # Kích thước chữ nhỏ hơn
    new_custom_style.alignment = 1  # Căn trái


    # Thêm dòng trống
    elements.append(Paragraph("<br/><br/>", content_style))
    elements.append(Paragraph("Các phòng thuê: " + ", ".join(room.name for room in rooms), new_custom_style))
    elements.append(Paragraph("<br/><br/>", content_style))
    # Danh sách khách hàng
    customer_data = [["Tên khách hàng", "Loại khách hàng", "CMND", "Địa chỉ", "Phòng"]]
    for item in data:
        room_id = item['room_id']
        cust_id = item['cust_id']
        customer = dao.get_customer_by_id(cust_id)
        room = dao.get_room_by_id(room_id)
        customer_row = [
            Paragraph(customer.cust_name, content_style),
            Paragraph(customer.custType.name, content_style),
            Paragraph(customer.custIdentity_num, content_style),
            Paragraph(customer.custAddress, content_style),
            Paragraph(room.name, content_style)
        ]
        customer_data.append(customer_row)

    customer_table = Table(customer_data, colWidths=[140, 100, 100, 130, 130])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSerif'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(customer_table)
    elements.append(Paragraph("<br/><br/>", content_style))

    # Lời cảm ơn
    elements.append(Paragraph(
        "Cảm ơn quý khách đã sử dụng dịch vụ thuê phòng khách sạn của chúng tôi!",
        content_style
    ))

    # Tạo PDF
    pdf.build(elements)
    buffer.seek(0)

    # Trả về file PDF
    return send_file(buffer, as_attachment=True, download_name=f"phieu_thue_{order.id}.pdf", mimetype='application/pdf')


@app.route('/export_invoice/<order_id>')
def export_invoices(order_id):
    order = dao.get_bill_by_id(order_id)
    booking_order = dao.get_booking_order_details(order_id)
    rooms = [dao.get_room_by_id(room_info.room_id) for room_info in booking_order.booking_room_info]
    custs = [dao.get_customer_by_id(cust_info.cust_id) for cust_info in booking_order.booking_cust_info]
    total_price = dao.calculate_total_price_for_renting_order(order_id)
    renting_details = dao.get_renting_order_room_details(order_id)

    if not order:
        return "Phiếu thuê không tồn tại", 404

    # Tạo file PDF
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Định nghĩa style chung
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName='DejaVuSerif',
        fontSize=14,
        alignment=1,  # Căn giữa
    )

    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontName='DejaVuSerif',
        fontSize=10,
        leading=12,
        wordWrap='CJK',  # Tự động xuống dòng
        alignment=1,  # Căn trái
    )

    elements = []

    # Tiêu đề
    elements.append(Paragraph("HÓA ĐƠN THANH TOÁN", title_style))
    elements.append(Paragraph("<br/><br/>", content_style))
    elements.append(Paragraph("<br/><br/>", content_style))

    # Thông tin cơ bản
    basic_info_data = [
        ["Nhân viên lập phiếu", "Ngày nhận phòng", "Ngày trả phòng", "Số lượng khách thuê", "Số lượng phòng thuê"],
        [current_user.name, order.checkin_date.strftime('%d/%m/%Y'), order.checkout_date.strftime('%d/%m/%Y'),
         len(custs), len(rooms)]
    ]
    basic_info_table = Table(basic_info_data, colWidths=[140, 100, 100, 130, 130])
    basic_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSerif'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(basic_info_table)

    new_custom_style = styles['Normal']
    new_custom_style.fontName = 'DejaVuSerif'  # Sử dụng font DejaVuSerif
    new_custom_style.fontSize = 11  # Kích thước chữ nhỏ hơn
    new_custom_style.alignment = 1  # Căn trái


    # Thêm dòng trống
    elements.append(Paragraph("<br/><br/>", content_style))
    elements.append(Paragraph("Tổng tiền: " + "{:,.0f}".format(total_price) + " VNĐ", new_custom_style))
    elements.append(Paragraph("<br/><br/>", content_style))
    # Danh sách khách hàng
    customer_data = [["Phòng", "Khách nội địa", "Khách quốc tế", "Đơn giá phòng", "Tổng giá phòng"]]
    for item in renting_details:
        customer_row = [
            Paragraph(item['room_name'], content_style),
            Paragraph(str(item['num_of_default_cust']), content_style),
            Paragraph(str(item['num_of_other_cust']), content_style),
            Paragraph("{:,.0f}".format(item['room_base_price']), content_style),
            Paragraph("{:,.0f}".format(item['room_final_price']), content_style)
        ]
        customer_data.append(customer_row)

    customer_table = Table(customer_data, colWidths=[140, 100, 100, 130, 130])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSerif'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(customer_table)
    elements.append(Paragraph("<br/><br/>", content_style))

    # Lời cảm ơn
    elements.append(Paragraph(
        "Cảm ơn quý khách đã sử dụng dịch vụ thuê phòng khách sạn của chúng tôi!",
        content_style
    ))

    # Tạo PDF
    pdf.build(elements)
    buffer.seek(0)

    # Trả về file PDF
    return send_file(buffer, as_attachment=True, download_name=f"hoa_don_{order.id}.pdf", mimetype='application/pdf')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.context_processor
def common_response_data():
    return {
        'user_roles': UserRoles
    }


if __name__ == '__main__':
    with app.app_context():
        from appQLKS import admin

        app.run(debug=True)
