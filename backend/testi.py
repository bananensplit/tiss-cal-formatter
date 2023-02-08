import logging

from fastapi import Depends, FastAPI, HTTPException, Request, Response, Security
from fastapi.security.api_key import APIKeyCookie
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models import ErrorResponse, UserLoginRequest, UserResponse
from MyHTTPException import MyHTTPException
from UserHandler import User, UserAlreadyExistsError, UserDoesNotExistError, UserHandler

logger = logging.getLogger("TissCal-API")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
fh = logging.FileHandler("fastapi.log")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)


app = FastAPI()
user_handler = UserHandler(
    "mongodb://admin:adminadmin@10.0.0.150:8882/",
    "tisscal",
    "users",
    "10.0.0.150",
    8881,
    None,
    logger=logger,
)
api_key_cookie = APIKeyCookie(name="token", auto_error=True)


# Exception handlers ####
@app.exception_handler(MyHTTPException)
def my_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=ErrorResponse(message=exc.detail).dict())


# Authentication ####
def verify_token(token: str = Security(api_key_cookie)):
    if not user_handler.is_logged_in(token=token):
        raise MyHTTPException(status_code=401, detail="Request not authenticated")
    uid = user_handler.get_login_session(token=token)[1]
    return user_handler.get_user_by_uid(uid)


# Events ####
@app.on_event("startup")
async def startup_event():
    logger.warning("Starting up")


@app.on_event("shutdown")
async def shutdown_event():
    user_handler.close()
    logger.warning("Shuted down")


# Endpoints ####
@app.get("/tisscal/user/me", response_model=UserResponse, status_code=200)
async def user_data_me(current_user: User = Depends(verify_token)):
    return current_user


@app.get("/tisscal/{token}", status_code=200)
async def get_calender(token: str, response: Response):
    pass


@app.post("/tisscal/login", response_model=UserResponse, status_code=200)
async def login(user: UserLoginRequest, response: Response):
    token = user_handler.login(user.username, user.password)
    response.set_cookie(key="token", value=token, max_age=60 * 60)
    return {
        "username": user.username,
    }


@app.get("/tisscal/logout", status_code=200)
async def logout(response: Response, current_user: User = Depends(verify_token)):
    user_handler.logout(current_user.uid)
    response.delete_cookie(key="token")
    return {}
