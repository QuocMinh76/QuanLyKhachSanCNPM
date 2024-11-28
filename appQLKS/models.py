from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime
import hashlib
from enum import Enum as RoleEnum
from flask_login import UserMixin

# Thay đổi theo máy
from kiet.appQLKS import db, app


class UserRoles(RoleEnum):
    admin = 1
    employee = 2
    customer = 3


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    username = Column(String(), nullable=False, unique=True)
    password = Column(String(), nullable=False)
    avatar = Column(String(), nullable=True)
    active = Column(Boolean, default=True)
    user_role = Column(Enum(UserRoles), default=UserRoles.customer)


class CustomerType(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    cust_type = Column(String(), nullable=False)
    cust_rate = Column(Float, default="1")


class Customer(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    cust_active = Column(Boolean, default=True)
    cust_name = Column(String(), nullable=False)
    custIdentity_num = Column(String(), nullable=False)
    custAddress = Column(String(), nullable=False)
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
    rentingOrder_id = Column(Integer, ForeignKey(RentingOrder.id_bookingOrder), primary_key=True)
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)
    totalCust = Column(Integer, nullable=False)
    foreignCust = Column(Integer, nullable=False)
    basePrice = Column(Float, nullable=False)
    extraCharge = Column(Float, default=0)


class RoomType(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    basePrice = Column(Float, default=0)
    maxCust = Column(Integer, default=3)
    overMaxRate = Column(Float, default=1.25)


class Room(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    description = Column(String(), nullable=True)
    available = Column(Boolean, default=True)
    roomType_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)


class OrderDetails(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    rentingOrder_id = Column(Integer, ForeignKey(RentingOrder.id_bookingOrder), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)
    cust_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
