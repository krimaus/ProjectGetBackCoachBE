import uuid
import datetime as dt

import pytest
from sqlalchemy import select

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
        location="Test location",
        description="Practice 1",
    )
    async_session.add(practice)
    await async_session.flush()

    return team, practice


@pytest.mark.asyncio
async def test_delete_practice_allowed_for_owner(authorized_client, async_session, test_user):
    team, practice = await _setup_team_with_practice(async_session, UserRoleEnum.OWNER, test_user)

    response = await authorized_client.delete(f"/practice/{team.id}/{practice.id}")

    assert response.status_code == 204

    result = await async_session.execute(select(Practice).where(Practice.id == practice.id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_practice_allowed_for_coach(authorized_client, async_session, test_user):
    team, practice = await _setup_team_with_practice(async_session, UserRoleEnum.COACH, test_user)

    response = await authorized_client.delete(f"/practice/{team.id}/{practice.id}")

    assert response.status_code == 204

    result = await async_session.execute(select(Practice).where(Practice.id == practice.id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_practice_forbidden_for_member(authorized_client, async_session, test_user):
    team, practice = await _setup_team_with_practice(async_session, UserRoleEnum.MEMBER, test_user)

    response = await authorized_client.delete(f"/practice/{team.id}/{practice.id}")

    assert response.status_code == 403

    result = await async_session.execute(select(Practice).where(Practice.id == practice.id))
    assert result.scalar_one_or_none() is not None  # untouched


@pytest.mark.asyncio
async def test_delete_practice_forbidden_without_role_row(authorized_client, async_session):
    team, practice = await _setup_team_with_practice(async_session, role=None)

    response = await authorized_client.delete(f"/practice/{team.id}/{practice.id}")

    assert response.status_code == 403

    result = await async_session.execute(select(Practice).where(Practice.id == practice.id))
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_delete_practice_nonexistent_practice_returns_404(authorized_client, async_session, test_user):
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

    response = await authorized_client.delete(f"/practice/{team.id}/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_practice_cross_team_returns_404_and_does_not_delete(authorized_client, async_session, test_user):
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
        location="Test location",
        description="Practice 1",
    )
    async_session.add(practice)
    await async_session.flush()

    response = await authorized_client.delete(f"/practice/{team_a.id}/{practice.id}")

    assert response.status_code == 404

    result = await async_session.execute(select(Practice).where(Practice.id == practice.id))
    assert result.scalar_one_or_none() is not None