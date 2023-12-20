from fastapi import Request, HTTPException, status, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.services.auth import service_auth
from src.database.models import BlacklistedToken, User
from src.database.db import get_db

security = HTTPBearer()

class BannedDependency:
    def __init__(self):
        pass

    async def __call__(self, request: Request,
                       current_user: User = Depends(service_auth.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security),
                       db: Session = Depends(get_db)):

        banned_satauts = current_user.banned
        
        if banned_satauts:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {current_user.email} banned. Please contact your administrator!"
            )

banned_dependency = BannedDependency()
