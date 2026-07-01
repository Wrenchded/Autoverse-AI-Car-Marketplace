import joblib
import pandas as pd
import os
import logging
from app import models
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
    
_MODEL = None
_FEATURES = None

def _load_model():
    global _MODEL, _FEATURES
    if _MODEL is None:
        base = os.path.dirname(__file__)
        # Ensure these paths are correct relative to your service file
        _MODEL = joblib.load(os.path.join(base, '..', 'ml_models', 'price_model.pkl'))
        _FEATURES = joblib.load(os.path.join(base, '..', 'ml_models', 'price_features.pkl'))
        logger.info('Price model loaded.')

def predict_price(input_dict: dict) -> float:
    _load_model()

    # 1. Define the Mappings
    # These MUST match the order/numbers used during your model training
    mappings = {
        'Fuel_Type': {'Petrol': 0, 'Diesel': 1, 'Electric': 2},
        'Seller_Type': {'Dealer': 0, 'Individual': 1},
        'Transmission': {'Manual': 0, 'Automatic': 1}
    }

    # 2. Transform the strings in input_dict to numbers
    processed_dict = input_dict.copy()
    for column, mapping in mappings.items():
        if column in processed_dict:
            val = processed_dict[column]
            # Use .get() to avoid crashing if a value is missing; default to 0
            processed_dict[column] = mapping.get(val, 0)

    # 3. Build DataFrame with correct column order using the processed dict
    try:
        df = pd.DataFrame([processed_dict])[_FEATURES]
        prediction = _MODEL.predict(df)
        price = float(prediction[0])    
        return max(round(price, 2), 0) 
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise RuntimeError(f"Model Inference Error: {str(e)}")

def log_prediction(db: Session, input_data: dict, predicted_price: float) -> None:
    entry = models.ModelLog(
        model_type = 'price',
        input_data = input_data,
        output_data = {'predicted_price': predicted_price},
    )
    db.add(entry)
    db.commit()