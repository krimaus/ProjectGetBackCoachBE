from uuid import UUID

from pydantic import UUID4, BaseModel, field_validator, model_validator
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
    start_time: dt.datetime
    end_time: dt.datetime
    location: str
    description: str

    @field_validator("start_time", "end_time")
    @classmethod
    def require_timezone(cls, v: dt.datetime) -> dt.datetime:
        if v.tzinfo is None:
            raise ValueError("datetime must include timezone info (e.g. '+00:00' or 'Z')")
        return v

    @model_validator(mode="after")
    def check_times(self) -> "CreatePracticeInput":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self