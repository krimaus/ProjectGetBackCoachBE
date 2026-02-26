from .practice import practice_router
from .team import teams_router
from .attendance import attendance_router
from . import user

__all__ = [
    "practice_router",
    "teams_router",
    "attendance_router",
    "user",
]