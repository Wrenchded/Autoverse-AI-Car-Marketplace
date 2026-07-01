import uuid
from datetime import datetime
from sqlalchemy import (
Column, String, Integer, Float, Boolean, DateTime,
ForeignKey, Enum, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum

# ■■■ Enum definitions --------------------------------
class UserRole(str, enum.Enum):
    buyer = 'buyer' 
    seller = 'seller'
    admin = 'admin'

class CarStatus(str, enum.Enum):
    available = 'available'
    sold = 'sold'
    rented = 'rented'
    pending = 'pending'

class FuelType(str, enum.Enum):
    petrol = 'petrol'
    diesel = 'diesel'
    electric = 'electric'
    hybrid = 'hybrid'
    cng = 'cng'

class Transmission(str, enum.Enum):
    manual = 'manual'
    automatic = 'automatic'

class BookingStatus(str, enum.Enum):
    pending = 'pending'
    confirmed = 'confirmed'
    cancelled = 'cancelled'

class RentalStatus(str, enum.Enum):
    active = 'active'
    completed = 'completed'
    cancelled = 'cancelled'

class ModelType(str, enum.Enum):
    price = 'price'
    recommendation = 'recommendation'
    damage = 'damage'

# ■■■ User table --------------------------------
class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True,
    default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.buyer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # one-to-many relationships
    cars = relationship('Car', back_populates='seller', cascade='all, delete-orphan')
    test_drive_bookings = relationship('TestDriveBooking', back_populates='user', cascade='all, delete-orphan')
    rentals = relationship('Rental', back_populates='user', cascade='all, delete-orphan')

# ■■■ Car table --------------------------------
class Car(Base):
    __tablename__ = 'cars'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    mileage = Column(Float, nullable=False)
    fuel_type = Column(Enum(FuelType), nullable=False)
    transmission = Column(Enum(Transmission), nullable=False)
    engine = Column(Float, nullable=True) # cc or litres
    body_type = Column(String(50), nullable=True)
    listed_price = Column(Float, nullable=False)
    predicted_price = Column(Float, nullable=True) # ML-filled
    damage_label = Column(String(20), nullable=True)
    damage_confidence = Column(Float, nullable=True)
    damage_score = Column(Float, nullable=True)
    status = Column(Enum(CarStatus), default=CarStatus.available)
    created_at = Column(DateTime, default=datetime.utcnow)
    seller = relationship('User', back_populates='cars')

    test_drive_bookings = relationship('TestDriveBooking', back_populates='car', cascade='all, delete-orphan')
    rentals = relationship('Rental', back_populates='car', cascade='all, delete-orphan')

# ■■■ TestDriveBooking table --------------------------------
class TestDriveBooking(Base):
    __tablename__ = 'test_drive_bookings'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    car_id = Column(UUID(as_uuid=True), ForeignKey('cars.id', ondelete='CASCADE'), nullable=False)
    booking_date = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='test_drive_bookings')
    car = relationship('Car', back_populates='test_drive_bookings')

# ■■■ Rental table --------------------------------
class Rental(Base):
    __tablename__ = 'rentals'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    car_id = Column(UUID(as_uuid=True), ForeignKey('cars.id', ondelete='CASCADE'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(RentalStatus), default=RentalStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='rentals')
    car = relationship('Car', back_populates='rentals')

# ■■■ ModelLog table --------------------------------
class ModelLog(Base):
    __tablename__ = 'model_logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_type = Column(Enum(ModelType), nullable=False)
    input_data = Column(JSON, nullable=False) # dict stored as JSONB
    output_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)