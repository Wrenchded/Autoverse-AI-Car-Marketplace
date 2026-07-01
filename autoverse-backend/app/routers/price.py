from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas
from app.services.price_service import predict_price, log_prediction
from datetime import datetime

router = APIRouter(prefix='/price', tags=['Price Prediction'])

@router.post('/predict', response_model=schemas.PricePredictResponse)
def predict(payload: dict, db: Session = Depends(get_db)): # Use dict if schema is strict
    try:
        # 1. Feature Engineering (Calculating 'car_age')
        current_year = datetime.now().year
        car_age = current_year - payload.get('year', 2020)

        # 2. Map frontend names to EXACT dataset column names
        # This solves the KeyError: "None of [Index([...])] are in the [columns]"
        input_dict = {
            'Present_Price_INR': payload.get('present_price'),
            'Kms_Driven': payload.get('mileage'),
            'Fuel_Type': payload.get('fuel_type'),
            'Seller_Type': payload.get('seller_type'),
            'Transmission': payload.get('transmission'),
            'Owner': payload.get('owner'),
            'car_age': car_age
        }

        # 3. Call service
        price = predict_price(input_dict)
        
        # 4. Log to DB
        log_prediction(db, input_dict, price)
        
        return {'predicted_price': float(price)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Model Error: {str(e)}")