from datetime import timedelta, datetime
import pytz
from dateutil.relativedelta import relativedelta
from flask_login import current_user
from appQLKS.models import (User, Room, RoomType, CustomerType, Customer, BookingOrder, BookingRoomInfo,
                            BookingCustInfo, Comment, RentingOrder, RentingDetails, Bill)
from appQLKS import app, db
import hashlib
import cloudinary.uploader
from sqlalchemy import or_, func, case
import json
from sqlalchemy.orm import joinedload, aliased
from collections import defaultdict


def load_room_types():
    return RoomType.query.order_by('id').all()


def get_all_rooms():
    return Room.query.order_by('id').all()


def load_rooms(room_type_id=None, kw=None, min_price=None, max_price=None, page=1):
    rooms = Room.query.filter(Room.available.__eq__(True))

    if kw:
        rooms = rooms.filter(Room.name.contains(kw))

    if room_type_id:
        rooms = rooms.filter(Room.roomType_id.__eq__(room_type_id))

    if min_price:
        rooms = rooms.filter(Room.roomPrice >= float(min_price))

    if max_price:
        rooms = rooms.filter(Room.roomPrice <= float(max_price))

    page_size = app.config["PAGE_SIZE"]
    start = (page - 1) * page_size
    rooms = rooms.slice(start, start + page_size)

    return rooms.all()


def load_booking_orders(kw=None):
    orders = BookingOrder.query

    if kw:
        orders = orders.join(User).filter(
            or_(
                BookingOrder.id == kw,  # Search by order ID
                User.name.ilike(f"%{kw}%")  # Search by username (case-insensitive)
            )
        )

    orders = orders.filter(BookingOrder.is_processed.__eq__(False))
    orders = orders.filter(BookingOrder.is_cancelled.__eq__(False))

    return orders.all()


def load_renting_orders(kw=None):
    orders = RentingOrder.query

    if kw:
        orders = orders.join(BookingOrder).join(User).filter(
            or_(
                RentingOrder.id == kw,  # Search by order ID
                User.name.ilike(f"%{kw}%")  # Search by username (case-insensitive)
            )
        )

    orders = orders.filter(RentingOrder.pay_status.is_(False))

    return orders.options(joinedload(RentingOrder.booking_order)).all()


def load_bills(kw=None):
    query = Bill.query

    if kw:
        query = query.join(Bill.renting_order).join(RentingOrder.booking_order).join(User).filter(
            or_(
                Bill.id == kw,  # Filter by RentingOrder ID
                User.name.ilike(f"%{kw}%")  # Filter by user name (case-insensitive)
            )
        )

    return query.all()


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
        deadline_date = app.config['BOOKING_DEADLINE_DAYS']

        # Create the booking order
        booking_order = BookingOrder(
            user_id=user_id,
            checkin_date=checkin_date,
            checkout_date=checkout_date
        )
        db.session.add(booking_order)
        db.session.flush()  # Flush to generate the ID for the booking order

        if booking_order.created_date:  # Assuming created_date is auto-set
            booking_order.deadline_date = booking_order.created_date + timedelta(days=deadline_date)

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


def add_bill(order_id, checkin, checkout, domestic_cust_num, foreign_cust_num, total_price):
    bill = Bill(id=order_id, checkin_date=checkin, checkout_date=checkout, domesticCust=domestic_cust_num,
                foreignCust=foreign_cust_num, finalPrice=total_price)

    db.session.add(bill)
    db.session.commit()


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

        booking_order = get_booking_order_by_id(order_id)
        update_booking_order_state(booking_order)

        add_renting_order(order_id=order_id, checkin=checkin, checkout=checkout,
                          rooms_custs=customer_room_mapping)

    except Exception as e:
        # If something goes wrong, roll back the transaction
        db.session.rollback()
        raise Exception(f"Error during booking process: {e}")


def process_bill(order_id, checkin, checkout, total_domestic_cust, total_foreign_cust, total_price):
    try:
        renting_order = get_renting_order_by_id(order_id)

        add_bill(
            order_id=renting_order.id,
            checkin=checkin,
            checkout=checkout,
            domestic_cust_num=total_domestic_cust,
            foreign_cust_num=total_foreign_cust,
            total_price=total_price
        )

        update_renting_order_state(renting_order)

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


def get_bills_of_user(user_id):
    # Start the query from Bill
    bills = Bill.query

    # Join the necessary tables in the correct order
    bills = bills.join(RentingOrder).join(BookingOrder).join(User)

    # Filter by the user_id
    bills = bills.filter(User.id == user_id)

    return bills.all()


# Lấy danh sách phòng theo loại phòng
# This function get all AVAILABLE rooms of a room type
def get_rooms_by_type(room_type_id=None):
    rooms = (db.session.query(Room, RoomType.name.label('type_name'), RoomType.maxCust.label('max_cust'))
             .join(RoomType, Room.roomType_id.__eq__(RoomType.id)))

    if room_type_id:
        rooms = rooms.filter(Room.roomType_id.__eq__(room_type_id))

    rooms = rooms.filter(Room.available.__eq__(True))

    return rooms.order_by('id').all()


