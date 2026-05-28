from datetime import datetime, timezone
import uuid
import pytest

from app.db_layer.orm_models.practice import Practice
from app.db_layer.orm_models.team import Team

@pytest.mark.asyncio
async def test_get_team_practices(client, async_session):
    team1 = Team(id=uuid.uuid4(), name="Alpha")
    team2 = Team(id=uuid.uuid4(), name="Beta")

    async_session.add_all([team1, team2])
    
    practice1 = Practice(
        id=uuid.uuid4(), 
        team_id=team1.id, 
        start_time=datetime(2026, 3, 11, 14, 30, 0, tzinfo=timezone.utc), 
        end_time=datetime(2026, 3, 11, 16, 30, 0, tzinfo=timezone.utc), 
        location="Location 1", 
        description="Some Description"
    )
    practice2 = Practice(
        id=uuid.uuid4(), 
        team_id=team1.id, 
        start_time=datetime(2026, 3, 12, 14, 30, 0, tzinfo=timezone.utc), 
        end_time=datetime(2026, 3, 12, 16, 30, 0, tzinfo=timezone.utc), 
        location="Location 2", 
        description="Some Description"
    )
    practice3 = Practice(
        id=uuid.uuid4(), 
        team_id=team2.id, 
        start_time=datetime(2026, 4, 13, 14, 30, 0, tzinfo=timezone.utc), 
        end_time=datetime(2026, 4, 13, 16, 30, 0, tzinfo=timezone.utc), 
        location="Some Location", 
        description="Some Description"
    )
    
    async_session.add_all([practice1, practice2, practice3])
    await async_session.flush()
    
    response = await client.get(
        f"/practice/schedule/{team1.id}",
        params={
            "time_from": "2026-03-10T00:00:00Z",
            "time_to": "2026-03-13T00:00:00Z"
        }
    )
    
    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["practice"][0]["location"] == "Location 1"
    assert data[1]["practice"][0]["location"] == "Location 2"