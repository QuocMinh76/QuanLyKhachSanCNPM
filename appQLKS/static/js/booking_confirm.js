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
            bookingData.selected_rooms.forEach(room => {
                const roomElement = `
                    <label class="form-check-label">${room.name}, </label>
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
