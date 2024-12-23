from appQLKS import db, app
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect, flash
from appQLKS.models import (RoomType, Room, CustomerType, UserRoles, User,
                            BookingOrder, RentingOrder, Bill, Customer)


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRoles.ADMIN)


class RoomTypeView(ModelView):
    can_export = True
    column_list = ['id', 'name', 'basePrice', 'maxCust', 'overMaxRate', 'rooms']
    column_searchable_list = ['name']
    column_filters = ['name']
    can_view_details = True
    column_labels = dict(id='Mã loại phòng', name='Tên loại', basePrice='Giá ban đầu',
                         maxCust='Khách tối đa', overMaxRate='Phí phụ thu', rooms='Các phòng')


class RoomView(ModelView):
    column_list = ['id', 'name', 'roomPrice', 'available', 'roomType_id']
    column_searchable_list = ['name']
    column_filters = ['name']
    can_view_details = True
    column_labels = dict(id='Mã phòng', name='Tên phòng', roomPrice='Giá phòng',
                         available='Trạng thái', roomType_id='Loại phòng')


class CustomerTypeView(ModelView):
    column_list = ['id', 'name', 'cust_rate']
    column_searchable_list = ['name']
    column_filters = ['name']
    can_view_details = True
    column_labels = dict(id='Mã loại khách hàng', name='Tên loại', cust_rate='Hệ số')


class UserView(ModelView):
    column_list = ['id', 'name', 'username', 'active', 'user_role']
    column_searchable_list = ['name', 'username']
    column_filters = ['name', 'username', 'user_role']
    can_view_details = True
    column_labels = dict(id='Mã người dùng', name='Tên người dùng', username='Tên đăng nhập',
                         active='Trạng thái', user_role='Vai trò')

    def delete_model(self, model):
        # Kiểm tra user bị xóa có phải admin không, nếu phải thì chặn không cho xóa
        if model.user_role == UserRoles.ADMIN:
            flash('The admin user cannot be deleted.', 'error')
            return False
        return super().delete_model(model)


class BookingOrderView(ModelView):
    column_list = ['id', 'user_id', 'checkin_date', 'checkout_date', 'created_date']
    column_searchable_list = ['user_id', 'checkin_date', 'checkout_date', 'created_date']
    column_filters = ['user_id', 'checkin_date', 'checkout_date', 'created_date']
    can_view_details = True
    can_delete = False
    column_labels = dict(id='Mã đơn đặt', user_id='Người đặt', checkin_date='Ngày nhận phòng',
                         checkout_date='Ngày trả phòng', created_date='Ngày tạo đơn')


class RentingOrderView(ModelView):
    column_list = ['bookingOrder_id', 'checkin_date', 'checkout_date', 'created_date']
    column_searchable_list = ['checkin_date', 'checkout_date', 'created_date']
    column_filters = ['checkin_date', 'checkout_date', 'created_date']
    can_view_details = True
    can_delete = False
    column_labels = dict(bookingOrder_id='Mã phiếu thuê', checkin_date='Ngày nhận phòng',
                         checkout_date='Ngày trả phòng', created_date='Ngày tạo phiếu')


class BillView(ModelView):
    column_list = ['rentingOrder_id', 'checkin_date', 'checkout_date', 'totalCust', 'foreignCust',
                   'basePrice', 'extraCharge', 'created_date']
    column_searchable_list = ['checkin_date', 'checkout_date', 'created_date']
    column_filters = ['checkin_date', 'checkout_date', 'created_date']
    can_view_details = True
    can_delete = False
    column_labels = dict(rentingOrder_id='Mã hóa đơn', checkin_date='Ngày nhận phòng',
                         checkout_date='Ngày trả phòng', totalCust='Tổng số khách hàng',
                         foreignCust='Số khách hàng ngoại quốc', basePrice='Giá gốc',
                         extraCharge='Phụ thu', created_date='Ngày tạo phiếu')


class CustomerView(ModelView):
    column_list = ['id', 'cust_name', 'custIdentity_num', 'custAddress', 'custType_id']
    column_searchable_list = ['cust_name', 'custIdentity_num']
    column_filters = ['cust_name', 'custType_id', 'custAddress']
    column_labels = dict(id='Mã khách hàng', cust_name='Tên khách hàng', custIdentity_num='CMND',
                         custAddress='Địa chỉ', custType_id='Loại khách hàng')
    can_view_details = True


class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AuthenticatedBaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


class StatsView(AuthenticatedBaseView):
    @expose("/")
    def index(self):
        return self.render('admin/stats.html')


admin = Admin(app, name='Hotel Admin Page', template_mode='bootstrap4')


admin.add_view(RoomTypeView(RoomType, db.session, name='Loại phòng'))
admin.add_view(RoomView(Room, db.session, name='Phòng'))
admin.add_view(CustomerTypeView(CustomerType, db.session, name='Loại khách hàng'))
admin.add_view(CustomerView(Customer, db.session, name='Khách hàng'))
admin.add_view(UserView(User, db.session, name='Người dùng'))
admin.add_view(BookingOrderView(BookingOrder, db.session, name='Đơn đặt phòng'))
admin.add_view(RentingOrderView(RentingOrder, db.session, name='Phiếu thuê phòng'))
admin.add_view(BillView(Bill, db.session, name='Hóa đơn'))


admin.add_view(StatsView(name='Thống kê - Báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))