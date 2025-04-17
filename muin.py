from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, constr
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Optional
import time

app = FastAPI()

# Модель данных пользователя
class User(BaseModel):
    username: str
    email: EmailStr
    password: constr(min_length=8, max_length=16) # type: ignore

# Модель ответа на ошибку
class ErrorResponseModel(BaseModel):
    status_code: int
    message: str
    error_code: Optional[str] = None

# Пользовательское исключение для несуществующего пользователя
class UserNotFoundException(Exception):
    def __init__(self, username: str):
        self.username = username

# Пользовательское исключение для недействительных данных пользователя
class InvalidUserDataException(Exception):
    def __init__(self, message: str):
        self.message = message

# Запоминаем пользователей в простом словаре
users_db = {}

@app.post("/register/", response_model=User)
def register_user(user: User):
    if user.username in users_db:
        raise InvalidUserDataException("User with this username already exists.")
    users_db[user.username] = user
    return user

@app.get("/users/{username}", response_model=User)
def get_user(username: str):
    if username not in users_db:
        raise UserNotFoundException(username)
    return users_db[username]

# Обработчик неожиданного исключения
@app.exception_handler(InvalidUserDataException)
async def invalid_user_data_exception_handler(request, exc: InvalidUserDataException):
    processing_time = datetime.utcnow()  # Получаем текущее время
    response = ErrorResponseModel(
        status_code=400,
        message=exc.message,
        error_code="INVALID_USER_DATA"
    )
    return JSONResponse(
        status_code=400,
        content=response.dict(),
        headers={"X-ErrorHandleTime": str(processing_time)}
    )

@app.exception_handler(UserNotFoundException)
async def user_not_found_exception_handler(request, exc: UserNotFoundException):
    processing_time = datetime.utcnow()  # Получаем текущее время
    response = ErrorResponseModel(
        status_code=404,
        message=f"User '{exc.username}' not found.",
        error_code="USER_NOT_FOUND"
    )
    return JSONResponse(
        status_code=404,
        content=response.dict(),
        headers={"X-ErrorHandleTime": str(processing_time)}
    )

# Обработчик ошибок HTTPException по умолчанию
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    response = ErrorResponseModel(
        status_code=exc.status_code,
        message=exc.detail
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict(),
    )

