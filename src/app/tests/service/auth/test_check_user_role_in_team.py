import uuid

import pytest

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from app.service_layer.services.auth.service import check_user_role_in_team


@pytest.mark.asyncio
async def test_check_user_role_in_team_returns_role_when_present(async_session):
    team = Team(id=uuid.uuid4(), name="Alpha")
    user = User(id=uuid.uuid4(), first_name="Adam", last_name="Kowalski", username="ADAKOW", hashed_password="some_hash")
    async_session.add_all([team, user])
    await async_session.flush()

    user_role = UserRole(user_id=user.id, team_id=team.id, role=UserRoleEnum.COACH)
    async_session.add(user_role)
    await async_session.flush()

    result = await check_user_role_in_team(async_session, user.id, team.id)

    assert result == UserRoleEnum.COACH


@pytest.mark.asyncio
async def test_check_user_role_in_team_returns_none_when_no_row(async_session):
    team = Team(id=uuid.uuid4(), name="Alpha")
    user = User(id=uuid.uuid4(), first_name="Jan", last_name="Lewandowski", username="JANLEW", hashed_password="some_hash")
    async_session.add_all([team, user])
    await async_session.flush()

    result = await check_user_role_in_team(async_session, user.id, team.id)

    assert result is None


@pytest.mark.asyncio
async def test_check_user_role_in_team_returns_none_for_different_team(async_session):
    team1 = Team(id=uuid.uuid4(), name="Alpha")
    team2 = Team(id=uuid.uuid4(), name="Beta")
    user = User(id=uuid.uuid4(), first_name="Ewa", last_name="Nowak", username="EWANOW", hashed_password="some_hash")
    async_session.add_all([team1, team2, user])
    await async_session.flush()

    user_role = UserRole(user_id=user.id, team_id=team1.id, role=UserRoleEnum.OWNER)
    async_session.add(user_role)
    await async_session.flush()

    result = await check_user_role_in_team(async_session, user.id, team2.id)

    assert result is None