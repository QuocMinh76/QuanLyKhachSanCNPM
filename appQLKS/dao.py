from appQLKS.models import User, Room, RoomType
from appQLKS import app, db
import hashlib
import cloudinary.uploader


def load_room_types():
    return RoomType.query.order_by('id').all()


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


def count_rooms():
    return Room.query.count()


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


# Lấy danh sách loại phòng
def get_room_types():
    return RoomType.query.all()


# Lấy danh sách phòng theo loại phòng
def get_rooms_by_type(room_type_id):
    return Room.query.filter(Room.roomType_id == room_type_id).all()
