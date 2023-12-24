from fastapi import Request, HTTPException, status, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..services.auth import service_auth
from ..database.models import BlacklistedToken, User
from ..database.db import get_db

security = HTTPBearer()

class LogoutDependency:
    def __init__(self):
        pass

    async def __call__(self, request: Request,
                       current_user: User = Depends(service_auth.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security),
                       db: Session = Depends(get_db)):
        """
        The __call__ function is the main function of this class. It takes in a request,
        current_user, credentials and db as arguments. The current_user argument is passed
        in by the Depends decorator which calls get_current_user from service auth to 
        get the user object for that particular request. The credentials argument is passed in 
        by Security(security) which gets it from security defined above (the JWT token). Finally, 
        db is passed in by Depends(get_db) which calls get_db to create a database session.

        :param self: Represent the instance of a class
        :param request: Request: Get the request object
        :param current_user: User: Get the current user object from the database
        :param credentials: HTTPAuthorizationCredentials: Get the access token from the request header
        :param db: Session: Access the database
        :return: A response object
        """

        user_id = current_user.id
        token = db.query(BlacklistedToken).filter(BlacklistedToken.user_id == user_id).first()
        access_token = credentials.credentials
        
        if token and token.blacklisted_token == access_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation forbidden for {current_user.email}. Please login again!"
            )

logout_dependency = LogoutDependency()
