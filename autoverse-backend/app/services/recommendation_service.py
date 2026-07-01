import joblib, os, logging
import numpy as np
from sqlalchemy.orm import Session
from app import models
logger = logging.getLogger(__name__)
_REC = None

def _load():
    global _REC
    if _REC is None:
        path = os.path.join(os.path.dirname(__file__), '..', 'ml_models', 'recommender.pkl')
        _REC = joblib.load(path)
        logger.info('Recommender loaded.')

def get_recommendations(car_id: str, db: Session, top_n: int = 5) -> list:
    _load()
    ids = _REC['ids']
    matrix = _REC['matrix']

    if car_id not in ids:
        return []

    idx = ids.index(car_id)
    scores = list(enumerate(matrix[idx]))
    scores.sort(key=lambda x: x[1], reverse=True)
    # exclude the car itself (score=1.0)
    top = [ids[i] for i, _ in scores if ids[i] != car_id][:top_n]

    cars = db.query(models.Car).filter(models.Car.id.in_(top)).all()

    # Log the recommendation
    log = models.ModelLog(
        model_type = 'recommendation',
        input_data = {'car_id': car_id},
        output_data = {'recommended_ids': top}, 
    )
    
    db.add(log)
    db.commit()
    return cars