import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.db_layer.orm_models.attendance import AttendanceEntry
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from app.service_layer.pydantic_models.practice import CreatePracticeInput
from app.service_layer.services.practice.service import create_practice_service


@pytest.mark.asyncio
async def test_create_practice_service_creates_attendance_entries_for_team_members(async_session, future_window):
    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    user1 = User(id=uuid.uuid4(), first_name="Adam", last_name="Kowalski", username="ADAKOW", hashed_password="some_hash")
    user2 = User(id=uuid.uuid4(), first_name="Jan", last_name="Lewandowski", username="JANLEW", hashed_password="some_hash")
    async_session.add_all([user1, user2])
    await async_session.flush()

    async_session.add_all([
        UserRole(user_id=user1.id, team_id=team.id, role=UserRoleEnum.MEMBER),
        UserRole(user_id=user2.id, team_id=team.id, role=UserRoleEnum.COACH),
    ])
    await async_session.flush()

    start_time, end_time = future_window()
    payload = CreatePracticeInput(
        start_time=start_time,
        end_time=end_time,
        location="Test location",
        description="Practice 1",
    )

    result = await create_practice_service(async_session, team.id, payload)

    assert result.team_id == team.id
    assert result.start_time == payload.start_time
    assert result.end_time == payload.end_time
    assert result.location == payload.location
    assert result.description == payload.description
    assert result.series_id is None

    entries_stmt = select(AttendanceEntry)
    entries = (await async_session.execute(entries_stmt)).scalars().all()

    assert len(entries) == 2
    entry_user_ids = {e.user_id for e in entries}
    assert entry_user_ids == {user1.id, user2.id}
    for entry in entries:
        assert entry.planned_attendance is None
        assert entry.actual_attendance is None


@pytest.mark.asyncio
async def test_create_practice_service_no_team_members_creates_no_attendance_entries(async_session, future_window):
    team = Team(id=uuid.uuid4(), name="Beta")
    async_session.add(team)
    await async_session.flush()

    start_time, end_time = future_window()
    payload = CreatePracticeInput(
        start_time=start_time,
        end_time=end_time,
        location="Test location",
        description="Practice 1",
    )

    result = await create_practice_service(async_session, team.id, payload)

    assert result.team_id == team.id

    entries_stmt = select(AttendanceEntry)
    entries = (await async_session.execute(entries_stmt)).scalars().all()

    assert len(entries) == 0