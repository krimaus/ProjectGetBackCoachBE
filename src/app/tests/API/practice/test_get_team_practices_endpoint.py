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
        start_time=datetime(2026, 3, 11, 14, 30, 0, tzinfo=timezone.UTC), 
        end_time=datetime(2026, 3, 11, 16, 30, 0, tzinfo=timezone.UTC), 
        location="Location 1", 
        description="Some Description"
    )
    practice2 = Practice(
        id=uuid.uuid4(), 
        team_id=team1.id, 
        start_time=datetime(2026, 3, 12, 14, 30, 0, tzinfo=timezone.UTC), 
        end_time=datetime(2026, 3, 12, 16, 30, 0, tzinfo=timezone.UTC), 
        location="Location 2", 
        description="Some Description"
    )
    practice3 = Practice(
        id=uuid.uuid4(), 
        team_id=team2.id, 
        start_time=datetime(2026, 4, 13, 14, 30, 0, tzinfo=timezone.UTC), 
        end_time=datetime(2026, 4, 13, 16, 30, 0, tzinfo=timezone.UTC), 
        location="Some Location", 
        description="Some Description"
    )
    
    async_session.add_all([practice1, practice2, practice3])
    await async_session.commit()
    
    response = await client.get(f"/practice/schedule/{team1.id}")
    
    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert [practice["location"] for practice in data] == ["Location 1", "Location 2"]