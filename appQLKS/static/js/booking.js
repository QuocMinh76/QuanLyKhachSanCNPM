// Constants and DOM Elements
const MAX_ITEMS_PER_ROW = 5;
const roomListContainer = document.getElementById('room-list');
const numRoomsInput = document.getElementById('num_rooms');
const customerTableBody = document.getElementById('customerTableBody');

// Selected room tracking
const selectedRooms = [];

// Event Listeners
document.querySelectorAll('.room-type-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', handleCheckboxChange);
});

document.getElementById('uncheckAllButton').addEventListener('click', uncheckAllRooms);
document.getElementById('addRowButton').addEventListener('click', addCustomerRow);
document.getElementById('removeRowButton').addEventListener('click', removeCustomerRow);
document.getElementById('confirmBookingButton').addEventListener('click', confirmBooking);

// Functions
function handleCheckboxChange() {
    const selectedTypes = Array.from(document.querySelectorAll('.room-type-checkbox:checked')).map(cb => cb.value);
    roomListContainer.innerHTML = '';
    roomListContainer.style.display = selectedTypes.length ? 'block' : 'none';

    if (!selectedTypes.length) return;

    const roomPromises = selectedTypes.map(type => fetchRoomsByType(type));
    Promise.all(roomPromises).then(responses => {
        const allRooms = responses.flat().map((room, idx) => ({ ...room, type: selectedTypes[idx] }));
        displayRooms(allRooms);
    }).catch(error => console.error('Error fetching rooms:', error));
}

