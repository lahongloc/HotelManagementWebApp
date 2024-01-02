from app import app, db
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime, Float
from sqlalchemy.orm import Relationship
from enum import Enum as CommonEnum


class UserRole(CommonEnum):
    ADMIN = 1
    SERVICE_STAFF = 2
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
    comments = Relationship('Comment', backref='customer', lazy=True)

    def __str__(self):
        return self.id


class RoomType(BaseModel):
    name = Column(String(50), nullable=False)
    room_type = Column(Enum(RoomEnum), default=RoomEnum.SINGLE_BED_ROOM)
    rooms = Relationship('Room', backref='room_type', lazy=True)

    def __str__(self):
        return self.name


class Room(BaseModel):
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)
    reservations = Relationship('Reservation', backref='room', lazy=True)
    room_rental = Relationship('RoomRental', backref='room', lazy=True)
    comments = Relationship('Comment', backref='room', lazy=True)


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


class RoomRegulation(BaseModel):
    admin_id = Column(Integer, ForeignKey(Admin.id), nullable=False)
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)


class CustomerTypeRegulation(BaseModel):
    admin_id = Column(Integer, ForeignKey(Admin.id), nullable=False)
    customer_type_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False)


if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        # db.create_all()
        rt1 = RoomType(name='1 Guest, 1 Bed')
        rt2 = RoomType(name='2 Guest, 2 Bed', room_type=RoomEnum.TWIN_BED_ROOM)
        rt3 = RoomType(name='3 Guest, 2 Bed', room_type=RoomEnum.DOUBLE_BED_ROOM)
        db.session.add_all([rt1, rt2, rt3])
        db.session.commit()
