import uuid
from datetime import datetime, timezone

import pytest

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.practice import Practice
from app.db_layer.orm_models.attendance import AttendanceEntry
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole


@pytest.mark.asyncio
async def test_get_attendance_grid(authorized_client, async_session, mock_user_role):
    mock_user_role(UserRoleEnum.COACH, target="app.communications_layer.endpoints.attendance.check_user_role_in_team")

    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    user1 = User(id=uuid.uuid4(), first_name="Adam", last_name="Kowalski", username="ADAKOW", hashed_password="some_hash")
    user2 = User(id=uuid.uuid4(), first_name="Jan", last_name="Lewandowski", username="JANLEW", hashed_password="some_hash")
    user3 = User(id=uuid.uuid4(), first_name="Aleksandra", last_name="Doba", username="ALEDOB", hashed_password="some_hash")
    
    async_session.add_all([user1, user2, user3])
    await async_session.flush()
    
    user_role1 = UserRole(user_id=user1.id, team_id=team.id, role=UserRoleEnum.OWNER)
    user_role2 = UserRole(user_id=user2.id, team_id=team.id, role=UserRoleEnum.MEMBER)
    user_role3 = UserRole(user_id=user3.id, team_id=team.id, role=UserRoleEnum.COACH)
    
    async_session.add_all([user_role1, user_role2, user_role3])
    await async_session.flush()

    practice1 = Practice(
        id=uuid.uuid4(),
        team_id=team.id,
        start_time=datetime(2026, 6, 10, 10, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 6, 10, 12, 0, 0, tzinfo=timezone.utc),
        description="Practice 1",
        location="Test location",
    )
    practice2 = Practice(
        id=uuid.uuid4(),
        team_id=team.id,
        start_time=datetime(2026, 6, 11, 10, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 6, 11, 12, 0, 0, tzinfo=timezone.utc),
        description="Practice 2",
        location="Test location",
    )
    practice_out_of_range = Practice(
        id=uuid.uuid4(),
        team_id=team.id,
        start_time=datetime(2026, 6, 20, 10, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 6, 20, 12, 0, 0, tzinfo=timezone.utc),
        description="Out of range",
        location="Test location",
    )
    async_session.add_all([practice1, practice2, practice_out_of_range])
    await async_session.flush()

    async_session.add_all([
        AttendanceEntry(
            practice_id=practice1.id,
            user_id=user1.id,
            planned_attendance=True,
            actual_attendance=True,
        ),
        AttendanceEntry(
            practice_id=practice1.id,
            user_id=user2.id,
            planned_attendance=True,
            actual_attendance=False,
        ),
        AttendanceEntry(
            practice_id=practice2.id,
            user_id=user1.id,
            planned_attendance=False,
            actual_attendance=False,
        ),
        AttendanceEntry(
            practice_id=practice_out_of_range.id,
            user_id=user1.id,
            planned_attendance=True,
            actual_attendance=True,
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
    user1_entry = next(e for e in first["attendance"] if e["user_id"] == str(user1.id))
    assert user1_entry["planned"] is True
    assert user1_entry["real"] is True

    second = data[1]
    assert second["date"] == "2026-06-11T10:00:00Z"
    assert len(second["attendance"]) == 1
    assert second["attendance"][0]["user_id"] == str(user1.id)
    assert second["attendance"][0]["planned"] is False
    assert second["attendance"][0]["real"] is False