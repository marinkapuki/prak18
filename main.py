from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time

app = FastAPI()

class ErrorResponseModel(BaseModel):
    status_code: int
    message: str
    error_code: str

class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id

class InvalidUserDataException(Exception):
    def __init__(self, message: str):
        self.message = message

class User(BaseModel):
    id: int
    name: str

users_db = {
    1: {"id": 1, "name": "Alice"},
    2: {"id": 2, "name": "Bob"}
}

@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    start_time = time.time()
    response = {"status_code": 404, "message": f"User with ID {exc.user_id} not found", "error_code": "USER_NOT_FOUND"}
    process_time = time.time() - start_time
    return JSONResponse(content=response, status_code=404, headers={"X-ErrorHandleTime": str(process_time)})

@app.exception_handler(InvalidUserDataException)
async def invalid_user_data_handler(request: Request, exc: InvalidUserDataException):
    start_time = time.time()
    response = {"status_code": 400, "message": exc.message, "error_code": "INVALID_USER_DATA"}
    process_time = time.time() - start_time
    return JSONResponse(content=response, status_code=400, headers={"X-ErrorHandleTime": str(process_time)})

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    if user_id not in users_db:
        raise UserNotFoundException(user_id)
    return users_db[user_id]

@app.post("/users/", response_model=User)
async def create_user(user: User):
    if user.id in users_db:
        raise InvalidUserDataException("User with this ID already exists")
    users_db[user.id] = user.model_dump()
    return user