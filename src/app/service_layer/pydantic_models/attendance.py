import datetime as dt
from pydantic import UUID4, BaseModel


# class AttendanceEntryModel(BaseModel):
#     user_id: UUID4
#     planned_attendance: bool | None = Field(default=None)
#     actual_attendance: bool | None = Field(default=None)

#     class Config:
#         frozen = False
        
    
# class AttendanceModel(BaseModel):
#     practice_id: UUID4
#     attendance_list: list[AttendanceEntryModel]
#     notes: str | None = Field(default=None)
    
#     class Config:
#         frozen = False

class AttendanceItem(BaseModel):
    user_id: UUID4
    real: bool
    planned: bool

class AttendanceListingItem(BaseModel):
    date: dt.datetime
    attendance: list[AttendanceItem]