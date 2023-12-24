from typing import List

from fastapi import Depends, HTTPException, status, Request

from ..database.models import User
from ..services.auth import service_auth

class RoleRights:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request,
                       current_user: User = Depends(service_auth.get_current_user)):
        """
        The __call__ function is a decorator that checks if the current user has one of the allowed roles.
        If not, it raises an HTTPException with status code 403 and a detail message.

        :param self: Represent the instance of the class
        :param request: Request: Get the request object
        :param current_user: User: Get the current user from the database
        :return: A response object
        """

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation forbidden for {current_user.role}"
            )
