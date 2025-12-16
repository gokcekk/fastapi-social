# app/core/exceptions.py

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base business exception."""
    status_code: int = status.HTTP_404_NOT_FOUND
    message: str = "An error occurred."

    def __init__(self, message: str | None = None):
        if message:
            self.message = message


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND


class ForbiddenError(AppError):
    status_code = status.HTTP_403_FORBIDDEN


class BadRequestError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT


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
