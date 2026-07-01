from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app import models, schemas
from app.dependencies import require_seller
from app.services.damage_service import detect_damage, log_damage_result

router = APIRouter(prefix='/damage', tags=['Damage Detection'])

ALLOWED_MIME = {'image/jpeg', 'image/png', 'image/webp', 'image/jpg'}
MAX_BYTES = 5 * 1024 * 1024


@router.post('/detect', response_model=schemas.DamageResponse)
async def detect_car_damage(
    file: UploadFile = File(...)
):
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(400, "Unsupported image type")

    image_bytes = await file.read()

    if len(image_bytes) > MAX_BYTES:
        raise HTTPException(400, "Image exceeds 5MB limit")

    # Run AI model
    result = detect_damage(image_bytes)

    return result

    car = db.query(models.Car).filter(
        models.Car.id == car_id,
        models.Car.seller_id == current_user.id,
    ).first()

    if not car:
        raise HTTPException(404, "Car not found or not owned by you")

    result = detect_damage(image_bytes)

    car.damage_label = result['damage_label']
    car.damage_confidence = result['damage_confidence']
    car.damage_score = result['damage_score']

    db.commit()

    log_damage_result(db, str(car_id), result)

    return result