from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
    ConflictError,
    NotFoundError,
)


def _get_status_code(
    error: AppError,
) -> int:
    if isinstance(error, NotFoundError):
        return status.HTTP_404_NOT_FOUND

    if isinstance(error, ConflictError):
        return status.HTTP_409_CONFLICT

    if isinstance(error, AuthenticationError):
        return status.HTTP_401_UNAUTHORIZED

    if isinstance(error, AuthorizationError):
        return status.HTTP_403_FORBIDDEN

    if isinstance(error, BusinessRuleError):
        return status.HTTP_400_BAD_REQUEST

    return status.HTTP_500_INTERNAL_SERVER_ERROR


async def app_error_handler(
    request: Request,
    error: AppError,
) -> JSONResponse:
    return JSONResponse(
        status_code=_get_status_code(error),
        content={
            "code": error.code.value,
        },
    )