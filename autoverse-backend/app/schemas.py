from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models import UserRole, CarStatus, BookingStatus, RentalStatus, FuelType, Transmission
# ■■■ Auth schemas ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None

# ■■■ User schemas ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.buyer

@field_validator('password')
@classmethod
def password_strength(cls, v: str) -> str:
    if not any(c.isdigit() for c in v):
        raise ValueError('Password must contain at least one digit.')
    return v

class UserRead(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    model_config = {'from_attributes': True}

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None

# ■■■ Car schemas ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
class CarCreate(BaseModel):
    brand: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1990, le=2025)
    mileage: float = Field(..., ge=0)
    fuel_type: FuelType
    transmission: Transmission
    engine: Optional[float] = Field(None, ge=0)
    body_type: Optional[str] = Field(None, max_length=50)
    listed_price: float = Field(..., gt=0)

class CarRead(BaseModel):
    id: UUID
    seller_id: UUID
    brand: str
    model: str
    year: int
    mileage: float
    fuel_type: FuelType
    transmission: Transmission
    engine: Optional[float] 
    body_type: Optional[str]
    listed_price: float
    predicted_price: Optional[float]
    damage_label: Optional[str] 
    damage_confidence: Optional[float]
    damage_score: Optional[float]
    status: CarStatus
    created_at: datetime
    model_config = {'from_attributes': True}

class CarUpdate(BaseModel):
    brand: Optional[str] = None 
    model: Optional[str] = None
    year: Optional[int] = None
mileage: Optional[float] = None
fuel_type: Optional[FuelType] = None
transmission: Optional[Transmission] = None
engine: Optional[float] = None
body_type: Optional[str] = None
listed_price: Optional[float] = None
status: Optional[CarStatus] = None

# ■■■ Booking schemas ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
class BookingCreate(BaseModel):
    car_id: UUID
    booking_date: datetime

class BookingRead(BaseModel):
    id: UUID
    user_id: UUID
    car_id: UUID
    booking_date: datetime
    status: BookingStatus
    created_at: datetime
    model_config = {'from_attributes': True}

# ■■■ Rental schemas ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
class RentalCreate(BaseModel):
    car_id: UUID
    start_date: datetime
    end_date: datetime
@model_validator(mode='after')
def end_after_start(self):
    if self.end_date <= self.start_date:
        raise ValueError('end_date must be after start_date')
        return self

class RentalRead(BaseModel):
    id: UUID
    user_id: UUID
    car_id: UUID
    start_date: datetime
    end_date: datetime
    total_price: float
    status: RentalStatus
    created_at: datetime
    model_config = {'from_attributes': True}

# ■■■ ML schemas ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
class PricePredictRequest(BaseModel):
    brand: str
    model: str
    year: int = Field(..., ge=1990, le=2025)
    mileage: float = Field(..., ge=0)
    fuel_type: FuelType
    transmission: Transmission
    engine: Optional[float] = None
    body_type: Optional[str] = None

class PricePredictResponse(BaseModel):
    predicted_price: float
    confidence_interval: Optional[dict] = None

class DamageResponse(BaseModel):
    damage_label: str # 'damaged' | 'undamaged'
    damage_confidence: float
    damage_score: float

# ■■■ Analytics schema ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
class AnalyticsSummary(BaseModel):
    total_users: int
    total_cars: int
    available_cars: int
    avg_listed_price: float
    avg_predicted_price: Optional[float]
    total_bookings: int
    total_rentals: int  
    rental_revenue: float
    damage_rate_pct: float