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
        from appQLKS import models
        db.create_all()
        print("Dữ liệu mẫu đã được thêm thành công!")

if __name__ == '__main__':
    with app.app_context():
        u = User(name="admin", username="admin",
                 password=str(hashlib.md5("123456".strip().encode('utf-8')).hexdigest()),
                 avatar="https://res.cloudinary.com/dhhpxhskj/image/upload/v1734859482/default_admin_avt_gv720p.png",
                 user_role=UserRoles.ADMIN)
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
            CustomerType(name="Nội địa", cust_rate=1),
            CustomerType(name="Quốc tế", cust_rate=1.5)
        ]
        db.session.add_all(cust_types)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        string_image_1 = 'https://res.cloudinary.com/dhhpxhskj/image/upload/v1735037004/rbaga60fyfj9lr5ln8e4.jpg'
        string_image_2 = 'https://res.cloudinary.com/dhhpxhskj/image/upload/v1735037004/uh6q2fjupcpr5oxqqaxw.jpg'
        string_image_3 = 'https://res.cloudinary.com/dhhpxhskj/image/upload/v1733934406/coakbeg2epakg1ghrl1x.jpg'
        rooms = [
            Room(name="Room 1", description="Standard Room", image=string_image_1, available=True, roomType_id=1),
            Room(name="Room 2", description="Standard Room", image=string_image_1, available=True, roomType_id=1),
            Room(name="Room 3", description="Standard Room", image=string_image_1, available=True, roomType_id=1),
            Room(name="Room 4", description="Standard Room", image=string_image_1, available=True, roomType_id=1),
            Room(name="Room 5", description="Pro Room", image=string_image_2, available=True, roomType_id=2),
            Room(name="Room 6", description="Pro Room", image=string_image_2, available=True, roomType_id=2),
            Room(name="Room 7", description="Pro Room", image=string_image_2, available=True, roomType_id=2),
            Room(name="Room 8", description="Pro Room", image=string_image_2, available=True, roomType_id=2),
            Room(name="Room 9", description="Ultra Room", image=string_image_3, available=True, roomType_id=3),
            Room(name="Room 10", description="Ultra Room", image=string_image_3, available=True, roomType_id=3),
            Room(name="Room 11", description="Ultra Room", image=string_image_3, available=True, roomType_id=3),
            Room(name="Room 12", description="Ultra Room", image=string_image_3, available=True, roomType_id=3),
        ]
        db.session.add_all(rooms)
        db.session.commit()

