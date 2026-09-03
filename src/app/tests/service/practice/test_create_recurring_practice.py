import uuid
import datetime as dt

import pytest
from sqlalchemy import select

from app.db_layer.orm_models.team import Team
from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.db_layer.orm_models.practice import Practice, PracticeSeries
from app.db_layer.orm_models.attendance import AttendanceEntry
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from app.service_layer.pydantic_models.practice import CreateRecurringPracticeInput
from app.service_layer.services.practice.service import create_recurring_practice_service


@pytest.mark.asyncio
async def test_create_recurring_practice_service_only_creates_future_occurrences_and_fans_out_attendance(async_session):
    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    user1 = User(id=uuid.uuid4(), first_name="Adam", last_name="Kowalski", username="ADAKOW", hashed_password="some_hash")
    user2 = User(id=uuid.uuid4(), first_name="Jan", last_name="Lewandowski", username="JANLEW", hashed_password="some_hash")
    async_session.add_all([user1, user2])
    await async_session.flush()

    async_session.add_all([
        UserRole(user_id=user1.id, team_id=team.id, role=UserRoleEnum.MEMBER),
        UserRole(user_id=user2.id, team_id=team.id, role=UserRoleEnum.COACH),
    ])
    await async_session.flush()

    today = dt.datetime.now(dt.timezone.utc).date()
    past_day = today - dt.timedelta(days=1)
    future_day = today + dt.timedelta(days=2)

    payload = CreateRecurringPracticeInput(
        days_of_week=[past_day.weekday(), future_day.weekday()],
        start_date=past_day,
        end_date=future_day,
        start_time=dt.time(10, 0, tzinfo=dt.timezone.utc),
        end_time=dt.time(12, 0, tzinfo=dt.timezone.utc),
        location="Test location",
        description="Recurring practice",
    )

    result = await create_recurring_practice_service(async_session, team.id, payload)

    assert len(result) == 1
    created = result[0]
    assert created.team_id == team.id
    assert created.start_time == dt.datetime.combine(future_day, dt.time(10, 0), tzinfo=dt.timezone.utc)
    assert created.end_time == dt.datetime.combine(future_day, dt.time(12, 0), tzinfo=dt.timezone.utc)
    assert created.location == "Test location"
    assert created.description == "Recurring practice"

    series_stmt = select(PracticeSeries).where(PracticeSeries.team_id == team.id)
    series = (await async_session.execute(series_stmt)).scalar_one()
    assert series.start_date == past_day
    assert series.end_date == future_day
    assert sorted(series.days_of_week) == sorted({past_day.weekday(), future_day.weekday()})
    assert created.series_id == series.id

    practice_stmt = select(Practice).where(Practice.id == created.id)
    persisted_practice = (await async_session.execute(practice_stmt)).scalar_one()
    assert persisted_practice.team_id == team.id

    all_practices_stmt = select(Practice).where(Practice.team_id == team.id)
    all_practices = (await async_session.execute(all_practices_stmt)).scalars().all()
    assert len(all_practices) == 1

    entries_stmt = select(AttendanceEntry)
    entries = (await async_session.execute(entries_stmt)).scalars().all()
    assert len(entries) == 2
    assert {e.practice_id for e in entries} == {created.id}
    assert {e.user_id for e in entries} == {user1.id, user2.id}


@pytest.mark.asyncio
async def test_create_recurring_practice_service_no_future_occurrences_creates_no_practices(async_session):
    team = Team(id=uuid.uuid4(), name="Alpha")
    async_session.add(team)
    await async_session.flush()

    today = dt.datetime.now(dt.timezone.utc).date()
    past_start = today - dt.timedelta(days=10)
    past_end = today - dt.timedelta(days=1)

    payload = CreateRecurringPracticeInput(
        days_of_week=[past_start.weekday()],
        start_date=past_start,
        end_date=past_end,
        start_time=dt.time(10, 0, tzinfo=dt.timezone.utc),
        end_time=dt.time(12, 0, tzinfo=dt.timezone.utc),
        location="Test location",
        description="Recurring practice",
    )

    result = await create_recurring_practice_service(async_session, team.id, payload)

    assert result == []

    series_stmt = select(PracticeSeries).where(PracticeSeries.team_id == team.id)
    series = (await async_session.execute(series_stmt)).scalar_one_or_none()
    assert series is not None

    entries_stmt = select(AttendanceEntry)
    entries = (await async_session.execute(entries_stmt)).scalars().all()
    assert len(entries) == 0


@pytest.mark.asyncio
async def test_create_recurring_practice_service_no_team_members_creates_no_attendance_entries(async_session):
    team = Team(id=uuid.uuid4(), name="Beta")
    async_session.add(team)
    await async_session.flush()

    today = dt.datetime.now(dt.timezone.utc).date()
    future_day = today + dt.timedelta(days=2)

    payload = CreateRecurringPracticeInput(
        days_of_week=[future_day.weekday()],
        start_date=today,
        end_date=future_day,
        start_time=dt.time(10, 0, tzinfo=dt.timezone.utc),
        end_time=dt.time(12, 0, tzinfo=dt.timezone.utc),
        location="Test location",
        description="Recurring practice",
    )

    result = await create_recurring_practice_service(async_session, team.id, payload)

    assert len(result) == 1

    entries_stmt = select(AttendanceEntry)
    entries = (await async_session.execute(entries_stmt)).scalars().all()
    assert len(entries) == 0