import logging
import os
from io import StringIO

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security.api_key import APIKeyCookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models.ErrorResponse import ErrorResponse
from models.TissCalModels import (
    TissCalCreateRequest,
    TissCalCreateResponse,
    TissCalDB,
    TissCalDataResponse,
    TissCalListResponse,
    TissCalResponse,
    TissCalSuccessDeleteResponse,
    TissCalUpdateRequest,
    TissCalUpdateResponse,
)
from models.UserModels import UserDB, UserLoginRequest, UserLoginResponse, UserLogoutResponse, UserResponse
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


load_dotenv()
BASE_URL = os.getenv("BASE_URL")
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE")

if BASE_URL is None:
    logger.error("BASE_URL environment variable is not set")
    exit(1)
if MONGO_CONNECTION_STRING is None:
    logger.error("MONGO_CONNECTION_STRING environment variable is not set")
    exit(1)
if REDIS_HOST is None:
    logger.error("REDIS_HOST environment variable is not set")
    exit(1)
if REDIS_PASSWORD in ("", "None"):
    REDIS_PASSWORD = None

if DEVELOPMENT_MODE in ("", "None", "False", "false"):
    DEVELOPMENT_MODE = False
else:
    DEVELOPMENT_MODE = True



app = FastAPI(root_path=BASE_URL, title="TissCal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_handler = UserHandler(
    logger=logger,
    connection_string=MONGO_CONNECTION_STRING,
    db_name="tisscal",
    user_collection="users",
    redis_host=REDIS_HOST,
    redis_port=REDIS_PORT,
    redis_password=REDIS_PASSWORD,
)
tiss_cal_handler = TissCalHandler(
    logger=logger,
    connection_string=MONGO_CONNECTION_STRING,
    db_name="tisscal",
    tiss_cal_collection="calendars",
    user_handler=user_handler,
)

api_key_cookie = APIKeyCookie(name="token", auto_error=False)

templates = Jinja2Templates(directory="../frontend/dist")


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
@app.get("/api/me", response_model=UserResponse, status_code=200)
async def user_data_me(current_user: UserDB = Depends(verify_token)):
    return current_user


@app.post("/api/login", response_model=UserLoginResponse)
async def login(request: UserLoginRequest, response: Response):
    if not (token := user_handler.login(request.username, request.password)):
        raise MyHTTPException(status_code=404, detail="User name or password incorrect")

    response.set_cookie(key="token", value=token, max_age=60 * 60, httponly=True, samesite="none", secure=True)
    return {
        "username": request.username,
    }


@app.get("/api/logout", response_model=UserLogoutResponse, status_code=200)
async def logout(response: Response, current_user: UserDB = Depends(verify_token)):
    user_handler.logout(str(current_user.uid))
    response.delete_cookie(key="token")
    return {}


@app.post("/api/cal/create", response_model=TissCalCreateResponse, status_code=200)
async def create_cal(request: TissCalCreateRequest, current_user: UserDB = Depends(verify_token)):
    cal = tiss_cal_handler.create_new_calendar(url=request.url, name=request.name, owner=str(current_user.uid))
    if cal is None:
        raise MyHTTPException(status_code=400, detail="Can't create calendar :I")
    return TissCalCreateResponse(**cal.dict())


@app.get("/api/cal/list", response_model=TissCalListResponse, status_code=200)
async def get_calendars(current_user: UserDB = Depends(verify_token)):
    cals = tiss_cal_handler.get_calendars_by_owner(str(current_user.uid))
    if cals is None:
        raise MyHTTPException(status_code=404, detail="No calendars found / Something went wrong :I")
    return TissCalListResponse(calendars=[TissCalResponse(**cal.dict()) for cal in cals])


@app.get("/api/cal/delete/{token}", response_model=TissCalSuccessDeleteResponse, status_code=200)
async def delete_calender(token: str, current_user: UserDB = Depends(verify_token)):
    # TODO: Check if user is owner
    res = tiss_cal_handler.delete_calendar_by_token(token)
    return {}


@app.get("/api/cal/data/{token}", response_model=TissCalDataResponse, status_code=200)
async def get_calendar_data(token: str, current_user: UserDB = Depends(verify_token)):
    res = tiss_cal_handler.get_calendar_by_token(token)
    if res is None:
        raise MyHTTPException(status_code=404, detail="There is no calendar with this token :I")
    return TissCalDataResponse(**res.dict())


@app.post("/api/cal/data", response_model=TissCalUpdateResponse, status_code=200)
async def update_calender_data(request: TissCalUpdateRequest, current_user: UserDB = Depends(verify_token)):
    # TODO: Check if user is owner
    # TODO: Handle token change (or deny it at all) -> for now token changes are just ignored (not changed at all)
    # TODO: Check if given templates are valid (contain only valid placeholders)
    old_cal = tiss_cal_handler.get_calendar_by_token(request.token)
    if old_cal is None:
        raise MyHTTPException(status_code=404, detail="There is no calendar with this token :I")
    res = tiss_cal_handler.update_calendar(TissCalDB(**{**old_cal.dict(), **request.dict(exclude={"token"})}))
    return TissCalUpdateResponse(**res.dict())


@app.get("/api/cal/{token}", status_code=200)
async def get_calender_by_token(token: str, response: Response):
    cal = tiss_cal_handler.prettify_calendar(token)
    if cal is None:
        raise MyHTTPException(status_code=404, detail="Something went wrong (aka. no calendar for you) :I")

    new_cal_stream = StringIO(cal)
    return StreamingResponse(iter([new_cal_stream.getvalue()]), media_type="text/calendar")


if not DEVELOPMENT_MODE:
    app.mount("/assets", StaticFiles(directory="../frontend/dist/assets", html=True, check_dir=True), name="frontend-assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(request: Request, full_path: str):
        logger.info(f"frontend: serving frontend for path={full_path}")
        return templates.TemplateResponse("index.html", {"request": request})
