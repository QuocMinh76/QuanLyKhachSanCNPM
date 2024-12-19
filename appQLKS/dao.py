from appQLKS.models import User, Room, RoomType, BookingOrder
from appQLKS import app, db
import hashlib
import cloudinary.uploader
from sqlalchemy import or_


def load_room_types():
    return RoomType.query.order_by('id').all()


def get_all_rooms():
    return Room.query.order_by('id').all()


def load_rooms(room_type_id=None, kw=None, page=1):
    products = Room.query

    if kw:
        products = products.filter(Room.name.contains(kw))

    if room_type_id:
        products = products.filter(Room.roomType_id.__eq__(room_type_id))

    page_size = app.config["PAGE_SIZE"]
    start = (page - 1) * page_size
    products = products.slice(start, start + page_size)

    return products.all()


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


def count_rooms():
    return Room.query.count()


def add_booking_order(username, checkin_date, checkout_date, created_date):
    pass


def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User(name=name, username=username, password=password,
             avatar="https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg")

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get("secure_url")

    db.session.add(u)
    db.session.commit()


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username.strip()),
                          User.password.__eq__(password))

    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


# Lấy danh sách phòng theo loại phòng
# This function get all AVAILABLE rooms of a room type
def get_rooms_by_type(room_type_id=None):
    rooms = (db.session.query(Room, RoomType.name.label('type_name'))
             .join(RoomType, Room.roomType_id.__eq__(RoomType.id)))

    if room_type_id:
        rooms = rooms.filter(Room.roomType_id.__eq__(room_type_id))

    rooms = rooms.filter(Room.available.__eq__(True))

    return rooms.order_by('id').all()


def get_room_type_by_id(room_type_id):
    return RoomType.query.get(room_type_id)