from fastapi import FastAPI, HTTPException
from tortoise.models import Model
from tortoise import fields, Tortoise, run_async

app = FastAPI()

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50)

class Photo(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=100)
    url = fields.CharField(max_length=200)

async def init():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['__main__']},
    )
    await Tortoise.generate_schemas()

@app.post("/users/", response_model=User)
async def create_user(username: str):
    user = await User.create(username=username)
    return user

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    user = await User.filter(id=user_id).first().prefetch_related('photos')
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, username: str):
    user = await User.filter(id=user_id).update(username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    deleted_count = await User.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@app.post("/photos/", response_model=Photo)
async def create_photo(title: str, url: str):
    photo = await Photo.create(title=title, url=url)
    return photo

@app.get("/photos/{photo_id}", response_model=Photo)
async def read_photo(photo_id: int):
    photo = await Photo.filter(id=photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo

@app.put("/photos/{photo_id}", response_model=Photo)
async def update_photo(photo_id: int, title: str, url: str):
    photo = await Photo.filter(id=photo_id).update(title=title, url=url)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo

@app.delete("/photos/{photo_id}")
async def delete_photo(photo_id: int):
    deleted_count = await Photo.filter(id=photo_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail="Photo not found")
    return {"message": "Photo deleted successfully"}


if __name__ == "__main__":
    run_async(init())
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
