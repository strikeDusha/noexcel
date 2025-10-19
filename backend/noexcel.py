import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr, validator
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
app = FastAPI()
#TODO -  добавить правильную базу данных  MongoDB, для сохранения логинов и паролей пользователей
MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.users_db
users_collection = db.get_collection("users")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#Задал ограничения по длине и набору символов


class UserIn(BaseModel):
    username: constr(min_length=3, max_length=30)
    password: constr(min_length=8)
    @validator("password")
    def password_complexity(cls, v):
        if v.isdigit() or v.isalpha():
            raise ValueError("Пароль должен содержать и буквы, и цифры")
        return v
    @validator("username")
    def username_complexity(cls, v):
        if not(v.isalnum()):
            raise ValueError("Логин не может содержать спецсимволы и пробелы")
        return v
class UserOut(BaseModel):
    username: str
def users_password(pasword: str) -> str:
    return pwd_context.hash(pasword)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
async def get_user(username: str):
    return await users_collection.find_one({"username": username})


@app.post("/register", response_model=UserOut, tags=["Создание пользователя"])
async def register(user: UserIn):
    existing_user = await get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    hashed_password = users_password(user.password)
    user_doc = {"username": user.username, "password": hashed_password}
    await users_collection.insert_one(user_doc)
    return {"username": user.username}


@app.post("/login", tags=[" Вход в систему"])
async def login(user: UserIn):
    existing_user = await get_user(user.username)
    if not existing_user:
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    if not verify_password(user.password, existing_user["password"]):
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    return {"message": f"Пользователь {user.username} успешно вошёл в систему"}


if __name__ == "__main__":
    uvicorn.run("noexcel:app", reload=True)