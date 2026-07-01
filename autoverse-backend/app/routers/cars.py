import logging
from app.services.price_service import predict_price, log_prediction
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from uuid import UUID
from typing import Optional
from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user, require_seller

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/cars', tags=['Cars'])

# List cars (public, with optional filters) 
@router.get('/', response_model=list[schemas.CarRead])

def list_cars(
    brand: Optional[str] = Query(None),
    fuel_type: Optional[str] = Query(None),
    max_price: Optional[float] = Query(None),
    min_year: Optional[int] = Query(None),
    transmission: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    
    q = db.query(models.Car).filter(models.Car.status == 'available')
    if brand: q = q.filter(models.Car.brand.ilike(f'%{brand}%'))
    if fuel_type: q = q.filter(models.Car.fuel_type == fuel_type)
    if max_price is not None: q = q.filter(models.Car.listed_price <= max_price)
    if min_year: q = q.filter(models.Car.year >= min_year)
    if transmission: q = q.filter(models.Car.transmission == transmission)
    return q.order_by(models.Car.created_at.desc()).all()

# ■■ Get single car 
@router.get('/{car_id}', response_model=schemas.CarRead)
def get_car(car_id: UUID, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(404, 'Car not found.')
    return car

# ■■ Seller: list a new car
@router.post('/', response_model=schemas.CarRead, status_code=201)
def create_car(
    payload: schemas.CarCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_seller),
):
    
    car = models.Car(**payload.model_dump(), seller_id=current_user.id)

    # Auto-run price prediction — don't fail listing if ML unavailable  
    try:
        features = payload.model_dump()
        car.predicted_price = predict_price(features)
        log_prediction(db, features, car.predicted_price)
        logger.info(f'Predicted price for new car: {car.predicted_price}')
    except Exception as e:  
        logger.warning(f'Price prediction skipped: {e}')

    db.add(car)
    db.commit()
    db.refresh(car)
    return car

# ■■ Seller/Admin: update car 
@router.patch('/{car_id}', response_model=schemas.CarRead)
def update_car(
    car_id: UUID,   
    payload: schemas.CarUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(404, 'Car not found.')

# Only the owning seller or an admin can update
    if current_user.role.value == 'buyer':
        raise HTTPException(403, 'Buyers cannot update listings.')
    if current_user.role.value == 'seller' and car.seller_id != current_user.id:
        raise HTTPException(403, 'You can only update your own listings.')
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(car, field, value)

    db.commit()
    db.refresh(car)
    return car

# ■■ Seller/Admin: delete car
@router.delete('/{car_id}', status_code=204)
def delete_car(
    car_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    car = db.query(models.Car).filter(models.Car.id == car_id).first()  
    if not car:
        raise HTTPException(404, 'Car not found.')
    if current_user.role.value == 'buyer':
        raise HTTPException(403, 'Buyers cannot delete listings.')
    if current_user.role.value == 'seller' and car.seller_id != current_user.id:
        raise HTTPException(403, 'You can only delete your own listings.')
    db.delete(car)
    db.commit()

    return {"message ": "Deleted Successfully"} # Added Safe Response

# ■■ Seller: view own listings 
@router.get('/my/listings', response_model=list[schemas.CarRead])
def my_listings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_seller),
):
    
    return db.query(models.Car).filter( 
        models.Car.seller_id == current_user.id
    ).all()

