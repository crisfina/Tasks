from enum import Enum


class ErrorCode(str, Enum):
    USER_NOT_FOUND = "user_not_found"
    USERNAME_OR_EMAIL_EXISTS = "username_or_email_exists"
    INVALID_PASSWORD = "invalid_password"
    INVALID_CURRENT_PASSWORD = "invalid_current_password"

    HOUSEHOLD_NOT_FOUND = "household_not_found"
    HOUSEHOLD_MEMBER_NOT_FOUND = "household_member_not_found"
    USER_ALREADY_HOUSEHOLD_MEMBER = (
        "user_already_household_member"
    )
    HOUSEHOLD_ADMIN_REQUIRED = "household_admin_required"
    LAST_HOUSEHOLD_ADMIN = "last_household_admin"


class AppError(Exception):
    def __init__(self, code: ErrorCode):
        self.code = code
        super().__init__(code.value)


class NotFoundError(AppError):
    pass


class ConflictError(AppError):
    pass


class AuthenticationError(AppError):
    pass


class AuthorizationError(AppError):
    pass


class BusinessRuleError(AppError):
    pass