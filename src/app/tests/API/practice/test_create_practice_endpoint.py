import uuid

import pytest
from sqlalchemy import select

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.db_layer.orm_models.attendance import AttendanceEntry
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum


@pytest.mark.asyncio
async def test_create_practice_allowed_for_coach(authorized_client, async_session, test_user, future_window):
    team = Team(id=uuid.uuid4(), name="Alpha")
    user = User(
        id=test_user["id"],
        first_name="Adam",
        last_name="Kowalski",
        username=test_user["username"],
        hashed_password="some_hash",
    )
    async_session.add_all([team, user])
    await async_session.flush()

    async_session.add(UserRole(user_id=test_user["id"], team_id=team.id, role=UserRoleEnum.COACH))
    await async_session.flush()

    start_time, end_time = future_window()

    response = await authorized_client.post(
        f"/practice/{team.id}",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "location": "Test location",
            "description": "Practice 1",
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert data["team_id"] == str(team.id)
    assert data["location"] == "Test location"
    assert data["description"] == "Practice 1"
    assert data["series_id"] is None

    entries_stmt = select(AttendanceEntry)
    entries = (await async_session.execute(entries_stmt)).scalars().all()
    assert len(entries) == 1
    assert entries[0].user_id == test_user["id"]


@pytest.mark.asyncio
async def test_create_practice_forbidden_for_member(authorized_client, async_session, test_user, future_window):
    team = Team(id=uuid.uuid4(), name="Alpha")
    user = User(
        id=test_user["id"],
        first_name="Adam",
        last_name="Kowalski",
        username=test_user["username"],
        hashed_password="some_hash",
    )
    async_session.add_all([team, user])
    await async_session.flush()

    async_session.add(UserRole(user_id=test_user["id"], team_id=team.id, role=UserRoleEnum.MEMBER))
    await async_session.flush()

    start_time, end_time = future_window()

    response = await authorized_client.post(
        f"/practice/{team.id}",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "location": "Test location",
            "description": "Practice 1",
        },
    )

    assert response.status_code == 403

    entries_stmt = select(AttendanceEntry)
    entries = (await async_session.execute(entries_stmt)).scalars().all()
    assert len(entries) == 0


@pytest.mark.asyncio
async def test_create_practice_forbidden_without_role_row(authorized_client, async_session):
    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    response = await authorized_client.post(
        f"/practice/{team.id}",
        json={
            "start_time": "2099-01-01T10:00:00Z",
            "end_time": "2099-01-01T12:00:00Z",
            "location": "Test location",
            "description": "Practice 1",
        },
    )

    assert response.status_code == 403