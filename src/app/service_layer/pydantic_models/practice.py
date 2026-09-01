from uuid import UUID

from pydantic import UUID4, AwareDatetime, BaseModel, Field, field_validator, model_validator
import datetime as dt


class PracticeItem(BaseModel):
    team_id: UUID
    start_time: dt.datetime
    end_time: dt.datetime
    location: str
    description: str | None
    series_id: UUID | None
        
class BulkPracticeItem(BaseModel):
    id: UUID4
    start_time: dt.datetime
    end_time: dt.datetime
    description: str


class TeamPracticeListingItem(BaseModel):
    date: dt.date
    practice: list[BulkPracticeItem]
    
    
class CreatePracticeInput(BaseModel):
    start_time: AwareDatetime
    end_time: AwareDatetime
    location: str
    description: str
    
    @field_validator("start_time", "end_time")
    @classmethod
    def must_be_utc(cls, v):
        if v.utcoffset() != dt.timezone.utc.utcoffset(None):
            raise ValueError("datetime must be in UTC")
        return v
    
    @field_validator("start_time", "end_time")
    @classmethod
    def require_time_in_future(cls, v: AwareDatetime) -> AwareDatetime:
        if v < dt.datetime.now(dt.timezone.utc):
            raise ValueError(f"datetime must be in the future")
        return v

    @model_validator(mode="after")
    def check_times(self) -> "CreatePracticeInput":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self
    
    
class UpdatePracticeInput(BaseModel):
    start_time: AwareDatetime
    end_time: AwareDatetime
    location: str
    description: str
    
    @field_validator("start_time", "end_time")
    @classmethod
    def must_be_utc(cls, v):
        if v.utcoffset() != dt.timezone.utc.utcoffset(None):
            raise ValueError("datetime must be in UTC")
        return v

    @field_validator("start_time", "end_time")
    @classmethod
    def require_timezone(cls, v: AwareDatetime) -> AwareDatetime:
        if v.tzinfo is None:
            raise ValueError("datetime must include timezone info (e.g. '+00:00' or 'Z')")
        return v
    
    @field_validator("start_time", "end_time")
    @classmethod
    def require_time_in_future(cls, v: AwareDatetime) -> AwareDatetime:
        if v < dt.datetime.now(dt.timezone.utc):
            raise ValueError(f"datetime must be in the future")
        return v

    @model_validator(mode="after")
    def check_times(self) -> "CreatePracticeInput":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self
    
    
class ActualAttendanceEntry(BaseModel):
    user_id: UUID4
    actual_attendance: bool


class MarkActualAttendanceInput(BaseModel):
    entries: list[ActualAttendanceEntry]

    @field_validator("entries")
    @classmethod
    def no_duplicate_users(cls, v):
        ids = [e.user_id for e in v]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate user_id in entries")
        return v
    
    
MAX_RECURRING_PRACTICE_SPAN_DAYS = 365

class CreateRecurringPracticeInput(BaseModel):
    days_of_week: list[int] = Field(..., min_length=1)  # 0=Mon - 6=Sun
    start_date: dt.date
    end_date: dt.date
    start_time: dt.time
    end_time: dt.time
    location: str | None = None
    description: str | None = None

    @field_validator("days_of_week")
    @classmethod
    def validate_days(cls, v: list[int]) -> list[int]:
        if not all(0 <= d <= 6 for d in v):
            raise ValueError("days_of_week must be 0 (Mon) through 6 (Sun)")
        return sorted(set(v))

    @field_validator("start_time", "end_time")
    @classmethod
    def must_be_utc(cls, v: dt.time) -> dt.time:
        if v.utcoffset() != dt.timedelta(0):
            raise ValueError("start_time/end_time must be UTC")
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> "CreateRecurringPracticeInput":
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        if (self.end_date - self.start_date).days > MAX_RECURRING_PRACTICE_SPAN_DAYS:
            raise ValueError(
                f"date range cannot exceed {MAX_RECURRING_PRACTICE_SPAN_DAYS} days"
            )
        return self
    
    
class UpdateRecurringPracticeInput(BaseModel):
    days_of_week: list[int] = Field(..., min_length=1)  # 0=Mon..6=Sun
    start_date: dt.date
    end_date: dt.date
    start_time: dt.time
    end_time: dt.time
    location: str | None = None
    description: str | None = None

    @field_validator("days_of_week")
    @classmethod
    def validate_days(cls, v: list[int]) -> list[int]:
        if not all(0 <= d <= 6 for d in v):
            raise ValueError("days_of_week must be 0 (Mon) through 6 (Sun)")
        return sorted(set(v))

    @field_validator("start_time", "end_time")
    @classmethod
    def must_be_utc(cls, v: dt.time) -> dt.time:
        if v.utcoffset() != dt.timedelta(0):
            raise ValueError("start_time/end_time must be UTC")
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> "CreateRecurringPracticeInput":
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        if (self.end_date - self.start_date).days > MAX_RECURRING_PRACTICE_SPAN_DAYS:
            raise ValueError(
                f"date range cannot exceed {MAX_RECURRING_PRACTICE_SPAN_DAYS} days"
            )
        return self