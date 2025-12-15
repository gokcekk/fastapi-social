# app/core/exceptions.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base business exception."""
    status_code: int = 400
    message: str = "An error occurred."

    def __init__(self, message: str | None = None):
        if message:
            self.message = message


class NotFoundError(AppError):
    status_code = 404


class ForbiddenError(AppError):
    status_code = 403


class BadRequestError(AppError):
    status_code = 400


class ConflictError(AppError):
    status_code = 409


def register_exception_handlers(app: FastAPI) -> None:
    """
    Global handler for AppError.
    Keeps FastAPI style response: {"detail": "..."}
    """

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )
