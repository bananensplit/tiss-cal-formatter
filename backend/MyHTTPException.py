from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class MyHTTPException(HTTPException):
    pass

