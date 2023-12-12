"""
Тут будуть тільки шляхи: router = APIRouter(prefix='/pictures', tags=['pictures'])

"""
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from fastapi.security import HTTPBearer

from fastapi import APIRouter
from src.services.auth import service_auth
from src.database.models import User
from src.services.roles import RoleRights

router = APIRouter(prefix='/roles_test', tags=['proles_test'])
security = HTTPBearer()

allowd_operation_get = RoleRights(["user", "moderator"])
# allowd_operation_create = RoleRights(["user","moderator", "admin"])
# allowd_operation_update = RoleRights(["admin"])
# allowd_operation_remove = RoleRights(["admin"])


#test
@router.get("/", status_code=status.HTTP_200_OK,
                dependencies=[Depends(allowd_operation_get)],
                description = "Only moderators and admin")
async def read_root(current_user: User = Depends(service_auth.get_current_user)):

    """
    The read_root function returns a JSON object with the message: Hello World.
    
    :return: A dict
    """
    return {"message": f"Hello {current_user.username}!"}

