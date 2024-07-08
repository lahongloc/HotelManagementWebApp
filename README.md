<h1 align="center">🏨 Hotel Management WebApp</h1>

<h3 align="center">A comprehensive server-side rendering (SSR) web application for managing hotel bookings, built with Python Flask, SQLAlchemy, MySQL, and Bootstrap 4. This project demonstrates my skills in developing a fully functional hotel management system.</h3>

## ✨ Features
- **🔍 Hotel Room Search**: Search for hotel rooms based on various criteria such as date, price, room type, and more.
- **⭐ Hotel Room Reviews**: Customers can leave reviews for hotel rooms.
- **🛏️ Online Room Booking**: Customers can book rooms online and pay a deposit through VNPay.
- **🏨 Direct Room Booking**: Customers can book rooms directly at the hotel.
- **💳 Room Checkout**: Customers can check out and pay their room bill through VNPay.
- **📱 Twilio Integration**: Send payment information to customers' phones via SMS using Twilio.
- **📧 SMTP Integration**: Send thank-you emails to customers using SMTP. Both Twilio and SMTP run asynchronously.

## 🛠 Tech Stack

### Backend
- **🐍 Python Flask**
- **🛠 SQLAlchemy**
- **🐬 MySQL**

### Frontend
- **💻 Bootstrap 4**

### Payment and Communication
- **💳 VNPay**
- **📱 Twilio**
- **📧 SMTP**

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- MySQL

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/lahongloc/HotelManagementWebApp.git
    cd HotelManagementWebApp/HotelManagementProject
    ```

2. **Backend Setup:**
    **Steps to run the project after cloning:**

    - **Step 1:** Create a virtual environment (venv)

    - **Step 2:** Install the required libraries from `requirements.txt`:
      ```sh
      pip install -r requirements.txt
      ```
    - **Step 3:** Connect to the database via MySQL Workbench by configuring the database name and password in the `init.py` file:

      Edit lines 9-10 in `init.py`:
      ```python
      app.config["SQLALCHEMY_DATABASE_URI"] = str.format("mysql+pymysql://root:{}@localhost/yourDatabaseName?charset=utf8mb4",
                                                         "yourDatabasePassword")
      ```
      Replace `yourDatabaseName` with the name of your MySQL database and `yourDatabasePassword` with your MySQL password.

    - **Step 4:** Run `models.py` to create tables in the database:
      ```python
      from your_application import db
      db.create_all()
      ```

      Run individual blocks of code to insert data into the tables.

    - **Step 5:** Fix the `markup` bug:
      - Navigate to `venv -> lib -> flask_recaptcha.py`.
      - On line 14, replace `jinja2` with `markupsafe`:
        ```python
        from markupsafe import escape
        ```

    - **Step 6:** Save the changes and run `index.py`:
      ```sh
      python index.py
      ```

    - **Step 7:** Open your browser and go to `http://localhost:{port}` to see if the application is running.

## 💡 Usage

### 🔐 Authentication
- **Admin Login**: Admin can log in and manage all features.
- **Customer Login**: Customers can log in to book rooms, leave reviews, and manage their bookings.

### 📋 Core Features
1. **Hotel Room Search**:
    - Search rooms based on date, price, room type, and more.
  
2. **Hotel Room Reviews**:
    - Leave and view reviews for hotel rooms.

3. **Online Room Booking**:
    - Book rooms online and pay a deposit via VNPay.

4. **Direct Room Booking**:
    - Book rooms directly at the hotel without online payment.

5. **Room Checkout**:
    - Check out from the hotel and pay the room bill via VNPay.

6. **Twilio Integration**:
    - Receive payment information via SMS.

7. **SMTP Integration**:
    - Receive thank-you emails asynchronously.

## 📸 Screenshots
_Add screenshots of your application here to give visual insight into its functionality._

## 🤝 Contributing
- Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.

## 📞 Contact
- **Name**: La Hồng Lộc
- **Email**: hongloc111990@gmail.com
- **LinkedIn**: www.linkedin.com/in/hongloc2405
