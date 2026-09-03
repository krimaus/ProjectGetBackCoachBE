import uuid
import datetime as dt

import pytest
from sqlalchemy import select

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.db_layer.orm_models.attendance import AttendanceEntry
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from app.db_layer.orm_models.practice import PracticeSeries


async def _setup_team_and_role(async_session, test_user, role):
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

    async_session.add(UserRole(user_id=test_user["id"], team_id=team.id, role=role))
    await async_session.flush()
    return team


def _recurring_payload(today: dt.date, future_day: dt.date) -> dict:
    return {
        "days_of_week": [future_day.weekday()],
        "start_date": today.isoformat(),
        "end_date": future_day.isoformat(),
        "start_time": "10:00:00Z",
        "end_time": "12:00:00Z",
        "location": "Test location",
        "description": "Recurring practice",
    }


@pytest.mark.asyncio
async def test_create_recurring_practice_allowed_for_owner(authorized_client, async_session, test_user):
    team = await _setup_team_and_role(async_session, test_user, UserRoleEnum.OWNER)

    today = dt.datetime.now(dt.timezone.utc).date()
    future_day = today + dt.timedelta(days=2)

    response = await authorized_client.post(
        f"/practice/{team.id}/recurring",
        json=_recurring_payload(today, future_day),
    )

    assert response.status_code == 201
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["team_id"] == str(team.id)
    assert data[0]["location"] == "Test location"
    assert data[0]["description"] == "Recurring practice"
    assert uuid.UUID(data[0]["id"])

    entries_stmt = select(AttendanceEntry)
    entries = (await async_session.execute(entries_stmt)).scalars().all()
    assert len(entries) == 1
    assert entries[0].user_id == test_user["id"]


@pytest.mark.asyncio
async def test_create_recurring_practice_allowed_for_coach(authorized_client, async_session, test_user):
    team = await _setup_team_and_role(async_session, test_user, UserRoleEnum.COACH)

    today = dt.datetime.now(dt.timezone.utc).date()
    future_day = today + dt.timedelta(days=2)

    response = await authorized_client.post(
        f"/practice/{team.id}/recurring",
        json=_recurring_payload(today, future_day),
    )

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["team_id"] == str(team.id)


@pytest.mark.asyncio
async def test_create_recurring_practice_forbidden_for_member(authorized_client, async_session, test_user):
    team = await _setup_team_and_role(async_session, test_user, UserRoleEnum.MEMBER)

    today = dt.datetime.now(dt.timezone.utc).date()
    future_day = today + dt.timedelta(days=2)

    response = await authorized_client.post(
        f"/practice/{team.id}/recurring",
        json=_recurring_payload(today, future_day),
    )

    assert response.status_code == 403

    series_stmt = select(PracticeSeries).where(PracticeSeries.team_id == team.id)
    series = (await async_session.execute(series_stmt)).scalar_one_or_none()
    assert series is None


@pytest.mark.asyncio
async def test_create_recurring_practice_forbidden_without_role_row(authorized_client, async_session):
    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    today = dt.datetime.now(dt.timezone.utc).date()
    future_day = today + dt.timedelta(days=2)

    response = await authorized_client.post(
        f"/practice/{team.id}/recurring",
        json=_recurring_payload(today, future_day),
    )

    assert response.status_code == 403