from flask_login import current_user
from appQLKS.models import (User, Room, RoomType, CustomerType, Customer, BookingOrder, BookingRoomInfo,
                            BookingCustInfo, Comment, RentingOrder, RentingDetails, Bill)
from appQLKS import app, db
import hashlib
import cloudinary.uploader
from sqlalchemy import or_
import json
from sqlalchemy.orm import joinedload


def load_room_types():
    return RoomType.query.order_by('id').all()


def get_all_rooms():
    return Room.query.order_by('id').all()


def load_rooms(room_type_id=None, kw=None, page=1):
    rooms = Room.query

    if kw:
        rooms = rooms.filter(Room.name.contains(kw))

    if room_type_id:
        rooms = rooms.filter(Room.roomType_id.__eq__(room_type_id))

    page_size = app.config["PAGE_SIZE"]
    start = (page - 1) * page_size
    rooms = rooms.slice(start, start + page_size)

    return rooms.all()


def load_booking_orders(kw=None):
    orders = BookingOrder.query

    if kw:
        # Join with the User table and filter by user ID or name
        orders = orders.join(User).filter(
            or_(
                BookingOrder.id == kw,  # Search by user ID
                User.name.ilike(f"%{kw}%")  # Search by username (case-insensitive)
            )
        )

    return orders.all()


def load_comments(room_id, page=1):
    comments = Comment.query.filter(Comment.room_id.__eq__(room_id))

    page_size = app.config["COMMENT_PAGE_SIZE"]
    start = (page - 1) * page_size
    comments = comments.slice(start, start + page_size)

    return comments


def load_customer_type():
    return CustomerType.query.order_by('id').all()


def count_rooms():
    return Room.query.count()


def count_comments_of_room(room_id):
    return Comment.query.filter(Comment.room_id.__eq__(room_id)).count()


def add_comment(content, room_id):
    c = Comment(content=content, room_id=room_id, user=current_user)

    db.session.add(c)
    db.session.commit()

    return c


def add_booking_order(user_id, checkin_date, checkout_date, rooms: list, customers: list):
    try:
        # Create the booking order
        booking_order = BookingOrder(
            user_id=user_id,
            checkin_date=checkin_date,
            checkout_date=checkout_date
        )
        db.session.add(booking_order)
        db.session.flush()  # Flush to generate the ID for the booking order

        # Add room information
        for room_id in rooms:
            room_info = BookingRoomInfo(
                bookingOrder_id=booking_order.id,
                room_id=room_id
            )
            db.session.add(room_info)

        # Add customer information
        for customer_id in customers:
            cust_info = BookingCustInfo(
                bookingOrder_id=booking_order.id,
                cust_id=customer_id
            )
            db.session.add(cust_info)

        db.session.commit()  # Commit the transaction
        return booking_order

    except Exception as e:
        # Rollback in case of an error
        db.session.rollback()
        raise e


def add_renting_order(order_id, checkin, checkout, rooms_custs: list):
    try:
        # Create renting order
        renting_order = RentingOrder(id=order_id, checkin_date=checkin,
                                     checkout_date=checkout, pay_status=False)
        db.session.add(renting_order)
        db.session.flush()

        # Add room-cust info
        for rc in rooms_custs:
            customer_id = rc['customerId']
            room_id = rc['roomId']

            renting_details = RentingDetails(rentingOrder_id=renting_order.id, room_id=room_id,
                                             cust_id=customer_id)
            db.session.add(renting_details)

        db.session.commit()
        return renting_order

    except Exception as e:
        # Rollback in case of an error
        db.session.rollback()
        raise e


