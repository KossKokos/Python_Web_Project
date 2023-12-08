from ipaddress import ip_address
from typing import Callable

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis

from src.conf.config import settings


allowed_ips = []
banned_ips = []
user_agent_ban_list = []


async def startup_event():
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


async def ban_ips_middleware(request: Request, call_next: Callable):
    ip = ip_address(request.client.host)
    if ip in banned_ips:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are banned")
    response = await call_next(request)
    return response


async def limit_access_by_ip(request: Request, call_next: Callable):
    ip = ip_address(request.client.host)
    if ip not in allowed_ips:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
    response = await call_next(request)
    return response


async def user_agent_ban_middleware(request: Request, call_next: Callable):
    user_agent = request.headers.get("user-agent")