document.addEventListener('DOMContentLoaded', function () {
    const bookingData = JSON.parse(localStorage.getItem('bookingData'));

    if (bookingData) {
        // Display basic booking information
        document.getElementById('name').value = bookingData.name;
        document.getElementById('checkin').value = bookingData.checkin;
        document.getElementById('checkout').value = bookingData.checkout;
        document.getElementById('num_guests').value = bookingData.num_guests;
        document.getElementById('num_rooms').value = bookingData.num_rooms;

        // Update hidden input fields
        document.getElementById('hidden_name').value = bookingData.name;
        document.getElementById('hidden_checkin').value = bookingData.checkin;
        document.getElementById('hidden_checkout').value = bookingData.checkout;
        document.getElementById('hidden_num_guests').value = bookingData.num_guests;
        document.getElementById('hidden_num_rooms').value = bookingData.num_rooms;
        document.getElementById('hidden_selected_rooms').value = JSON.stringify(bookingData.selected_rooms || []);
        document.getElementById('hidden_customers').value = JSON.stringify(bookingData.customers || []);

        // Check if the selected room list exists and is not empty
        if (bookingData.selected_rooms && bookingData.selected_rooms.length > 0) {
            bookingData.selected_rooms.forEach((room, index) => {
                const isLast = index === bookingData.selected_rooms.length - 1;
                const roomElement = `
                    <label class="form-check-label">${room.name}${isLast ? '' : ','}</label>
                `;
                document.getElementById('roomListContainer').insertAdjacentHTML('beforeend', roomElement);
            });
        } else {
            document.getElementById('roomListContainer').innerHTML = '<p>Không có phòng nào được chọn.</p>';
        }

        // Display customer information
        if (bookingData.customers && bookingData.customers.length > 0) {
            bookingData.customers.forEach(customer => {
                const row = `
                    <tr>
                        <td>
                            <input type="text" class="form-control" value="${customer.name}" readonly placeholder="Tên khách hàng">
                        </td>
                        <td>
                            <input type="text" class="form-control" value="${customer.type.name}" readonly placeholder="Loại khách hàng">
                        </td>
                        <td>
                            <input type="text" class="form-control" value="${customer.idNum}" readonly placeholder="CMND">
                        </td>
                        <td>
                            <input type="text" class="form-control" value="${customer.address}" readonly placeholder="Địa chỉ">
                        </td>
                    </tr>
                `;
                document.getElementById('customerTableBody').insertAdjacentHTML('beforeend', row);
            });
        } else {
            document.getElementById('customerTableBody').innerHTML = `
                <tr>
                    <td colspan="4">Không có khách hàng nào được nhập.</td>
                </tr>
            `;
        }
    }
});

//document.getElementById('confirmBookingButton').addEventListener('click', function () {
//    // Lấy dữ liệu đặt phòng từ localStorage
//    const bookingData = JSON.parse(localStorage.getItem('bookingData'));
//    console.log('Dữ liệu đặt phòng trước khi cập nhật:', bookingData);
//
//    if (bookingData && bookingData.selected_rooms && bookingData.selected_rooms.length > 0) {
//        // Cập nhật trạng thái phòng trong bookingData
//        bookingData.selected_rooms.forEach(room => {
//            room.status = 'Unavailable'; // Đặt trạng thái phòng là "Không sẵn sàng"
//        });
//
//        console.log('Dữ liệu đặt phòng sau khi cập nhật trạng thái phòng:', bookingData);
//
//        // Cập nhật lại bookingData vào localStorage
//        localStorage.setItem('bookingData', JSON.stringify(bookingData));
//
//        // Gửi yêu cầu cập nhật trạng thái phòng trên server
//        fetch('/api/update_rooms_status', {
//            method: 'POST',
//            headers: {
//                'Content-Type': 'application/json',
//            },
//            body: JSON.stringify({ rooms: bookingData.selected_rooms })
//        })
//        .then(response => response.json())
//        .then(data => {
//            console.log('Kết quả trả về từ server:', data);
//            if (data.success) {
//                alert('Đặt phòng thành công và trạng thái phòng đã được cập nhật.');
//            } else {
//                alert('Có lỗi xảy ra khi cập nhật trạng thái phòng.');
//            }
//        })
//        .catch(error => {
//            console.error('Error:', error);
//            alert('Có lỗi xảy ra khi cập nhật trạng thái phòng.');
//        });
//    } else {
//        alert('Không có phòng nào được chọn.');
//    }
//});

let bookingStartTime = null; // Biến lưu thời gian bắt đầu đặt phòng

document.getElementById('confirmBookingButton').addEventListener('click', function () {
    // Lấy dữ liệu đặt phòng từ localStorage
    const bookingData = JSON.parse(localStorage.getItem('bookingData'));
    console.log('Dữ liệu đặt phòng trước khi cập nhật:', bookingData);

    if (bookingData && bookingData.selected_rooms && bookingData.selected_rooms.length > 0) {
        // Cập nhật trạng thái phòng trong bookingData
        bookingData.selected_rooms.forEach(room => {
            room.status = 'Unavailable'; // Đặt trạng thái phòng là "Không sẵn sàng"
        });

        console.log('Dữ liệu đặt phòng sau khi cập nhật trạng thái phòng:', bookingData);

        // Cập nhật lại bookingData vào localStorage
        localStorage.setItem('bookingData', JSON.stringify(bookingData));

        // Lưu thời gian bắt đầu
        bookingStartTime = new Date().getTime();

        // Gửi yêu cầu cập nhật trạng thái phòng trên server
        fetch('/api/update_rooms_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rooms: bookingData.selected_rooms })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Kết quả trả về từ server:', data);
            if (data.success) {
                alert('Đặt phòng thành công và trạng thái phòng đã được cập nhật.');
            } else {
                alert('Có lỗi xảy ra khi cập nhật trạng thái phòng.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Có lỗi xảy ra khi cập nhật trạng thái phòng.');
        });

        // Kiểm tra trạng thái phòng sau 30 giây nếu chưa có hành động tiếp theo
        setTimeout(() => {
            const currentTime = new Date().getTime();
            if (currentTime - bookingStartTime >= 5000) { // Kiểm tra nếu đã qua 30 giây
                // Lấy lại dữ liệu từ localStorage
                const updatedBookingData = JSON.parse(localStorage.getItem('bookingData'));

                // Cập nhật lại trạng thái các phòng
                updatedBookingData.selected_rooms.forEach(room => {
                    room.status = 'Available'; // Đặt lại trạng thái phòng thành "Sẵn sàng"
                });

                // Cập nhật lại bookingData vào localStorage
                localStorage.setItem('bookingData', JSON.stringify(updatedBookingData));
                console.log('Trạng thái phòng đã được cập nhật lại sau 30 giây.');
            }
        }, 5000); // 30 giây
    } else {
        alert('Không có phòng nào được chọn.');
    }
});
