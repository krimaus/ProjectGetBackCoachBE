import uuid
import pytest

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum


@pytest.mark.asyncio
async def test_list_teams_endpoint_returns_sorted_list(authorized_client, async_session, mock_user_role):
    mock_user_role(UserRoleEnum.OWNER, target="app.communications_layer.endpoints.team.check_user_role_in_team")
    
    team1 = Team(id=uuid.uuid4(), name="Zeta")
    team2 = Team(id=uuid.uuid4(), name="Alpha")
    team3 = Team(id=uuid.uuid4(), name="Delta")

    async_session.add_all([team1, team2, team3])
    await async_session.flush()

    response = await authorized_client.get("/teams/names")

    assert response.status_code == 200

    data = response.json()

    assert [team["name"] for team in data] == ["Alpha", "Delta", "Zeta"]