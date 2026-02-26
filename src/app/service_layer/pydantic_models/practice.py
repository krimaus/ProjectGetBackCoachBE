from pydantic import UUID4, BaseModel
import datetime as dt
        
class PracticeItem(BaseModel):
    id: UUID4
    start_time: dt.datetime
    end_time: dt.datetime
    description: str


class TeamPracticeListingItem(BaseModel):
    date: dt.date
    practice: list[PracticeItem]