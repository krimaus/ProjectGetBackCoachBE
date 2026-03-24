import uuid
import pytest

from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole


@pytest.mark.asyncio
async def test_get_team_members_list_endpoint(client, async_session):
    team1 = Team(id=uuid.uuid4(), name="Zeta")
    
    async_session.add(team1)
    await async_session.commit()
    
    user1 = User(id=uuid.uuid4(), first_name="Adam", last_name="Kowalski", username="ADAKOW")
    user2 = User(id=uuid.uuid4(), first_name="Jan", last_name="Lewandowski", username="JANLEW")
    user3 = User(id=uuid.uuid4(), first_name="Aleksandra", last_name="Doba", username="ALEDOB")
    
    async_session.add_all([user1, user2, user3])
    await async_session.commit()
    
    user_role1 = UserRole(user_id=user1.id, team_id=team1.id, role=UserRoleEnum.ADMIN)
    user_role2 = UserRole(user_id=user2.id, team_id=team1.id, role=UserRoleEnum.MEMBER)
    user_role3 = UserRole(user_id=user3.id, team_id=team1.id, role=UserRoleEnum.COACH)
    
    async_session.add_all([user_role1, user_role2, user_role3])
    await async_session.commit()
    
    response = await client.get(f"/users/{team1.id}/names")
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert len(data) == 3