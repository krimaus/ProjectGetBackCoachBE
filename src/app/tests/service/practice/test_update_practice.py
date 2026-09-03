import uuid
import datetime as dt

import pytest
from fastapi import HTTPException

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.practice import Practice
from app.service_layer.pydantic_models.practice import UpdatePracticeInput
from app.service_layer.services.practice.service import update_practice_service


@pytest.mark.asyncio
async def test_update_practice_service_updates_fields(async_session, future_window):
    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    practice = Practice(
        id=uuid.uuid4(),
        team_id=team.id,
        start_time=dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1),
        end_time=dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1, hours=2),
        location="Old location",
        description="Old description",
    )
    async_session.add(practice)
    await async_session.flush()

    new_start, new_end = future_window(days_ahead=10)
    payload = UpdatePracticeInput(
        start_time=new_start,
        end_time=new_end,
        location="New location",
        description="New description",
    )

    result = await update_practice_service(async_session, practice.id, team.id, payload)

    assert result.id == practice.id
    assert result.team_id == team.id
    assert result.start_time == new_start
    assert result.end_time == new_end
    assert result.location == "New location"
    assert result.description == "New description"

    await async_session.refresh(practice)
    assert practice.location == "New location"
    assert practice.description == "New description"


@pytest.mark.asyncio
async def test_update_practice_service_nonexistent_practice_raises_404(async_session, future_window):
    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    start_time, end_time = future_window()
    payload = UpdatePracticeInput(
        start_time=start_time,
        end_time=end_time,
        location="New location",
        description="New description",
    )

    with pytest.raises(HTTPException) as exc_info:
        await update_practice_service(async_session, uuid.uuid4(), team.id, payload)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Practice not found"


@pytest.mark.asyncio
async def test_update_practice_service_cross_team_practice_raises_404(async_session, future_window):
    team_a = Team(id=uuid.uuid4(), name="Alpha")
    team_b = Team(id=uuid.uuid4(), name="Beta")
    async_session.add_all([team_a, team_b])
    await async_session.flush()

    practice = Practice(
        id=uuid.uuid4(),
        team_id=team_b.id,
        start_time=dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1),
        end_time=dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1, hours=2),
        location="Old location",
        description="Old description",
    )
    async_session.add(practice)
    await async_session.flush()

    start_time, end_time = future_window(days_ahead=10)
    payload = UpdatePracticeInput(
        start_time=start_time,
        end_time=end_time,
        location="Hijacked location",
        description="Hijacked description",
    )

    with pytest.raises(HTTPException) as exc_info:
        await update_practice_service(async_session, practice.id, team_a.id, payload)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Practice not found"

    await async_session.refresh(practice)
    assert practice.location == "Old location"