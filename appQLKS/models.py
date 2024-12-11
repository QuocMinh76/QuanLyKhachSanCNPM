from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime
import hashlib
from enum import Enum as RoleEnum
from flask_login import UserMixin

# Thay đổi theo máy
#from kiet.appQLKS import db, app
from appQLKS import db, app

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Dữ liệu mẫu đã được thêm thành công!")


class UserRoles(RoleEnum):
    ADMIN = 1
    EMPLOYEE = 2
    CUSTOMER = 3


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    avatar = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)
    user_role = Column(Enum(UserRoles), default=UserRoles.CUSTOMER)


class CustomerType(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    cust_type = Column(String(100), nullable=False)
    cust_rate = Column(Float, default="1")
    customers = relationship('Customer', backref='custType', lazy=True)


class Customer(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    cust_active = Column(Boolean, default=True)
    cust_name = Column(String(100), nullable=False)
    custIdentity_num = Column(String(100), nullable=False)
    custAddress = Column(String(100), nullable=False)
    custType_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False)


class BookingOrder(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ordered_by = Column(Integer, ForeignKey(User.id), nullable=False)  # Tham chiếu đến bảng User
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)


class RentingOrder(db.Model):
    bookingOrder_id = Column(Integer, ForeignKey(BookingOrder.id), primary_key=True)  # Khóa ngoại là khóa chính
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)


class Bill(db.Model):
    rentingOrder_id = Column(Integer, ForeignKey(RentingOrder.bookingOrder_id), primary_key=True)
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)
    totalCust = Column(Integer, nullable=False)
    foreignCust = Column(Integer, nullable=False)
    basePrice = Column(Float, nullable=False)
    extraCharge = Column(Float, default=0)


class RoomType(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    basePrice = Column(Float, default=0)
    maxCust = Column(Integer, default=3)
    overMaxRate = Column(Float, default=1.25)
    rooms = relationship('Room', backref='roomType', lazy=True)

    def __str__(self):
        return self.name


class Room(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=True)
    image = Column(String(100), nullable=True)
    available = Column(Boolean, default=True)
    roomPrice = Column(Float, default=0)
    roomType_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.roomPrice and self.roomType_id:
            room_type = RoomType.query.get(self.roomType_id)
            if room_type:
                self.roomPrice = room_type.basePrice


class OrderDetails(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    rentingOrder_id = Column(Integer, ForeignKey(RentingOrder.bookingOrder_id), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)
    cust_id = Column(Integer, ForeignKey(Customer.id), nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()