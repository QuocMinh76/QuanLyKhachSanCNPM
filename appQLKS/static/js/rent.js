//// Function to handle the change event for room selection
function handleRoomSelectionChange(event) {
    const selectElement = event.target; // The select element that was changed
    const selectedRoomId = selectElement.value; // The selected room ID

    // Get the maxCust value from the selected option's data-max-cust attribute
    const maxCust = parseInt(selectElement.selectedOptions[0]?.dataset.maxCust, 10);

    if (!selectedRoomId || isNaN(maxCust)) {
        return; // Exit if no room is selected or maxCust is invalid
    }

    // Count the total number of customers assigned to the selected room across all select elements
    const allSelectElements = document.querySelectorAll('select.form-select');
    let roomCustomerCount = 0;

    allSelectElements.forEach(select => {
        if (select.value === selectedRoomId) {
            roomCustomerCount++; // Increment the count if the same room is selected
        }
    });

    // If the customer count exceeds maxCust, show an alert and retain the previous selection
    if (roomCustomerCount > maxCust) {
        alert('Phòng này đã đủ số lượng khách, vui lòng chọn phòng khác!');
        selectElement.value = selectElement.dataset.previousValue || ""; // Retain the previous value
    } else {
        // If the selection is valid, store the current selection as the previous value
        selectElement.dataset.previousValue = selectedRoomId;
    }
}

document.querySelectorAll('select.form-select').forEach(select => {
    select.addEventListener('change', handleRoomSelectionChange);
});

// Function to initialize event listeners for all room select elements
function initializeRoomValidation() {
    const roomSelectElements = document.querySelectorAll('select.form-select');

    roomSelectElements.forEach(selectElement => {
        // Store the initial value of the select element as the previous value
        selectElement.dataset.previousValue = selectElement.value;

        selectElement.addEventListener('change', handleRoomSelectionChange);
    });
}

// Initialize validation when the document is fully loaded
document.addEventListener('DOMContentLoaded', initializeRoomValidation);

document.addEventListener("DOMContentLoaded", function () {
    const confirmButton = document.getElementById("confirmButton");
    const customerRoomField = document.getElementById("cust_room"); // Reuse 'rooms' field for simplicity

    confirmButton.addEventListener("click", function (event) {
        // Ensure the hidden field exists
        if (!customerRoomField) {
            console.error("Hidden input field for customer-room mapping is missing.");
            return;
        }

        // Collect customer-to-room mapping
        const customerRoomMapping = [];

        const roomOptions = document.querySelectorAll("select[name^='room_select_']");
        roomOptions.forEach(select => {
            const customerId = select.name.replace("room_select_", "");
            const roomId = select.value;

            if (roomId) {
                customerRoomMapping.push({
                    customerId: customerId,
                    roomId: roomId
                });
            }
        });

        // Debugging: Log the customer-room mapping
        console.log("Customer-Room Mapping:", customerRoomMapping);

        // Serialize and store in the hidden input
        customerRoomField.value = JSON.stringify(customerRoomMapping);

        // Debugging: Verify hidden field value
        console.log("Hidden Field Value:", customerRoomField.value);

        // Trường hợp confirmBookingButton đã bấm trước, thì xác nhận lại trạng thái phòng sau 30 giây
        setTimeout(() => {
            // Sau 30 giây, cần cập nhật lại trạng thái phòng
            const bookingData = JSON.parse(localStorage.getItem('bookingData'));
            if (bookingData && bookingData.selected_rooms) {
                bookingData.selected_rooms.forEach(room => {
                    if (room.status !== 'Unavailable') {
                        room.status = 'Available'; // Đặt lại trạng thái phòng thành "Sẵn sàng"
                    }
                });
                localStorage.setItem('bookingData', JSON.stringify(bookingData));
                console.log('Trạng thái phòng đã được cập nhật lại sau 30 giây');
            }
        }, 5000); // 30 giây
    });
});

// Mai xem lại cái qq dưới này
// Function to check if all select tags have a selection
function checkAllRowsSelected() {
    const selectElements = document.querySelectorAll('select.form-select');
    const confirmButton = document.getElementById('confirmButton'); // Confirm button with id

    let allSelected = true;

    // Loop through each select tag to check if a selection is made
    selectElements.forEach(select => {
        if (!select.value) {
            allSelected = false; // If any select has no value, set allSelected to false
        }
    });

    // Enable or disable the confirm button based on the selection status
    if (allSelected) {
        confirmButton.disabled = false; // Enable the button if all selects are filled
    } else {
        confirmButton.disabled = true; // Disable the button if any select is empty
    }
}

// Initialize event listeners to check for changes in the selects
function initializeSelectionValidation() {
    const selectElements = document.querySelectorAll('select.form-select');

    selectElements.forEach(select => {
        select.addEventListener('change', checkAllRowsSelected); // Add event listener on change
    });

    // Also check on page load in case there are any pre-selected options
    checkAllRowsSelected();
}

// Call the initialize function when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Ensure all elements are loaded before running the function
    initializeSelectionValidation();
});


