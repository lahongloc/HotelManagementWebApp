from app import app, db
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime, Float
from sqlalchemy.orm import Relationship
from enum import Enum as CommonEnum
from flask_login import UserMixin


class UserRole(CommonEnum):
    ADMIN = 1
    SERVICE_STAFF = 2
    RECEPTIONIST = 3
    CUSTOMER = 4


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)


class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False)
    identification = Column(String(15), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    phone = Column(String(50), nullable=False, unique=True)
    avatar = Column(String(100))
    gender = Column(Boolean, default=True)  # True = 1 is 'Man'


class Administrator(db.Model):
    id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    role = Column(Enum(UserRole), default=UserRole.ADMIN)


class ServiceStaff(db.Model):
    id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    role = Column(Enum(UserRole), default=UserRole.SERVICE_STAFF)
    service_records = Relationship('ServiceRecord', backref='service_staff', lazy=True)
    problem_records = Relationship('ProblemRecord', backref='service_staff', lazy=True)


class Receptionist(db.Model):
    id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    role = Column(Enum(UserRole), default=UserRole.RECEPTIONIST)
    reservations = Relationship('Reservation', backref='receptionist', lazy=True)
    room_rentals = Relationship('RoomRental', backref='receptionist', lazy=True)


class CustomerType(BaseModel):
    type = Column(String(50), default='DOMESTIC')
    customers = Relationship('Customer', backref='customer_type', lazy=True)

    def __str__(self):
        return self.type


class Customer(db.Model):
    id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    customer_type_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False)
    reservations = Relationship('Reservation', backref='customer', lazy=True)
    room_rentals = Relationship('RoomRental', backref='customer', lazy=True)
    comments = Relationship('Comment', backref='customer', lazy=True)

    def __str__(self):
        return self.id


class RoomType(BaseModel):
    name = Column(String(50), nullable=False, unique=True)
    rooms = Relationship('Room', backref='room_type', lazy=True)

    def __str__(self):
        return self.name


class Room(BaseModel):
    name = Column(String(50), nullable=False, unique=True)
    image = Column(String(500), nullable=False)
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)
    reservations = Relationship('Reservation', backref='room', lazy=True)
    room_rentals = Relationship('RoomRental', backref='room', lazy=True)
    comments = Relationship('Comment', backref='room', lazy=True)

    def __str__(self):
        return self.name


class Reservation(BaseModel):
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    is_at_hotel = Column(Boolean, default=False)
    receptionist_id = Column(Integer, ForeignKey(Receptionist.id))
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)


class RoomRental(BaseModel):
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    receptionist_id = Column(Integer, ForeignKey(Receptionist.id), nullable=False)
    is_received_room = Column(Boolean)
    room_id = Column(Integer, ForeignKey(Room.id))  # null if is_received_room == True
    reservation_id = Column(Integer, ForeignKey(Reservation.id))  # null if is_received_room == False

    receipt = Relationship('Receipt', uselist=False, back_populates='room_rental')


#
class ServiceRecord(BaseModel):
    description = Column(String(1000))
    price = Column(Float)
    service_staff_id = Column(Integer, ForeignKey(ServiceStaff.id), nullable=False)
    receipt = Relationship('Receipt', uselist=False, back_populates='service_record')


class ProblemRecord(BaseModel):
    description = Column(String(1000))
    price = Column(Float)
    service_staff_id = Column(Integer, ForeignKey(ServiceStaff.id), nullable=False)
    receipt = Relationship('Receipt', uselist=False, back_populates='problem_record')


class Receipt(BaseModel):
    rental_room_id = Column(Integer, ForeignKey(RoomRental.id), nullable=False)
    room_rental = Relationship('RoomRental', back_populates='receipt')
    service_record_id = Column(Integer, ForeignKey(ServiceRecord.id))
    service_record = Relationship('ServiceRecord', back_populates='receipt')
    problem_record_id = Column(Integer, ForeignKey(ProblemRecord.id))
    problem_record = Relationship('ProblemRecord', back_populates='receipt')


class Comment(db.Model):
    id = Column(Integer, ForeignKey(Customer.id), nullable=False,
                primary_key=True)  # primary key as well as foreign key
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False, primary_key=True)


class RoomRegulation(db.Model):
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False, primary_key=True)
    admin_id = Column(Integer, ForeignKey(Administrator.id), nullable=False)
    room_quantity = Column(Integer, default=10)
    capacity = Column(Integer, default=2)
    price = Column(Float, default=100000)


class CustomerTypeRegulation(BaseModel):
    rate = Column(Float, default=1.0, nullable=False)
    admin_id = Column(Integer, ForeignKey(Administrator.id), nullable=False)
    customer_type_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False)


if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        # db.create_all()

        # rt1 = RoomType(name='SINGLE BEDROOM')
        # rt2 = RoomType(name='TWIN BEDROOM')
        # rt3 = RoomType(name='DOUBLE BEDROOM')
        # db.session.add_all([rt1, rt2, rt3])
        # db.session.commit()

        # r1 = Room(name='A01', room_type_id=2, image='images/p1.png')
        # r2 = Room(name='A02', room_type_id=3, image='images/p2.png')
        # r3 = Room(name='A03', room_type_id=2, image='images/p3.png')
        # r4 = Room(name='A04', room_type_id=1, image='images/p4.png')
        # r5 = Room(name='A05', room_type_id=3, image='images/p5.png')
        # db.session.add_all([r1, r2, r3, r4, r5])
        # db.session.commit()

        # import hashlib
        # user1 = User(name='Loc',
        #                  identification='192137035',
        #                  username='locla123',
        #                  password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
        #                  avatar = 'https://cdn.pixabay.com/photo/2020/07/14/13/07/icon-5404125_1280.png',
        #                  email='loc@gmail.com',
        #                  phone='0334454203')
        # db.session.add(user1)
        # db.session.commit()

        # admin1 = Administrator(id=2)
        # db.session.add(admin1)
        # db.session.commit()

        # ct1 = CustomerType()
        # ct2 = CustomerType(type='FOREIGN')
        # db.session.add_all([ct1, ct2])
        # db.session.commit()

        ctr1 = CustomerTypeRegulation(admin_id=2, customer_type_id=1)
        ctr2 = CustomerTypeRegulation(admin_id=2, customer_type_id=2, rate=1.5)
        db.session.add_all([ctr1, ctr2])
        db.session.commit()

        # cus1 = Customer(id=1, customer_type_id=2)
        # db.session.add(cus1)
        # db.session.commit()

        # rr1 = RoomRegulation(room_type_id=1, admin_id=2, room_quantity=10, capacity=3, price=500000)
        # rr2 = RoomRegulation(room_type_id=2, admin_id=2, room_quantity=15, capacity=3, price=1500000)
        # rr3 = RoomRegulation(room_type_id=3, admin_id=2, room_quantity=17, capacity=3, price=2000000)
        # db.session.add_all([rr1, rr2, rr3])
        # db.session.commit()
