from app import app, db
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime, Float
from sqlalchemy.orm import Relationship
from enum import Enum as CommonEnum


class UserRole(CommonEnum):
    ADMIN = 1
    WAITER = 2
    RECEPTIONIST = 3
    CUSTOMER = 4


class CustomerEnum(CommonEnum):
    DOMESTIC = 1
    FOREIGN = 2


class RoomEnum(CommonEnum):
    SINGLE_BED_ROOM = 1
    TWIN_BED_ROOM = 2
    DOUBLE_BED_ROOM = 3


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)


class User(BaseModel):
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    email = Column(String(50))
    phone = Column(String(50), nullable=False)


class Admin(db.Model):
    id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    role = Column(Enum(UserRole), default=UserRole.ADMIN)
    # room_regulations = Relationship('RoomRegulation', backref='admin', lazy=True)


class Waiter(db.Model):
    id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    role = Column(Enum(UserRole), default=UserRole.WAITER)
    services = Relationship('Service', backref='waiter', lazy=True)
    problems = Relationship('Problem', backref='waiter', lazy=True)


class Receptionist(db.Model):
    id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    role = Column(Enum(UserRole), default=UserRole.RECEPTIONIST)
    reservations = Relationship('Reservation', backref='receptionist', lazy=True)
    room_rentals = Relationship('RoomRental', backref='receptionist', lazy=True)


class CustomerType(BaseModel):
    type = Column(Enum(CustomerEnum), default=CustomerEnum.FOREIGN)
    customers = Relationship('Customer', backref='customer_type', lazy=True)

    def __str__(self):
        return self.type


class Customer(db.Model):
    id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    customer_type_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False)
    reservations = Relationship('Reservation', backref='customer', lazy=True)
    room_rentals = Relationship('RoomRental', backref='customer', lazy=True)
    rates = Relationship('Rate', backref='customer', lazy=True)

    def __str__(self):
        return self.id


class RoomType(BaseModel):
    room_type = Column(Enum(RoomEnum), default=RoomEnum.SINGLE_BED_ROOM)
    rooms = Relationship('Room', backref='room_type', lazy=True)

    def __str__(self):
        return self.type


class Room(BaseModel):
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)
    reservations = Relationship('Reservation', backref='room', lazy=True)
    room_rental = Relationship('RoomRental', backref='room', lazy=True)
    rates = Relationship('Rate', backref='room', lazy=True)


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
class Service(BaseModel):
    description = Column(String(1000))
    price = Column(Float)
    waiter_id = Column(Integer, ForeignKey(Waiter.id), nullable=False)
    receipt = Relationship('Receipt', uselist=False, back_populates='service')


class Problem(BaseModel):
    description = Column(String(1000))
    price = Column(Float)
    waiter_id = Column(Integer, ForeignKey(Waiter.id), nullable=False)
    receipt = Relationship('Receipt', uselist=False, back_populates='problem')


class Receipt(BaseModel):
    rental_room_id = Column(Integer, ForeignKey(RoomRental.id), nullable=False)
    room_rental = Relationship('RoomRental', back_populates='receipt')
    service_id = Column(Integer, ForeignKey(Service.id))
    service = Relationship('Service', back_populates='receipt')
    problem_id = Column(Integer, ForeignKey(Problem.id))
    problem = Relationship('Problem', back_populates='receipt')


class Rate(db.Model):
    id = Column(Integer, ForeignKey(Customer.id), nullable=False,
                primary_key=True)  # primary key as well as foreign key
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False, primary_key=True)


class RoomRegulation(BaseModel):
    admin_id = Column(Integer, ForeignKey(Admin.id), nullable=False)
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)


class CustomerTypeRegulation(BaseModel):
    admin_id = Column(Integer, ForeignKey(Admin.id), nullable=False)
    customer_type_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
