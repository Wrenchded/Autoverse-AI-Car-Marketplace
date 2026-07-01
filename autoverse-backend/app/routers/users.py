from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix='/users', tags=['Users'])

@router.get('/me', response_model=schemas.UserRead)

def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.patch('/me', response_model=schemas.UserRead)
def update_me(
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    
    if payload.name is not None:
        current_user.name = payload.name
    db.commit() 
    db.refresh(current_user)
    return current_user

# Admin-only endpoints
@router.get('/', response_model=list[schemas.UserRead], dependencies=[Depends(require_admin)])

def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.patch('/{user_id}/status', response_model=schemas.UserRead, dependencies=[Depends(require_admin)])

def toggle_status(
    user_id: UUID,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
):
    
    user = db.query(models.User).filter(models.User.id == user_id).first()  
    if not user:
        raise HTTPException(404, 'User not found.')
    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)
    return user