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
- **📊 Statistics Reporting (Chart.js)**: Sales and revenue statistics by year, quarter, month, room types.

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

## 🖼️ System Design Analysis

### Class Diagram
- ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/dc027df9-ffc9-4a8f-abdf-098f4739566d)

### Relational Database Schema
- ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/bcb0dd26-bf45-4c64-9cf6-cf72f53f3948)

### Use Case Diagram
- ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/1ad78f29-30d7-4f36-b62b-9b1abb5f365d)

### Interface Design (Mockflow)
- Home page: ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/227d4945-13c8-4f37-af82-b058ebbf6d89)
- Customer - online booking:
  ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/1b084206-08d4-4e9e-9c89-3dbb8eacfe75)
  ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/f065f9be-30e8-493d-98d8-8c173df283a8)
  ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/cad8190a-797a-44e1-953a-bbf2b1a6eedb)
- Staff - direct booking: ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/a0b21aff-aa57-4150-acb5-12a43f298213)
- Staff - book room for customer: ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/99165b58-e325-4354-b7f8-a3ca18317bed)
  
## 📸 Screenshots
- Home page: ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/10b31cff-6f2d-4224-b53e-9669e1cc48dd)
- Room detail: ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/4867dc82-2454-44c3-b442-ac232ec6d7d1)
- Room booking and online payment: ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/06c54fbb-b71e-4d07-a08b-c9ed3698aeff)
- Generate receipt: ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/92c37a93-fef2-42f6-ae8e-852368f6de23)
- VNpay:
  ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/c700e68a-417b-4bf6-ba84-3c443d66d160)
  ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/f6c14b96-9c3b-4fce-9646-89e78f7e8b5f)
- Direct booking: ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/41b374d5-f373-46ab-a272-007aa18aa49c)
- Room checking-in: ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/940c26e1-c67d-4a09-a1d2-6f073c74136a)
- Report anf Statistics page: ![image](https://github.com/lahongloc/HotelManagementWebApp/assets/109413731/a04f556f-6b94-4459-8d87-e0a3aeaa1d7e)

## 🤝 Contributing
- Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.

## 📞 Contact
- **Name**: La Hồng Lộc
- **Email**: hongloc111990@gmail.com
- **LinkedIn**: www.linkedin.com/in/hongloc2405
