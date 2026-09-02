import uuid
from datetime import datetime, timezone

import pytest

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.practice import Practice
from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum


@pytest.mark.asyncio
async def test_get_team_practice_allowed_with_real_role_row(authorized_client, async_session, test_user):
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

    user_role = UserRole(user_id=test_user["id"], team_id=team.id, role=UserRoleEnum.COACH)
    async_session.add(user_role)
    await async_session.flush()

    practice = Practice(
        id=uuid.uuid4(),
        team_id=team.id,
        start_time=datetime(2026, 6, 10, 10, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 6, 10, 12, 0, 0, tzinfo=timezone.utc),
        description="Practice 1",
        location="Test location",
    )
    async_session.add(practice)
    await async_session.flush()

    response = await authorized_client.get(
        f"/practice/{team.id}",
        params={
            "time_from": "2026-06-09T00:00:00Z",
            "time_to": "2026-06-12T00:00:00Z",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    day = data[0]
    assert day["date"] == "2026-06-10"
    assert len(day["practice"]) == 1

    item = day["practice"][0]
    assert item["id"] == str(practice.id)
    assert item["start_time"] == "2026-06-10T10:00:00Z"
    assert item["end_time"] == "2026-06-10T12:00:00Z"
    assert item["description"] == "Practice 1"


@pytest.mark.asyncio
async def test_get_team_practice_forbidden_without_role_row(authorized_client, async_session):
    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    response = await authorized_client.get(
        f"/practice/{team.id}",
        params={
            "time_from": "2026-06-09T00:00:00Z",
            "time_to": "2026-06-12T00:00:00Z",
        },
    )

    assert response.status_code == 403