async function fetchRoomsByType(type) {
    try {
        const response = await fetch(`/api/rooms?room_type_id=${type}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`Error fetching rooms for type ${type}:`, error);
        return [];
    }
}

function displayRooms(rooms) {
    roomListContainer.innerHTML = '';
    let currentRow = document.createElement('div');
    currentRow.classList.add('room-row');
    roomListContainer.appendChild(currentRow);

    rooms.forEach((room, index) => {
        const roomItem = createRoomItem(room);
        currentRow.appendChild(roomItem);

        if ((index + 1) % MAX_ITEMS_PER_ROW === 0) {
            currentRow = document.createElement('div');
            currentRow.classList.add('room-row');
            roomListContainer.appendChild(currentRow);
        }
    });
}

function createRoomItem(room) {
    const roomItem = document.createElement('div');
    roomItem.classList.add('room-item');
    roomItem.setAttribute('data-room-id', room.id);

    roomItem.innerHTML = `
        <div class="room-name">${room.name}</div>
        <div class="room-type">${room.type_name} - ${formatPrice(room.price)}</div>
    `;

    if (selectedRooms.some(selectedRoom => selectedRoom.id === room.id)) {
        roomItem.classList.add('selected');
        roomItem.style.backgroundColor = 'rgb(117, 148, 101)';
    }

    roomItem.addEventListener('click', () => toggleRoomSelection(roomItem, room));
    return roomItem;
}

function toggleRoomSelection(roomItem, room) {
    const index = selectedRooms.findIndex(selectedRoom => selectedRoom.id === room.id);
    const isSelected = index === -1; // If not in the array, we select it

    // Toggle the selection visually
    roomItem.classList.toggle('selected', isSelected);
    roomItem.style.backgroundColor = isSelected ? 'rgb(117, 148, 101)' : '';

    if (isSelected) {
        selectedRooms.push(room);
    } else {
        selectedRooms.splice(index, 1);
    }

    updateSelectedRoomCount();
}

function reselectRooms() {
    selectedRooms.forEach(room => {
        const roomItem = document.querySelector(`[data-room-id="${room.id}"]`);
        if (roomItem) {
            roomItem.classList.add('selected');
            roomItem.style.backgroundColor = 'rgb(117, 148, 101)';
        }
    });
}

document.addEventListener('DOMContentLoaded', reselectRooms);

function updateSelectedRoomCount() {
    numRoomsInput.value = selectedRooms.length;
}

function uncheckAllRooms() {
    document.querySelectorAll('.room-item').forEach(item => {
        item.classList.remove('selected');
        item.style.backgroundColor = '';
    });
    selectedRooms.length = 0; // Clear array
    updateSelectedRoomCount();
}

function populateCustomerTypes(selectElement) {
    fetch('/api/customer_types')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch customer types');
            }
            return response.json();
        })
        .then(custTypes => {
            if (custTypes.length === 0) {
                const option = document.createElement('option');
                option.textContent = 'No customer types available';
                selectElement.appendChild(option);
            } else {
                selectElement.innerHTML = ''; // Clear any existing options
                custTypes.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type.id;
                    option.textContent = type.name;
                    selectElement.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error loading customer types:', error);
            const option = document.createElement('option');
            option.textContent = 'Error loading customer types';
            selectElement.appendChild(option);
        });
}

function addCustomerRow() {
    const customerTableBody = document.querySelector("#customerTableBody");
    const rows = customerTableBody.getElementsByTagName('tr');
    const lastRow = rows[rows.length - 1];
    const inputs = lastRow.querySelectorAll('input');

    if (Array.from(inputs).every(input => input.value.trim() !== '')) {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td><input type="text" class="form-control" placeholder="Tên khách hàng"></td>
            <td>
                <select class="form-select customerTypeSelect">
                </select>
            </td>
            <td><input type="text" class="form-control" placeholder="CMND"></td>
            <td><input type="text" class="form-control" placeholder="Địa chỉ"></td>
        `;
        customerTableBody.appendChild(newRow);

        // Populate the <select> element here
        populateCustomerTypes(newRow.querySelector(".customerTypeSelect"));

        updateGuestCount();
    } else {
        alert('Vui lòng điền đủ thông tin khách hàng hiện tại trước khi thêm khách hàng khác.');
    }
}

function removeCustomerRow() {
    const rows = customerTableBody.getElementsByTagName('tr');
    if (rows.length > 1) {
        customerTableBody.removeChild(rows[rows.length - 1]);
        updateGuestCount();
    }
}

function updateGuestCount() {
    document.getElementById('num_guests').value = customerTableBody.getElementsByTagName('tr').length;
}

function formatPrice(price) {
    if (isNaN(price)) return price;
    return new Intl.NumberFormat('vi-VN', { style: 'decimal', maximumFractionDigits: 0 }).format(price) + ' VNĐ';
}

function confirmBooking(event) {
    event.preventDefault();

    if (!validateBookingForm()) return;

    const bookingData = {
        name: document.getElementById('name').value,
        checkin: document.getElementById('checkin').value,
        checkout: document.getElementById('checkout').value,
        num_guests: document.getElementById('num_guests').value,
        num_rooms: document.getElementById('num_rooms').value,
        selected_rooms: selectedRooms,
        customers: Array.from(customerTableBody.getElementsByTagName('tr')).map(row => ({
            name: row.querySelector('input[placeholder="Tên khách hàng"]').value,
            type: {
                id: row.querySelector('select').value,
                name: row.querySelector('select option:checked').textContent  // This captures the visible text
            },
            idNum: row.querySelector('input[placeholder="CMND"]').value,
            address: row.querySelector('input[placeholder="Địa chỉ"]').value
        }))
    };

    localStorage.setItem('bookingData', JSON.stringify(bookingData));
    window.location.href = 'booking_confirm';
}

function validateBookingForm() {
    if (selectedRooms.length === 0) {
        alert('Vui lòng chọn ít nhất một phòng để tiếp tục.');
        return false;
    }

    const rows = customerTableBody.getElementsByTagName('tr');
    for (const row of rows) {
        if (['Tên khách hàng', 'CMND', 'Địa chỉ'].some(placeholder => row.querySelector(`input[placeholder="${placeholder}"]`).value.trim() === '')) {
            alert('Vui lòng điền đầy đủ thông tin khách hàng.');
            return false;
        }
    }

    const checkin = document.getElementById('checkin').value;
    const checkout = document.getElementById('checkout').value;
    const today = new Date().toISOString().split('T')[0];

    if (!checkin || !checkout || checkin < today || checkout < today || checkin > checkout) {
        alert('Vui lòng kiểm tra lại ngày nhận phòng và trả phòng.');
        return false;
    }

    return true;
}

// Initial Updates
updateSelectedRoomCount();
updateGuestCount();
