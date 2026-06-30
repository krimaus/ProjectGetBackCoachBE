from .practice import practice_router
from .team import teams_router
from .attendance import attendance_router
from .user import users_router
from .auth import auth_router

__all__ = [
    "practice_router",
    "teams_router",
    "attendance_router",
    "users_router",
    "auth_router",
]