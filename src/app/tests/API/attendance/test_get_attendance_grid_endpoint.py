import uuid
import pytest
from datetime import datetime, timezone

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.practice import Practice
from app.db_layer.orm_models.attendance import Attendance
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum


@pytest.mark.asyncio
async def test_get_attendance_grid(authorized_client, async_session, mock_user_role):
    mock_user_role(UserRoleEnum.OWNER)
    
    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())

    practice1 = Practice(
        id=uuid.uuid4(),
        team_id=team.id,
        start_time=datetime(2026, 6, 10, 10, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 6, 10, 12, 0, 0, tzinfo=timezone.utc),
        description="Practice 1",
        location="Test location"
    )
    practice2 = Practice(
        id=uuid.uuid4(),
        team_id=team.id,
        start_time=datetime(2026, 6, 11, 10, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 6, 11, 12, 0, 0, tzinfo=timezone.utc),
        description="Practice 2",
        location="Test location"
    )
    practice_out_of_range = Practice(
        id=uuid.uuid4(),
        team_id=team.id,
        start_time=datetime(2026, 6, 20, 10, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 6, 20, 12, 0, 0, tzinfo=timezone.utc),
        description="Out of range",
        location="Test location"
    )
    async_session.add_all([practice1, practice2, practice_out_of_range])
    await async_session.flush()

    async_session.add_all([
        Attendance(
            practice_id=practice1.id,
            attendance_list=[
                {"user_id": user1_id, "planned": True, "real": True},
                {"user_id": user2_id, "planned": True, "real": False},
            ],
        ),
        Attendance(
            practice_id=practice2.id,
            attendance_list=[
                {"user_id": user1_id, "planned": False, "real": False},
            ],
        ),
        Attendance(
            practice_id=practice_out_of_range.id,
            attendance_list=[
                {"user_id": user1_id, "planned": True, "real": True},
            ],
        ),
    ])
    await async_session.flush()

    response = await authorized_client.get(
        f"/attendance/{team.id}/grid",
        params={
            "time_from": "2026-06-09T00:00:00Z",
            "time_to": "2026-06-12T00:00:00Z",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    first = data[0]
    assert first["date"] == "2026-06-10T10:00:00Z"
    assert len(first["attendance"]) == 2
    user1_entry = next(e for e in first["attendance"] if e["user_id"] == user1_id)
    assert user1_entry["planned"] is True
    assert user1_entry["real"] is True

    second = data[1]
    assert second["date"] == "2026-06-11T10:00:00Z"
    assert len(second["attendance"]) == 1
    assert second["attendance"][0]["user_id"] == user1_id
    assert second["attendance"][0]["planned"] is False
    assert second["attendance"][0]["real"] is False