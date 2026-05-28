from datetime import datetime, timezone
import uuid

import pytest

from app.db_layer.orm_models.attendance import Attendance
from app.db_layer.orm_models.practice import Practice
from app.db_layer.orm_models.team import Team
from app.service_layer.services.attendance.attendance_grid.service import get_attendance_grid

@pytest.mark.asyncio
async def test_get_attendance_grid(async_session):
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
    
    attendance_list1 = [
        {"user_id": str(uuid.uuid4()), "planned": True, "real": True},
        {"user_id": str(uuid.uuid4()), "planned": True, "real": True},
        {"user_id": str(uuid.uuid4()), "planned": True, "real": True},
    ]
    
    attendance1 = Attendance(
        practice_id=practice1.id,
        attendance_list=attendance_list1,
        notes="Some Note"
    )
    
    attendance_list2 = [
        {"user_id": str(uuid.uuid4()), "planned": True, "real": True},
        {"user_id": str(uuid.uuid4()), "planned": True, "real": False},
        {"user_id": str(uuid.uuid4()), "planned": True, "real": True},
    ]
    
    attendance2 = Attendance(
        practice_id=practice2.id,
        attendance_list=attendance_list2,
        notes="Some Note"
    )
    
    attendance3 = Attendance(
        practice_id=practice3.id,
        attendance_list=[],
        notes="Some Note"
    )
    
    async_session.add_all([attendance1,attendance2,attendance3])
    
    result = await get_attendance_grid(session=async_session, team_id=team1.id, time_from=datetime(2026, 3, 11, 13, 30, 0, tzinfo=timezone.utc), time_to=datetime(2026, 3, 12, 17, 30, 0, tzinfo=timezone.utc))
    
    assert len(result) == 2
    
    assert result[0].date == datetime(2026, 3, 11, 14, 30, 0, tzinfo=timezone.utc)
    assert result[0].attendance[0].user_id == uuid.UUID(attendance_list1[0]["user_id"])
    assert result[0].attendance[0].real == attendance_list1[0]["real"]
    assert result[0].attendance[0].planned == attendance_list1[0]["planned"]
    
    assert result[0].date <= result[1].date