from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app import schemas
from app.services.recommendation_service import get_recommendations
router = APIRouter(prefix='/recommendations', tags=['Recommendations'])
@router.get('/{car_id}', response_model=list[schemas.CarRead])

def recommend(car_id: UUID, db: Session = Depends(get_db)):
    '''Return top 5 similar cars for the given car_id.'''
    results = get_recommendations(str(car_id), db)
    
    if results is None:
        raise HTTPException(503, 'Recommender model not available.')
    if not results:
        raise HTTPException(404, 'Car not in recommender index. Rebuild recommender.')
    return results