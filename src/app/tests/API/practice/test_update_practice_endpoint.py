import uuid
import datetime as dt

import pytest

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.db_layer.orm_models.practice import Practice
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum


async def _setup_team_with_practice(async_session, role, test_user=None):
    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    if test_user is not None:
        user = User(
            id=test_user["id"],
            first_name="Adam",
            last_name="Kowalski",
            username=test_user["username"],
            hashed_password="some_hash",
        )
        async_session.add(user)
        await async_session.flush()
        async_session.add(UserRole(user_id=test_user["id"], team_id=team.id, role=role))
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

    return team, practice


@pytest.mark.asyncio
async def test_update_practice_allowed_for_owner(authorized_client, async_session, test_user, future_window):
    team, practice = await _setup_team_with_practice(async_session, UserRoleEnum.OWNER, test_user)

    start_time, end_time = future_window(days_ahead=10)

    response = await authorized_client.put(
        f"/practice/{team.id}/{practice.id}",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "location": "New location",
            "description": "New description",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(practice.id)
    assert data["location"] == "New location"


@pytest.mark.asyncio
async def test_update_practice_allowed_for_coach(authorized_client, async_session, test_user, future_window):
    team, practice = await _setup_team_with_practice(async_session, UserRoleEnum.COACH, test_user)

    start_time, end_time = future_window(days_ahead=10)

    response = await authorized_client.put(
        f"/practice/{team.id}/{practice.id}",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "location": "New location",
            "description": "New description",
        },
    )

    assert response.status_code == 200
    assert response.json()["location"] == "New location"


@pytest.mark.asyncio
async def test_update_practice_forbidden_for_member(authorized_client, async_session, test_user, future_window):
    team, practice = await _setup_team_with_practice(async_session, UserRoleEnum.MEMBER, test_user)

    start_time, end_time = future_window(days_ahead=10)

    response = await authorized_client.put(
        f"/practice/{team.id}/{practice.id}",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "location": "New location",
            "description": "New description",
        },
    )

    assert response.status_code == 403

    await async_session.refresh(practice)
    assert practice.location == "Old location"


@pytest.mark.asyncio
async def test_update_practice_forbidden_without_role_row(authorized_client, async_session, future_window):
    team, practice = await _setup_team_with_practice(async_session, role=None)

    start_time, end_time = future_window(days_ahead=10)

    response = await authorized_client.put(
        f"/practice/{team.id}/{practice.id}",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "location": "New location",
            "description": "New description",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_practice_nonexistent_practice_returns_404(authorized_client, async_session, test_user, future_window):
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
    async_session.add(UserRole(user_id=test_user["id"], team_id=team.id, role=UserRoleEnum.OWNER))
    await async_session.flush()

    start_time, end_time = future_window(days_ahead=10)

    response = await authorized_client.put(
        f"/practice/{team.id}/{uuid.uuid4()}",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "location": "New location",
            "description": "New description",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_practice_cross_team_returns_404(authorized_client, async_session, test_user, future_window):
    team_a = Team(id=uuid.uuid4(), name="Alpha")
    team_b = Team(id=uuid.uuid4(), name="Beta")
    user = User(
        id=test_user["id"],
        first_name="Adam",
        last_name="Kowalski",
        username=test_user["username"],
        hashed_password="some_hash",
    )
    async_session.add_all([team_a, team_b, user])
    await async_session.flush()
    async_session.add(UserRole(user_id=test_user["id"], team_id=team_a.id, role=UserRoleEnum.OWNER))
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

    response = await authorized_client.put(
        f"/practice/{team_a.id}/{practice.id}",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "location": "Hijacked location",
            "description": "Hijacked description",
        },
    )

    assert response.status_code == 404

    await async_session.refresh(practice)
    assert practice.location == "Old location"