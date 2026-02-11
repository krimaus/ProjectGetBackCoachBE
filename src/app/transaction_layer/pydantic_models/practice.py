from pydantic import UUID4, BaseModel
import datetime as dt


class PracticeModel(BaseModel):
    id: UUID4
    team_id: UUID4
    start_time: dt.datetime
    end_time: dt.datetime
    location: str
    description: str

    class Config:
        frozen = False