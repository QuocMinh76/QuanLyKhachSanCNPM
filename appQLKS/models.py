from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime
from enum import Enum as RoleEnum
from flask_login import UserMixin
from appQLKS import db, app
from datetime import datetime
import pytz

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        # db.create_all()
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

    orders = relationship('BookingOrder', backref='user', lazy=True)
    comments = relationship('Comment', backref='user', lazy=True)

    def __str__(self):
        return self.username


class CustomerType(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    cust_rate = Column(Float, default="1")

    customers = relationship('Customer', backref='custType', lazy=True)

    def __str__(self):
        return self.name


class Customer(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    cust_active = Column(Boolean, default=True)
    cust_name = Column(String(100), nullable=False)
    custIdentity_num = Column(String(100), nullable=False)
    custAddress = Column(String(100), nullable=False)
    custType_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False)

    booking_room_info = relationship('BookingCustInfo', back_populates='customer', lazy=True)
    renting_details = relationship('RentingDetails', back_populates='customer', lazy=True)


class BookingOrder(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)  # Tham chiếu đến bảng User
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.utcnow()
                          .replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Ho_Chi_Minh')))

    booking_room_info = relationship('BookingRoomInfo', back_populates='booking_order', lazy=True)
    booking_cust_info = relationship('BookingCustInfo', back_populates='booking_order', lazy=True)
    renting_order = relationship('RentingOrder', back_populates='booking_order', uselist=False)


class RentingOrder(db.Model):
    id = Column(Integer, ForeignKey(BookingOrder.id, ondelete="CASCADE"),
                primary_key=True, unique=True)  # Khóa ngoại tham chiếu 1-1 đến khóa chính đơn đặt
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.utcnow()
                          .replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Ho_Chi_Minh')))
    status = Column(Boolean, default=False)

    details = relationship('RentingDetails', back_populates='renting_order', lazy=True)
    booking_order = relationship('BookingOrder', back_populates='renting_order')
    bill = relationship('Bill', back_populates='renting_order', uselist=False)


class Bill(db.Model):
    id = Column(Integer, ForeignKey(RentingOrder.id, ondelete="CASCADE"),
                primary_key=True, unique=True)
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)
    totalCust = Column(Integer, nullable=False)
    foreignCust = Column(Integer, nullable=False)
    basePrice = Column(Float, nullable=False)
    extraCharge = Column(Float, default=0)
    created_date = Column(DateTime, default=lambda: datetime.utcnow()
                          .replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Ho_Chi_Minh')))

    renting_order = relationship('RentingOrder', back_populates='bill')


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

    booking_room_info = relationship('BookingRoomInfo', back_populates='room', lazy=True)
    renting_details = relationship('RentingDetails', back_populates='room', lazy=True)
    comments = relationship('Comment', backref='room_comment', lazy=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.roomPrice and self.roomType_id:
            room_type = RoomType.query.get(self.roomType_id)
            if room_type:
                self.roomPrice = room_type.basePrice


class BookingRoomInfo(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    bookingOrder_id = Column(Integer, ForeignKey(BookingOrder.id), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)

    booking_order = relationship('BookingOrder', back_populates='booking_room_info')
    room = relationship("Room", back_populates="booking_room_info")


class BookingCustInfo(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    bookingOrder_id = Column(Integer, ForeignKey(BookingOrder.id), nullable=False)
    cust_id = Column(Integer, ForeignKey(Customer.id), nullable=False)

    booking_order = relationship('BookingOrder', back_populates='booking_cust_info')
    customer = relationship("Customer", back_populates="booking_room_info")


class RentingDetails(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    rentingOrder_id = Column(Integer, ForeignKey(RentingOrder.id), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)
    cust_id = Column(Integer, ForeignKey(Customer.id), nullable=False)

    renting_order = relationship("RentingOrder", back_populates="details")
    room = relationship("Room", back_populates="renting_details")
    customer = relationship("Customer", back_populates="renting_details")


class Comment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(255), nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.utcnow()
                          .replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Ho_Chi_Minh')))
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
