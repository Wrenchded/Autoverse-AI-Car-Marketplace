from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import decode_access_token
from app import models

# This tells FastAPI where the login endpoint is (for Swagger UI 'Authorize' button)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def get_current_user(
token: str = Depends(oauth2_scheme),
db: Session = Depends(get_db),
) -> models.User:
    '''
    Extracts and validates the JWT from the Authorization header.
    Returns the User ORM object if valid.
    Raises 401 if token is missing, invalid, or expired.
    '''
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials.',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get('sub')
        if not user_id: 
            raise exc
    except JWTError:
        raise exc

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.is_active:
        raise exc
    return user

def require_role(*roles: str):
    '''
    Factory function. Returns a FastAPI dependency that enforces role.
    Usage: Depends(require_role('seller', 'admin'))
    '''

    def checker(
        current_user: models.User = Depends(get_current_user)
    ) -> models.User:
        if current_user.role.value not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access restricted to: {', '.join(roles)}.",
            )
        return current_user
    return checker

# Convenience aliases — use these in your routers
require_buyer = require_role('buyer', 'admin')
require_seller = require_role('seller', 'admin')
require_admin = require_role('admin')