def get_booking_order_details(booking_order_id):
    return db.session.query(BookingOrder).options(
        joinedload(BookingOrder.booking_room_info).joinedload(BookingRoomInfo.room),
        joinedload(BookingOrder.booking_cust_info).joinedload(BookingCustInfo.customer),
        joinedload(BookingOrder.renting_order)
    ).filter(BookingOrder.id == booking_order_id).one_or_none()


def get_renting_order_details(renting_order_id):
    renting_order = db.session.query(RentingOrder) \
        .options(
        joinedload(RentingOrder.details)
        .joinedload(RentingDetails.room),
        joinedload(RentingOrder.details)
        .joinedload(RentingDetails.customer),
        joinedload(RentingOrder.booking_order),
        joinedload(RentingOrder.bill)
    ) \
        .filter(RentingOrder.id == renting_order_id) \
        .one_or_none()

    return renting_order


def get_room_cust_info_of_renting_order(renting_order_id):
    results = RentingDetails.query.filter(RentingDetails.rentingOrder_id == renting_order_id).all()
    if not results:
        return {}
    response = [{"cust_id": record.cust_id, "room_id": record.room_id} for record in results]
    return response


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_room_type_by_id(room_type_id):
    return RoomType.query.get(room_type_id)


def get_booking_order_by_id(booking_order_id):
    return BookingOrder.query.get(booking_order_id)


def get_renting_order_by_id(renting_order_id):
    return RentingOrder.query.get(renting_order_id)


def get_bill_by_id(bill_id):
    return Bill.query.get(bill_id)


def get_room_by_id(room_id):
    return Room.query.get(room_id)


def get_customer_by_id(cust_id):
    return Customer.query.get(cust_id)


def update_booking_order_state(booking_order):
    booking_order.is_processed = True

    db.session.commit()


def update_renting_order_state(renting_order):
    renting_order.pay_status = True

    db.session.commit()


def calculate_room_final_price(renting_order_id, room_id):
    # Fetch room details, including its type
    room = db.session.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise ValueError("Room not found.")

    # Get base price and maxCust from the room's type
    room_base_price = room.roomType.basePrice
    max_cust = room.roomType.maxCust
    over_max_rate = room.roomType.overMaxRate

    # Count customers in the room and group by customer type
    customer_counts = count_customers_in_room(renting_order_id, room_id)

    # Calculate total number of customers in the room
    total_customers = sum(data['cust_num'] for data in customer_counts.values())

    # Start with the base price
    final_price = room_base_price

    # Check if any customer type has a rate > 1 (foreign customers)
    max_rate = max(data['cust_rate'] for data in customer_counts.values()) if customer_counts else 1
    final_price *= max_rate

    if total_customers == 0:
        # No customers, treat as `maxCust - 1`
        pass  # Price remains the base price
    elif total_customers >= max_cust:
        # Apply overMaxRate surcharge if customers reach maxCust
        final_price += room_base_price * over_max_rate

    return final_price


def count_customers_in_room(renting_order_id, room_id):
    # Alias for customer_type to access customer_type data in the join
    customer_type_alias = aliased(CustomerType)

    # Query to get customer type name, count of customers, and cust_rate
    query = db.session.query(
        customer_type_alias.name.label("customer_type"),
        func.count(Customer.id).label("cust_num"),
        customer_type_alias.cust_rate.label("cust_rate")
    ).join(
        RentingDetails, RentingDetails.cust_id == Customer.id
    ).join(
        customer_type_alias, customer_type_alias.id == Customer.custType_id
    ).filter(
        RentingDetails.rentingOrder_id == renting_order_id,
        RentingDetails.room_id == room_id
    ).group_by(
        customer_type_alias.name, customer_type_alias.cust_rate
    ).all()

    # Format the result as a dictionary
    result = defaultdict(dict)
    for row in query:
        result[row.customer_type] = {
            "cust_num": row.cust_num,
            "cust_rate": row.cust_rate
        }

    return dict(result)


def calculate_total_price_for_renting_order(renting_order_id):
    # Get unique room IDs associated with the renting order
    unique_room_ids = db.session.query(
        RentingDetails.room_id
    ).filter(
        RentingDetails.rentingOrder_id == renting_order_id
    ).distinct().all()

    # Convert the list of tuples to a flat list
    unique_room_ids = [room_id[0] for room_id in unique_room_ids]

    if not unique_room_ids:
        raise ValueError("No rooms found for the given renting order.")

    # Initialize total price
    total_price = 0.0

    # Iterate through each unique room in the renting order
    for room_id in unique_room_ids:
        room_price = calculate_room_final_price(renting_order_id, room_id)
        total_price += room_price

    return total_price


