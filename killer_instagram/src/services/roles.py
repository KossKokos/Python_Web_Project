from typing import List

from fastapi import Depends, HTTPException, status, Request

from src.database.models import User
from src.services.auth import service_auth

class RoleRights:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request,
                       current_user: User = Depends(service_auth.get_current_user)):
        print(14, request.method, request.url)
        print(15, f"user role: {current_user.role}")
        print(16,f"Allowed roles: {self.allowed_roles}")
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation forbidden for {current_user.role}"
            )
