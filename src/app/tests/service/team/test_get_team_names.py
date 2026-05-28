import pytest
import uuid

from app.db_layer.orm_models.team import Team
from app.service_layer.services.team.listing.service import get_team_names


@pytest.mark.asyncio
async def test_get_team_names_returns_sorted_team_list(async_session):
    team1 = Team(id=uuid.uuid4(), name="Zeta")
    team2 = Team(id=uuid.uuid4(), name="Alpha")
    team3 = Team(id=uuid.uuid4(), name="Delta")

    async_session.add_all([team1, team2, team3])

    result = await get_team_names(async_session)

    assert len(result) == 3

    assert [team.name for team in result] == ["Alpha", "Delta", "Zeta"]

    assert result[0].id == team2.id
    assert result[0].name == "Alpha"
    
@pytest.mark.asyncio
async def test_get_team_names_returns_empty_list_when_no_teams(async_session):
    result = await get_team_names(async_session)
    assert result == []