from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime
import hashlib
from enum import Enum as RoleEnum
from flask_login import UserMixin
from appQLKS import db, app
from appQLKS.models import RoomType, User, UserRoles, CustomerType, Room

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Dữ liệu mẫu đã được thêm thành công!")

if __name__ == '__main__':
    with app.app_context():
        u = User(name="admin", username="admin",
                 password=str(hashlib.md5("123456".strip().encode('utf-8')).hexdigest()),
                 avatar="https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg",
                 user_role=UserRoles.admin)
        db.session.add(u)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        room_types = [
            RoomType(name="Standard Room", basePrice=100000, maxCust=3, overMaxRate=1.25),
            RoomType(name="Pro Room", basePrice=200000, maxCust=3, overMaxRate=1.25),
            RoomType(name="Ultra Room", basePrice=500000, maxCust=3, overMaxRate=1.25),
        ]

        db.session.add_all(room_types)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        cust_types = [
            CustomerType(cust_type="Domestic Guest", cust_rate=1),
            CustomerType(cust_type="Foreign Guest", cust_rate=1.5),
        ]
        db.session.add_all(cust_types)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        rooms = [
            Room(name="Room 1", description="Standard Room", available=True, roomType_id=1),
            Room(name="Room 2", description="Standard Room", available=True, roomType_id=1),
            Room(name="Room 3", description="Standard Room", available=True, roomType_id=1),
            Room(name="Room 4", description="Standard Room", available=True, roomType_id=1),
            Room(name="Room 5", description="Pro Room", available=True, roomType_id=2),
            Room(name="Room 6", description="Pro Room", available=True, roomType_id=2),
            Room(name="Room 7", description="Pro Room", available=True, roomType_id=2),
            Room(name="Room 8", description="Pro Room", available=True, roomType_id=2),
            Room(name="Room 9", description="Ultra Room", available=True, roomType_id=3),
            Room(name="Room 10", description="Ultra Room", available=True, roomType_id=3),
            Room(name="Room 11", description="Ultra Room", available=True, roomType_id=3),
            Room(name="Room 12", description="Ultra Room", available=True, roomType_id=3),
        ]
        db.session.add_all(rooms)
        db.session.commit()

