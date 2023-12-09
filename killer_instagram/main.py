import redis.asyncio as redis
import uvicorn

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from routes import users, photos, other_router

from src.routes import auth, users
from src.middlewares.middlewares import (
    startup_event, 
    ban_ips_middleware, 
    limit_access_by_ip,
    user_agent_ban_middleware
)

app = FastAPI()

# # create route so i don't need to add contacts/... everytime to my routes functions
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(photos.router, prefix='/api')
app.include_router(other_router.router, prefix='/api')

# app.add_event_handler("startup", startup_event)

# app.middleware("http")(ban_ips_middleware)
# app.middleware("http")(limit_access_by_ip)
# app.middleware("http")(user_agent_ban_middleware)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get("/")
async def read_root():
    """
    The read_root function returns a JSON object with the message: Hello World.
    
    :return: A dict
    """
    return {"message": "Hello World!"}

# start server, main:app - name of the file and app - Fastapi, reload=True - for authomatical reload
if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)