import logging
from io import StringIO

from fastapi import Depends, FastAPI, HTTPException, Request, Response, Security
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security.api_key import APIKeyCookie

from models.ErrorResponse import ErrorResponse
from models.TissCalModels import TissCalChangeRequest, TissCalCreateRequest, TissCalDB, TissCalResponse, TissCalSuccessDelete
from models.UserModels import UserDB, UserLoginRequest, UserLogoutResponse, UserResponse
from MyCalendar import MyCalendar
from MyHTTPException import MyHTTPException
from TissCalHandler import TissCalHandler
from UserHandler import UserHandler

# Setup Logging ####
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
    logger=logger,
    connection_string="mongodb://admin:adminadmin@10.0.0.150:8882/",
    db_name="tisscal",
    user_collection="users",
    redis_host="10.0.0.150",
    redis_port=8881,
    redis_password=None,
)
tiss_cal_handler = TissCalHandler(
    logger=logger,
    connection_string="mongodb://admin:adminadmin@10.0.0.150:8882/",
    db_name="tisscal",
    tiss_cal_collection="calendars",
    user_handler=user_handler,
)

api_key_cookie = APIKeyCookie(name="token", auto_error=False)


# Exception handlers ####
@app.exception_handler(MyHTTPException)
def my_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=ErrorResponse(message=exc.detail).dict())


# Authentication ####
def verify_token(token: str = Security(api_key_cookie)) -> UserDB | None:
    if not user_handler.check_login(token=token):
        raise MyHTTPException(status_code=401, detail="Request not authenticated")
    uid = user_handler.get_session(token=token)[1]
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
@app.get("/tisscal/api/me", response_model=UserResponse, status_code=200)
async def user_data_me(current_user: UserDB = Depends(verify_token)):
    return current_user


@app.post("/tisscal/api/login", response_model=UserResponse)
async def login(user: UserLoginRequest, response: Response):
    if not user_handler.get_user_by_username(user.username):
        raise MyHTTPException(status_code=404, detail="User name or password incorrect")

    if not (token := user_handler.login(user.username, user.password)):
        raise MyHTTPException(status_code=404, detail="User name or password incorrect")

    response.set_cookie(key="token", value=token, max_age=60 * 60)
    return {
        "username": user.username,
    }


@app.get("/tisscal/api/logout", response_model=UserLogoutResponse, status_code=200)
async def logout(response: Response, current_user: UserDB = Depends(verify_token)):
    user_handler.logout(str(current_user.uid))
    response.delete_cookie(key="token")
    return {}


@app.post("/tisscal/api/cal/create", response_model=TissCalResponse, status_code=200)
async def create_cal(request: TissCalCreateRequest, current_user: UserDB = Depends(verify_token)):
    cal = tiss_cal_handler.create_new_calendar(url=request.url, name=request.name, owner=str(current_user.uid))
    if cal is None:
        raise MyHTTPException(status_code=500, detail="Error creating calendar")
    return TissCalResponse(**cal.dict())


@app.post("/tisscal/api/cal/change", status_code=200)
async def get_calender(new_cal: TissCalChangeRequest, current_user: UserDB = Depends(verify_token)):
    old_cal = tiss_cal_handler.get_calendar_by_token(new_cal.token)
    if old_cal is None:
        raise MyHTTPException(status_code=404, detail="You need to create a calendar before you can change it :I")

    res = tiss_cal_handler.update_calendar(TissCalDB(**new_cal.dict(), id=old_cal.id, owner=old_cal.owner, token=old_cal.token))
    if res is None:
        raise MyHTTPException(status_code=500, detail="Something went wrong, calendar was not updated :I")

    return TissCalResponse(**res.dict())
    

@app.get("/tisscal/api/cal/data/{token}", status_code=200)
async def get_calender(token: str, current_user: UserDB = Depends(verify_token)):
    cal = tiss_cal_handler.get_calendar_by_token(token)
    if cal is None:
        raise MyHTTPException(status_code=404, detail="Something went wrong (aka. no calendar for you) :I")

    return TissCalResponse(**cal.dict())


@app.get("/tisscal/api/cal/delete/{token}", response_model=TissCalSuccessDelete, status_code=200)
async def get_calender(token: str, current_user: UserDB = Depends(verify_token)):
    res = tiss_cal_handler.delete_calendar_by_token(token)
    return {}


@app.post("/tisscal/api/cal/change", status_code=200)
async def get_calender(new_cal: TissCalChangeRequest, current_user: UserDB = Depends(verify_token)):
    old_cal = tiss_cal_handler.get_calendar_by_token(new_cal.token)
    if old_cal is None:
        raise MyHTTPException(status_code=404, detail="You need to create a calendar before you can change it :I")

    res = tiss_cal_handler.update_calendar(TissCalDB(**new_cal.dict(), id=old_cal.id, owner=old_cal.owner, token=old_cal.token))
    if res is None:
        raise MyHTTPException(status_code=500, detail="Something went wrong, calendar was not updated :I")

    return TissCalResponse(**res.dict())


@app.get("/tisscal/api/cal/{token}", status_code=200)
async def get_calender(token: str, response: Response):
    cal = tiss_cal_handler.prettify_calendar(token)
    if cal is None:
        raise MyHTTPException(status_code=404, detail="Something went wrong (aka. no calendar for you) :I")

    new_cal_stream = StringIO(cal)
    return StreamingResponse(iter([new_cal_stream.getvalue()]), media_type="text/calendar")


@app.get("/tisscal/calstring/{token}", status_code=200)
async def get_calender(token: str, response: Response):
    cal = tiss_cal_handler.prettify_calendar(token)
    if cal is None:
        raise MyHTTPException(status_code=404, detail="Something went wrong (aka. no calendar for you) :I")

    return cal


# https://andrea-emily-celebration-emacs.trycloudflare.com/tisscal/cal/asdasdasdasdasdasd
