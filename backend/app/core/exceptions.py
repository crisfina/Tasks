from enum import Enum


class ErrorCode(str, Enum):
    USER_NOT_FOUND = "user_not_found"
    USERNAME_OR_EMAIL_EXISTS = (
        "username_or_email_exists"
    )
    INVALID_PASSWORD = "invalid_password"
    INVALID_CURRENT_PASSWORD = (
        "invalid_current_password"
    )
    INVALID_TOKEN = "invalid_token"
    ADMIN_REQUIRED = "admin_required"

    HOUSEHOLD_NOT_FOUND = "household_not_found"
    HOUSEHOLD_MEMBER_NOT_FOUND = (
        "household_member_not_found"
    )
    USER_ALREADY_HOUSEHOLD_MEMBER = (
        "user_already_household_member"
    )
    HOUSEHOLD_OWNER_REQUIRED = (
        "household_owner_required"
    )
    HOUSEHOLD_MANAGER_REQUIRED = (
        "household_manager_required"
    )

    LAST_HOUSEHOLD_OWNER = (
        "last_household_owner"
    )

    HOUSEHOLD_INVITATION_NOT_FOUND = (
        "household_invitation_not_found"
    )

    HOUSEHOLD_INVITATION_EXPIRED = (
        "household_invitation_expired"
    )

    HOUSEHOLD_INVITATION_ALREADY_ACCEPTED = (
        "household_invitation_already_accepted"
    )

    HOUSEHOLD_INVITATION_REVOKED = (
        "household_invitation_revoked"
    )

    CATEGORY_NOT_FOUND = "category_not_found"
    CATEGORY_NAME_EXISTS = "category_name_exists"

    ROOM_NOT_FOUND = "room_not_found"
    ROOM_NAME_EXISTS = "room_name_exists"

    TASK_NOT_FOUND = "task_not_found"
    TASK_ACCESS_DENIED = "task_access_denied"
    TASK_HOUSEHOLD_REQUIRED = (
        "task_household_required"
    )
    TASK_CATEGORY_INVALID = "task_category_invalid"
    TASK_ROOM_INVALID = "task_room_invalid"
    TASK_ASSIGNED_USER_INVALID = (
        "task_assigned_user_invalid"
    )
    TASK_ASSIGNMENT_MODE_INVALID = (
        "task_assignment_mode_invalid"
    )
    TASK_REPEAT_INTERVAL_INVALID = (
        "task_repeat_interval_invalid"
    )
    TASK_VISIBILITY_INVALID = (
        "task_visibility_invalid"
    )

    TASK_OCCURRENCE_NOT_FOUND = (
        "task_occurrence_not_found"
    )
    TASK_OCCURRENCE_ALREADY_COMPLETED = (
        "task_occurrence_already_completed"
    )
    TASK_OCCURRENCE_ALREADY_FAILED = (
        "task_occurrence_already_failed"
    )
    TASK_OCCURRENCE_PENALIZED_USERS_REQUIRED = (
        "task_occurrence_penalized_users_required"
    )
    TASK_OCCURRENCE_NOT_AVAILABLE = (
        "task_occurrence_not_available"
    )
    TASK_OCCURRENCE_USER_INVALID = (
        "task_occurrence_user_invalid"
    )
    TASK_OCCURRENCE_TASK_INACTIVE = (
        "task_occurrence_task_inactive"
    )
    TASK_OCCURRENCE_DATES_INVALID = (
        "task_occurrence_dates_invalid"
    )

    EVENT_NOT_FOUND = "event_not_found"
    EVENT_SCOPE_INVALID = "event_scope_invalid"
    EVENT_HOUSEHOLD_INVALID = (
        "event_household_invalid"
    )
    EVENT_USER_INVALID = "event_user_invalid"

    POINT_TRANSACTION_NOT_FOUND = (
        "point_transaction_not_found"
    )
    POINT_TRANSACTION_SOURCE_INVALID = (
        "point_transaction_source_invalid"
    )
    POINT_TRANSACTION_SCOPE_INVALID = (
        "point_transaction_scope_invalid"
    )
    POINT_TRANSACTION_USER_INVALID = (
        "point_transaction_user_invalid"
    )
    POINT_TRANSACTION_EVENT_INVALID = (
        "point_transaction_event_invalid"
    )
    POINT_TRANSACTION_OCCURRENCE_INVALID = (
        "point_transaction_occurrence_invalid"
    )
    INSUFFICIENT_POINTS = "insufficient_points"

    USER_STATISTICS_NOT_FOUND = (
        "user_statistics_not_found"
    )


class AppError(Exception):
    def __init__(
        self,
        code: ErrorCode,
    ):
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