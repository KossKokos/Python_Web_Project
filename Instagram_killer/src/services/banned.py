from fastapi import Request, HTTPException, status, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.services.auth import service_auth
from src.database.models import User
from src.database.db import get_db

security = HTTPBearer()

class BannedDependency:
    def __init__(self):
        pass

    async def __call__(self, request: Request,
                       current_user: User = Depends(service_auth.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security),
                       db: Session = Depends(get_db)):
        """
        The __call__ function is the main function of a BannedDependency class.
        It receives the request and returns a response.


        :param self: Represent the instance of the class
        :param request: Request: Get the request data from the client
        :param current_user: User: Get the current user from the database
        :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
        :param db: Session: Access the database
        :return: HTTPException if user are banned. otherwise nothing
        """

        banned_satauts = current_user.banned
        
        if banned_satauts:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {current_user.email} banned. Please contact your administrator!"
            )

banned_dependency = BannedDependency()
