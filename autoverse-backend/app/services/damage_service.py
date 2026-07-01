import numpy as np
import tensorflow as tf
import os
import logging
from sqlalchemy.orm import Session
from app import models
from app.utils.image_processing import preprocess_image

logger = logging.getLogger(__name__)

# Global model (loaded once)
_MODEL = None


def _load_model():
    global _MODEL

    if _MODEL is not None:
        return

    try:
        BASE_DIR = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )

        path = os.path.join(BASE_DIR, "ml_models", "damage_model.h5")

        print("🔥 MODEL PATH:", path)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Model not found at {path}")

        _MODEL = tf.keras.models.load_model(path)
        print("✅ Damage model loaded successfully")

    except Exception as e:
        print("❌ Model load error:", e)
        _MODEL = None


def detect_damage(image_bytes: bytes) -> dict:
    """
    Runs damage detection on uploaded image.
    Returns:
        damage_label: 'damaged' or 'undamaged'
        damage_confidence: confidence score
        damage_score: % damage (0–100)
    """

    _load_model()

    if _MODEL is None:
        logger.error("❌ Model not loaded.")
        return {
            'damage_label': 'unknown',
            'damage_confidence': 0.0,
            'damage_score': 0.0
        }

    # Preprocess image
    img = preprocess_image(image_bytes)

    # Prediction
    score = float(_MODEL.predict(img, verbose=0)[0][0])

    # Interpret sigmoid output
    if score >= 0.5:
        label = 'undamaged'
        confidence = score
    else:
        label = 'damaged'
        confidence = 1.0 - score

    damage_percent = (1 - score) * 100

    logger.info(f"Prediction → score: {score}, label: {label}")

    return {
        'damage_label': label,
        'damage_confidence': round(confidence, 4),
        'damage_score': round(damage_percent, 2),
    }

    # Preprocess image
    img = preprocess_image(image_bytes)

    # Prediction
    score = float(_MODEL.predict(img, verbose=0)[0][0])

    # Interpret sigmoid output
    if score >= 0.5:
        label = 'undamaged'
        confidence = score
    else:
        label = 'damaged'
        confidence = 1.0 - score

    # Convert to meaningful % damage
    damage_percent = (1 - score) * 100

    logger.info(f"Prediction → score: {score}, label: {label}")

    return {
        'damage_label': label,
        'damage_confidence': round(confidence, 4),
        'damage_score': round(damage_percent, 2),
    }


def log_damage_result(db: Session, car_id: str, result: dict) -> None:
    """
    Logs prediction result into database
    """
    entry = models.ModelLog(
        model_type='damage',
        input_data={'car_id': car_id},
        output_data=result,
    )

    db.add(entry)
    db.commit()