def add_user(name, username, password, avatar=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User(name=name, username=username, password=password,
             avatar="https://res.cloudinary.com/dhhpxhskj/image/upload/v1734858820/default_avt_uy1yef.png")

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get("secure_url")

    db.session.add(u)
    db.session.commit()


def add_customer(name, idNum, address, cust_type_id):
    customer = Customer(
        cust_name=name,
        custIdentity_num=idNum,
        custAddress=address,
        custType_id=cust_type_id
    )
    db.session.add(customer)
    db.session.commit()  # Commit the transaction to save the customer
    return customer


def process_booking_order(user_id, checkin, checkout, customers, selected_rooms):
    try:
        # Directly use db.session for adding items
        added_cust = []
        rooms_info = []

        # Process customers
        if customers:
            customers_data = json.loads(customers)
            for c in customers_data:
                customer = add_customer(
                    name=c["name"],
                    idNum=c["idNum"],
                    address=c["address"],
                    cust_type_id=c["type"]["id"]
                )
                added_cust.append(customer.id)

        # Process selected rooms
        if selected_rooms:
            rooms_data = json.loads(selected_rooms)
            for room in rooms_data:
                rooms_info.append(room["id"])

        # Add booking order
        add_booking_order(
            user_id=user_id,
            checkin_date=checkin,
            checkout_date=checkout,
            rooms=rooms_info,
            customers=added_cust
        )

    except Exception as e:
        # If something goes wrong, roll back the transaction
        db.session.rollback()
        raise Exception(f"Error during booking process: {e}")


def process_renting_order(order_id, checkin, checkout, rooms_custs):
    try:
        customer_room_mapping = json.loads(rooms_custs)

        add_renting_order(order_id=order_id, checkin=checkin, checkout=checkout,
                          rooms_custs=customer_room_mapping)

    except Exception as e:
        # If something goes wrong, roll back the transaction
        db.session.rollback()
        raise Exception(f"Error during booking process: {e}")


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username.strip()),
                          User.password.__eq__(password))

    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()


# Lấy danh sách phòng theo loại phòng
# This function get all AVAILABLE rooms of a room type
def get_rooms_by_type(room_type_id=None):
    rooms = (db.session.query(Room, RoomType.name.label('type_name'))
             .join(RoomType, Room.roomType_id.__eq__(RoomType.id)))

    if room_type_id:
        rooms = rooms.filter(Room.roomType_id.__eq__(room_type_id))

    rooms = rooms.filter(Room.available.__eq__(True))

    return rooms.order_by('id').all()


def get_booking_order_details(booking_order_id):
    """
    Retrieve a booking order and all related data by booking order ID.

    :param booking_order_id: The ID of the booking order.
    :return: A BookingOrder object with all related data loaded, or None if not found.
    """
    return db.session.query(BookingOrder).options(
        joinedload(BookingOrder.booking_room_info).joinedload(BookingRoomInfo.room),
        joinedload(BookingOrder.booking_cust_info).joinedload(BookingCustInfo.customer),
        joinedload(BookingOrder.renting_order)
    ).filter(BookingOrder.id == booking_order_id).one_or_none()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_room_type_by_id(room_type_id):
    return RoomType.query.get(room_type_id)


def get_booking_order_by_id(booking_order_id):
    return BookingOrder.query.get(booking_order_id)


def get_room_by_id(room_id):
    return Room.query.get(room_id)


def get_customer_by_id(cust_id):
    return Customer.query.get(cust_id)


if __name__ == "__main__":
    with app.app_context():
        booking_order_id = 1  # Replace with the desired booking order ID
        details = get_booking_order_details(booking_order_id)

        if details:
            print("Booking Order Details:")
            print(f"ID: {details.id}")
            print(f"Check-in Date: {details.checkin_date}")
            print(f"Check-out Date: {details.checkout_date}")
            print("Room Info:")
            for room_info in details.booking_room_info:
                print(f"Room ID: {room_info.room_id}")
            print("Customer Info:")
            for cust_info in details.booking_cust_info:
                print(f"Customer ID: {cust_info.cust_id}")
            if details.renting_order:
                print(f"Renting Order ID: {details.renting_order.id}")
        else:
            print("Booking order not found.")
