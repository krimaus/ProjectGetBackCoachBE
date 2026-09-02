import uuid
from datetime import datetime, timezone

import pytest

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.practice import Practice
from app.db_layer.orm_models.attendance import AttendanceEntry
from app.db_layer.orm_models.user import User
from app.service_layer.services.attendance.service import get_attendance_grid
from src.app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from src.app.db_layer.orm_models.user_role import UserRole


@pytest.mark.asyncio
async def test_get_attendance_grid(async_session):
    team1 = Team(id=uuid.uuid4(), name="Alpha")
    team2 = Team(id=uuid.uuid4(), name="Beta")

    async_session.add_all([team1, team2])
    await async_session.flush()
    
    user1 = User(id=uuid.uuid4(), first_name="Adam", last_name="Kowalski", username="ADAKOW", hashed_password="some_hash")
    user2 = User(id=uuid.uuid4(), first_name="Jan", last_name="Lewandowski", username="JANLEW", hashed_password="some_hash")
    user3 = User(id=uuid.uuid4(), first_name="Aleksandra", last_name="Doba", username="ALEDOB", hashed_password="some_hash")
    
    async_session.add_all([user1, user2, user3])
    await async_session.flush()
    
    user_role1 = UserRole(user_id=user1.id, team_id=team1.id, role=UserRoleEnum.OWNER)
    user_role2 = UserRole(user_id=user2.id, team_id=team1.id, role=UserRoleEnum.MEMBER)
    user_role3 = UserRole(user_id=user3.id, team_id=team1.id, role=UserRoleEnum.COACH)
    user_role1 = UserRole(user_id=user1.id, team_id=team2.id, role=UserRoleEnum.OWNER)
    user_role2 = UserRole(user_id=user2.id, team_id=team2.id, role=UserRoleEnum.MEMBER)
    user_role3 = UserRole(user_id=user3.id, team_id=team2.id, role=UserRoleEnum.COACH)
    
    async_session.add_all([user_role1, user_role2, user_role3])
    await async_session.flush()

    practice1 = Practice(
        id=uuid.uuid4(),
        team_id=team1.id,
        start_time=datetime(2026, 3, 11, 14, 30, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 3, 11, 16, 30, 0, tzinfo=timezone.utc),
        location="Location 1",
        description="Some Description",
    )
    practice2 = Practice(
        id=uuid.uuid4(),
        team_id=team1.id,
        start_time=datetime(2026, 3, 12, 14, 30, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 3, 12, 16, 30, 0, tzinfo=timezone.utc),
        location="Location 2",
        description="Some Description",
    )
    practice3 = Practice(
        id=uuid.uuid4(),
        team_id=team2.id,
        start_time=datetime(2026, 4, 13, 14, 30, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 4, 13, 16, 30, 0, tzinfo=timezone.utc),
        location="Some Location",
        description="Some Description",
    )

    async_session.add_all([practice1, practice2, practice3])
    await async_session.flush()

    entries_practice1 = [
        AttendanceEntry(
            practice_id=practice1.id,
            user_id=user1.id,
            planned_attendance=True,
            actual_attendance=True,
        ),
        AttendanceEntry(
            practice_id=practice1.id,
            user_id=user2.id,
            planned_attendance=True,
            actual_attendance=True,
        ),
        AttendanceEntry(
            practice_id=practice1.id,
            user_id=user3.id,
            planned_attendance=True,
            actual_attendance=True,
        ),
    ]

    entries_practice2 = [
        AttendanceEntry(
            practice_id=practice2.id,
            user_id=user1.id,
            planned_attendance=True,
            actual_attendance=True,
        ),
        AttendanceEntry(
            practice_id=practice2.id,
            user_id=user2.id,
            planned_attendance=True,
            actual_attendance=False,
        ),
        AttendanceEntry(
            practice_id=practice2.id,
            user_id=user3.id,
            planned_attendance=True,
            actual_attendance=True,
        ),
    ]

    async_session.add_all([*entries_practice1, *entries_practice2])
    await async_session.flush()

    result = await get_attendance_grid(
        session=async_session,
        team_id=team1.id,
        time_from=datetime(2026, 3, 11, 13, 30, 0, tzinfo=timezone.utc),
        time_to=datetime(2026, 3, 12, 17, 30, 0, tzinfo=timezone.utc),
    )

    assert len(result) == 2

    assert result[0].date == datetime(2026, 3, 11, 14, 30, 0, tzinfo=timezone.utc)
    assert result[0].attendance[0].user_id == entries_practice1[0].user_id
    assert result[0].attendance[0].real == entries_practice1[0].actual_attendance
    assert result[0].attendance[0].planned == entries_practice1[0].planned_attendance

    assert result[0].date <= result[1].date