from uuid import UUID

from pydantic import UUID4, AwareDatetime, BaseModel, field_validator, model_validator
import datetime as dt
        
class PracticeItem(BaseModel):
    id: UUID4
    start_time: dt.datetime
    end_time: dt.datetime
    description: str


class TeamPracticeListingItem(BaseModel):
    date: dt.date
    practice: list[PracticeItem]
    
    
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