def get_renting_order_room_details(renting_order_id):
    # Query to get room details and calculate customer counts with conditional aggregation
    room_details_query = db.session.query(
        Room.id.label('room_id'),
        Room.name.label('room_name'),
        Room.roomPrice.label('room_base_price'),

        # Conditional aggregation for default customers ('Nội địa')
        func.count(
            case(
                (CustomerType.name == 'Nội địa', 1),  # Condition for 'Nội địa'
                else_=None  # Exclude non-'Nội địa' customers
            )
        ).label('num_of_default_cust'),

        # Conditional aggregation for other customers (not 'Nội địa')
        func.count(
            case(
                (CustomerType.name != 'Nội địa', 1),  # Condition for not 'Nội địa'
                else_=None  # Exclude 'Nội địa' customers
            )
        ).label('num_of_other_cust')
    ).join(
        RentingDetails, RentingDetails.room_id == Room.id
    ).join(
        Customer, Customer.id == RentingDetails.cust_id
    ).join(
        CustomerType, CustomerType.id == Customer.custType_id
    ).filter(
        RentingDetails.rentingOrder_id == renting_order_id
    ).group_by(
        Room.id, Room.name, Room.roomPrice
    ).all()

    # Initialize the result list
    result = []

    for room in room_details_query:
        # Calculate room final price using the previous function
        room_final_price = calculate_room_final_price(renting_order_id, room.room_id)

        # Append room details to the result
        result.append({
            'room_id': room.room_id,
            'room_name': room.room_name,
            'num_of_default_cust': room.num_of_default_cust,
            'num_of_other_cust': room.num_of_other_cust,
            'room_base_price': room.room_base_price,
            'room_final_price': room_final_price
        })

    return result


def update_room_status(room_id, available):
    try:
        room = db.session.query(Room).filter_by(id=room_id).first()
        if room:
            print(f'Cập nhật trạng thái phòng ID {room_id} thành {available}')
            room.available = available
            db.session.commit()
            return True
        print(f'Không tìm thấy phòng với ID {room_id}')
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error updating room status: {e}")
        return False


def get_monthly_statistics(month):
    start_date = datetime.strptime(month, '%Y-%m')
    end_date = start_date + relativedelta(months=1)

    # Thống kê doanh thu
    revenue_query = (
        db.session.query(
            RoomType.name.label('room_type'),
            func.sum(Bill.finalPrice).label('total_revenue'),
            func.count(Bill.id).label('rental_count')
        )
        .join(RentingOrder, RentingOrder.id == Bill.id)
        .join(BookingOrder, BookingOrder.id == RentingOrder.id)
        .join(BookingRoomInfo, BookingRoomInfo.bookingOrder_id == BookingOrder.id)
        .join(Room, Room.id == BookingRoomInfo.room_id)
        .join(RoomType, RoomType.id == Room.roomType_id)
        .filter(Bill.created_date >= start_date, Bill.created_date < end_date)
        .group_by(RoomType.name)
    ).all()

    total_revenue = sum(r.total_revenue for r in revenue_query)

    revenue_data = [
        {
            'room_type': r.room_type,
            'total_revenue': r.total_revenue,
            'rental_count': r.rental_count,
            'rate': (r.total_revenue / total_revenue) * 100
        }
        for r in revenue_query
    ]

    # Thống kê tần suất sử dụng phòng
    frequency_query = (
        db.session.query(
            Room.name.label('room_name'),
            func.count(RentingDetails.id).label('rental_days')
        )
        .join(RentingOrder, RentingOrder.id == RentingDetails.rentingOrder_id)  # Join RentingOrder to RentingDetails
        .join(Room, Room.id == RentingDetails.room_id)  # Correct join between RentingDetails and Room
        .filter(RentingOrder.checkin_date >= start_date, RentingOrder.checkin_date < end_date)
        .group_by(Room.name)
    ).all()

    frequency_data = [
        {
            'room_name': f.room_name,
            'rental_days': f.rental_days,
            'rate': (f.rental_days / sum(x.rental_days for x in frequency_query)) * 100
        }
        for f in frequency_query
    ]

    return {'revenue_data': revenue_data, 'frequency_data': frequency_data}


def stats_rooms():
    return db.session.query(RoomType.id, RoomType.name, func.count(Room.id))\
        .join(Room, Room.roomType_id.__eq__(RoomType.id), isouter=True).group_by(RoomType.id).all()


def get_expired_booking_orders():
    with db.session.begin():
        now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
        return BookingOrder.query.filter(BookingOrder.deadline_date < now,
                                         BookingOrder.is_cancelled.__eq__(False)).all()


def update_booking_order_status_and_rooms(order):
    order.is_cancelled = True
    for booking_room in order.booking_room_info:
        room = booking_room.room
        room.available = True
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        print(stats_rooms())
