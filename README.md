# Hotel Booking Website

A hotel booking web application developed by a team of 3 using **Python Flask**.  
The system supports multiple user roles with distinct capabilities, including normal users, hotel employees, and administrators.

## Finished product
We used pythonanywhere to host the web application: https://hqminh.pythonanywhere.com/.

However, the booking timeout system has been deactivate, as APScheduler has very limited supports by pythonanywhere.

## 🌐 Features

### 👤 Normal Users
- Search and book available rooms.
- View booking history.
- Leave comments or reviews on past stays.

### ⏳ Booking Timeout System
- When a user places a booking, the room is **temporarily marked as booked**.
- If the user does **not proceed with the order** within a configurable time limit, the room is **automatically made available again**.
- Timeout duration is set by the **admin**.
- Implemented using **APScheduler** to manage scheduled background tasks.

### 🧾 Employees
- View placed booking orders.
- Manage and update payment statuses.

### 🔧 Administrators
- Access the full admin panel.
- All privileges of employee-level users.
- Full CRUD (Create, Read, Update, Delete) control over:
  - Rooms
  - Bookings
  - Users
  - Customers
  - Bills, and more.
- Access a **statistics dashboard** with data visualizations to monitor hotel performance.
- Configure **booking timeout duration**.

## 🛠️ Tech Stack
- **Python Flask** – Web framework
- **MySQL** – Database
- **HTML, CSS, Bootstrap** – Frontend
- **Flask-Login** – Authentication and role management
- **APScheduler** – Handles background scheduling (e.g., booking timeouts)
- **Chart.js** – For generating statistical reports

## 👥 Team & Contributions

| Name         | Contributions                                                                 |
|--------------|--------------------------------------------------------------------------------|
| Hoàng Quốc Minh   | Implemented admin panel, booking timeout logic and normal user features (search, booking, review system)  |
| Lê Thị Yến My     | Built exporting orders and bills to PDF system, designed various views UI |
| Trần Tuấn Kiệt    | Developed employee-level features, payment management logic, and statistics   |

> The team members also shared the workloads in other aspects of the website.

## 🔒 License

This project is for educational purposes and not licensed for commercial distribution.
