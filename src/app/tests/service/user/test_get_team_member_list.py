import uuid
import pytest

from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.service_layer.services.user.team_members_listing.service import get_team_members_service


@pytest.mark.asyncio
async def test_get_team_members_list(async_session):
    team1 = Team(id=uuid.uuid4(), name="Zeta")
    
    async_session.add(team1)
    
    user1 = User(id=uuid.uuid4(), first_name="Adam", last_name="Kowalski", username="ADAKOW")
    user2 = User(id=uuid.uuid4(), first_name="Jan", last_name="Lewandowski", username="JANLEW")
    user3 = User(id=uuid.uuid4(), first_name="Aleksandra", last_name="Doba", username="ALEDOB")
    
    async_session.add_all([user1, user2, user3])
    
    user_role1 = UserRole(user_id=user1.id, team_id=team1.id, role=UserRoleEnum.ADMIN)
    user_role2 = UserRole(user_id=user2.id, team_id=team1.id, role=UserRoleEnum.MEMBER)
    user_role3 = UserRole(user_id=user3.id, team_id=team1.id, role=UserRoleEnum.COACH)
    
    async_session.add_all([user_role1, user_role2, user_role3])
    
    result = await get_team_members_service(session=async_session, team_id=team1.id)
    
    assert len(result) == 3
    
    result_ids = {user.id for user in result}
    assert result_ids == {user1.id, user2.id, user3.id}

    assert result[0].last_name == "Doba"
    assert result[1].last_name == "Kowalski"