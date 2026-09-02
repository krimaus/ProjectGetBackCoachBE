from datetime import datetime, timezone
import uuid
import pytest

from app.db_layer.orm_models.practice import Practice
from app.db_layer.orm_models.team import Team
from app.service_layer.services.practice.service import get_team_practices


@pytest.mark.asyncio
async def test_get_team_practices(async_session):
    team1 = Team(id=uuid.uuid4(), name="Alpha")
    team2 = Team(id=uuid.uuid4(), name="Beta")

    async_session.add_all([team1, team2])
    await async_session.flush()
    
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
    
    result = await get_team_practices(
        session=async_session, team_id=team1.id, 
        time_from=datetime(2026, 3, 11, 13, 30, 0, tzinfo=timezone.utc), 
        time_to=datetime(2026, 3, 12, 17, 30, 0, tzinfo=timezone.utc)
    )
    
    assert len(result) == 2
    
    assert result[0].date == datetime(2026, 3, 11, 14, 30, 0, tzinfo=timezone.utc).date()
    assert result[0].practice[0].id == practice1.id
    assert result[0].practice[0].start_time == practice1.start_time
    assert result[0].practice[0].end_time == practice1.end_time
    assert result[0].practice[0].description == practice1.description
    
    assert result[0].date <= result[1].date