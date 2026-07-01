from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/register', response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check email uniqueness
        if db.query(models.User).filter(models.User.email == payload.email).first():
            raise HTTPException(status_code=400, detail='Email already registered.')

        user = models.User(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=payload.role,    
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except Exception as exc:
        db.rollback()                       # important: don't leave transaction open
        import traceback
        print("REGISTER ERROR:", str(exc))  # ← shows in uvicorn terminal
        print(traceback.format_exc())       # ← full stack trace
        raise HTTPException(
            status_code=500,
            detail=f"Internal error during registration: {str(exc)}"
        )

@router.post('/login', response_model=schemas.Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    '''
    OAuth2 form: send username (email) + password as form-data.
    Returns JWT access token.
    '''
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password.',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail='Account is deactivated.')

    token = create_access_token({'sub': str(user.id), 'role': user.role.value})

    return {'access_token': token, 'token_type': 'bearer'}