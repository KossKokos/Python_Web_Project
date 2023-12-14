from fastapi import Request, HTTPException, status, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.services.auth import service_auth
from src.database.models import BlacklistedToken, User
from src.database.db import get_db

security = HTTPBearer()

class LogoutDependency:
    def __init__(self):
        pass

    async def __call__(self, request: Request,
                       current_user: User = Depends(service_auth.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security),
                       db: Session = Depends(get_db)):

        user_id = current_user.id
        token = db.query(BlacklistedToken).filter(BlacklistedToken.user_id == user_id).first()
        access_token = credentials.credentials
        
        if token and token.blacklisted_token == access_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation forbidden for {current_user.email}. Please login again!"
            )

logout_dependency = LogoutDependency()
