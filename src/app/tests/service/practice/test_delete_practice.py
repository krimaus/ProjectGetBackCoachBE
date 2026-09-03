import uuid
import datetime as dt

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.practice import Practice
from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.attendance import AttendanceEntry
from app.service_layer.services.practice.service import delete_practice_service


@pytest.mark.asyncio
async def test_delete_practice_service_deletes_practice(async_session):
    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    practice = Practice(
        id=uuid.uuid4(),
        team_id=team.id,
        start_time=dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1),
        end_time=dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1, hours=2),
        location="Test location",
        description="Practice 1",
    )
    async_session.add(practice)
    await async_session.flush()

    await delete_practice_service(async_session, team.id, practice.id)

    result = await async_session.execute(select(Practice).where(Practice.id == practice.id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_practice_service_cascades_attendance_entries(async_session):
    team = Team(id=uuid.uuid4(), name="Alpha")
    user = User(id=uuid.uuid4(), first_name="Adam", last_name="Kowalski", username="ADAKOW", hashed_password="some_hash")
    async_session.add_all([team, user])
    await async_session.flush()

    practice = Practice(
        id=uuid.uuid4(),
        team_id=team.id,
        start_time=dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1),
        end_time=dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1, hours=2),
        location="Test location",
        description="Practice 1",
    )
    async_session.add(practice)
    await async_session.flush()

    async_session.add(AttendanceEntry(practice_id=practice.id, user_id=user.id))
    await async_session.flush()

    await delete_practice_service(async_session, team.id, practice.id)

    result = await async_session.execute(
        select(AttendanceEntry).where(AttendanceEntry.practice_id == practice.id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_practice_service_nonexistent_practice_raises_404(async_session):
    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    with pytest.raises(HTTPException) as exc_info:
        await delete_practice_service(async_session, team.id, uuid.uuid4())

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Practice not found"


@pytest.mark.asyncio
async def test_delete_practice_service_cross_team_raises_404_and_does_not_delete(async_session):
    team_a = Team(id=uuid.uuid4(), name="Alpha")
    team_b = Team(id=uuid.uuid4(), name="Beta")
    async_session.add_all([team_a, team_b])
    await async_session.flush()

    practice = Practice(
        id=uuid.uuid4(),
        team_id=team_b.id,
        start_time=dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1),
        end_time=dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1, hours=2),
        location="Test location",
        description="Practice 1",
    )
    async_session.add(practice)
    await async_session.flush()

    with pytest.raises(HTTPException) as exc_info:
        await delete_practice_service(async_session, team_a.id, practice.id)

    assert exc_info.value.status_code == 404

    result = await async_session.execute(select(Practice).where(Practice.id == practice.id))
    assert result.scalar_one_or_none() is not None