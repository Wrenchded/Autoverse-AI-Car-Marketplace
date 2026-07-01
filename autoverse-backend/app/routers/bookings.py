from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user, require_buyer
router = APIRouter(prefix='/bookings', tags=['Test Drive Bookings'])

@router.post('/', response_model=schemas.BookingRead, status_code=201)
def create_booking(
    payload: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_buyer),
):
    
    car = db.query(models.Car).filter(models.Car.id == payload.car_id).first()
    if not car:
        raise HTTPException(404, 'Car not found.')
    if car.status != 'available':
        raise HTTPException(400, 'Car is not available for booking.')
    if payload.booking_date <= datetime.utcnow():
        raise HTTPException(400, 'Booking date must be in the future.')

    # Check no duplicate booking by same user for same car
    existing = db.query(models.TestDriveBooking).filter(
        models.TestDriveBooking.user_id == current_user.id,
        models.TestDriveBooking.car_id == payload.car_id,
        models.TestDriveBooking.status != 'cancelled',
    ).first()
    if existing:
        raise HTTPException(400, 'You already have an active booking for this car.')
    
    booking = models.TestDriveBooking(  
        user_id=current_user.id,
        car_id=payload.car_id,
        booking_date=payload.booking_date,
    )

    db.add(booking) 
    db.commit()
    db.refresh(booking)
    return booking

@router.get('/my', response_model=list[schemas.BookingRead])
def my_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    
    return db.query(models.TestDriveBooking).filter(
        models.TestDriveBooking.user_id == current_user.id
    ).order_by(models.TestDriveBooking.created_at.desc()).all()

@router.patch('/{booking_id}/cancel', response_model=schemas.BookingRead)
def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    booking = db.query(models.TestDriveBooking).filter(
        models.TestDriveBooking.id == booking_id
        ).first()
    if not booking:
        raise HTTPException(404, 'Booking not found.')
    if booking.user_id != current_user.id and current_user.role.value != 'admin':
        raise HTTPException(403, 'Not authorised to cancel this booking.')
    if booking.status == 'cancelled':
        raise HTTPException(400, 'Booking is already cancelled.')
    booking.status = 'cancelled'
    db.commit()
    db.refresh(booking)
    return booking