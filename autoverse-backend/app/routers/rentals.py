from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user, require_buyer
router = APIRouter(prefix='/rentals', tags=['Rentals'])


DAILY_RATE = 50.0 # USD per day — adjust as needed

@router.post('/', response_model=schemas.RentalRead, status_code=201)
def create_rental(
    payload: schemas.RentalCreate,
    db: Session = Depends(get_db),  
    current_user: models.User = Depends(require_buyer),
):
    
    car = db.query(models.Car).filter(models.Car.id == payload.car_id).first()
    if not car:
        raise HTTPException(404, 'Car not found.')
    if car.status != 'available':
        raise HTTPException(400, 'Car is not available for rent.')

    days = (payload.end_date - payload.start_date).days
    if days <= 0:   
        raise HTTPException(400, 'Rental must be at least 1 day.')

    total = round(days * DAILY_RATE, 2)

    rental = models.Rental(
        user_id = current_user.id,
        car_id = payload.car_id,
        start_date = payload.start_date,
        end_date = payload.end_date,
        total_price = total,
    )
    car.status = 'rented' # mark car unavailable
    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental

@router.get('/my', response_model=list[schemas.RentalRead])
def my_rentals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  
):
    return db.query(models.Rental).filter(
        models.Rental.user_id == current_user.id
    ).all()

@router.patch('/{rental_id}/complete', response_model=schemas.RentalRead, dependencies=[Depends(require_buyer)])

def complete_rental(
    rental_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental or rental.user_id != current_user.id:
        raise HTTPException(404, 'Rental not found.')
    if rental.status != 'active':
        raise HTTPException(400, 'Rental is not active.')
    rental.status = 'completed'
    rental.car.status = 'available' # free up the car
    db.commit()
    db.refresh(rental)
    return rental