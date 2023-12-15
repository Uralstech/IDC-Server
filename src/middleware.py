# IDC AI Server
# Copyright 2023 URAV ADVANCED LEARNING SYSTEMS PRIVATE LIMITED
# 
# This product includes software developed at
# URAV ADVANCED LEARNING SYSTEMS PRIVATE LIMITED (https://uralstech.in/)
# by Udayshankar Ravikumar.

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from fastapi.responses import JSONResponse
from fastapi import Request, Response

from typing import Any, Coroutine
from enum import Enum

from firebase_admin.auth import verify_id_token

class UMiddleware(BaseHTTPMiddleware):
    class DispatchErrorClass(Enum):
        NO_HEADER = -1
        INVALID_HEADER = -2
        AUTH = -3

    def __init__(self, app: ASGIApp, firebase_app: Any) -> None:
        super().__init__(app)
        self._firebase_app: Any = firebase_app

    def create_error_response(self, class_: DispatchErrorClass, message: str) -> JSONResponse:
        code: int
        if class_ == UMiddleware.DispatchErrorClass.NO_HEADER:
            code = 401
        elif class_ == UMiddleware.DispatchErrorClass.INVALID_HEADER:
            code = 401
        elif class_ == UMiddleware.DispatchErrorClass.AUTH:
            code = 403
        else:
            code = 418

        return JSONResponse({"error":{"code":code, "class":class_.name, "message":message}}, code, media_type="application/json")

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Coroutine[Any, Any, Response]:
        print(f"Authenticating...")

        header: str | None = request.headers.get("Authorization", None)
        if header:
            split_header: list[str] = header.split(" ")

            if len(split_header) != 2:
                print("Authentication unsuccessful: Header is invalid.")
                return self.create_error_response(UMiddleware.DispatchErrorClass.INVALID_HEADER, "Authorization header is invalid.")
            token: str = split_header[1]

            try:
                verify_id_token(token, self._firebase_app, True)
            except Exception as error:
                print(f"Authentication unsuccessful: {error}")
                return self.create_error_response(UMiddleware.DispatchErrorClass.AUTH, str(error))
        else:
            print("Authentication unsuccessful: Header is None.")
            return self.create_error_response(UMiddleware.DispatchErrorClass.INVALID_HEADER, "Authorization header is None.")

        print("Authentication successful!")
        return await call_next(request)