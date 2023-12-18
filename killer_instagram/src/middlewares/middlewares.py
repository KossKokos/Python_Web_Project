# from ipaddress import ip_address
# from typing import Callable

# from fastapi import Request, HTTPException, status, Depends
# from fastapi.responses import JSONResponse
# from fastapi_limiter import FastAPILimiter

# import redis.asyncio as redis

# from src.conf.config import settings

# from fastapi.security import OAuth2PasswordBearer
# from typing import Optional
# from jose import JWTError, jwt
# from database import SessionLocal
# from routes.users import User

# """
# Тут просто приклади, можете їх міняти як заманеться
# """

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# allowed_ips = []
# banned_ips = []
# user_agent_ban_list = []


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# async def get_current_user_role(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=401,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception

#     user = db.query(User).filter(User.username == username).first()
#     if user is None:
#         raise credentials_exception

#     return user.role


# async def check_admin_or_moderator(current_user_role: str = Depends(get_current_user_role)):
#     if current_user_role not in ["admin", "moderator"]:
#         raise HTTPException(status_code=403, detail="Permission denied. Admin or moderator role required")


# async def startup_event():
#     r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, encoding="utf-8",
#                           decode_responses=True)
#     await FastAPILimiter.init(r)


# async def ban_ips_middleware(request: Request, call_next: Callable):
#     ip = ip_address(request.client.host)
#     if ip in banned_ips:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are banned")
#     response = await call_next(request)
#     return response


# async def limit_access_by_ip(request: Request, call_next: Callable):
#     ip = ip_address(request.client.host)
#     if ip not in allowed_ips:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
#     response = await call_next(request)
#     return response


# async def user_agent_ban_middleware(request: Request, call_next: Callable):
#     user_agent = request.headers.get("user-agent")