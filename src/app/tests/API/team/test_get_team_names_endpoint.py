import uuid
import pytest

from app.db_layer.orm_models.team import Team


@pytest.mark.asyncio
async def test_list_teams_endpoint_returns_sorted_list(client, async_session):
    team1 = Team(id=uuid.uuid4(), name="Zeta")
    team2 = Team(id=uuid.uuid4(), name="Alpha")
    team3 = Team(id=uuid.uuid4(), name="Delta")

    async_session.add_all([team1, team2, team3])
    await async_session.commit()

    response = await client.get("/teams/names")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert [team["name"] for team in data] == ["Alpha", "Delta", "Zeta"]