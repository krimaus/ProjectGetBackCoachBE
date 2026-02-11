from pydantic import BaseModel, UUID4, Field


class AttendanceEntryModel(BaseModel):
    user_id: UUID4
    planned_attendance: bool | None = Field(default=None)
    actual_attendance: bool | None = Field(default=None)

    class Config:
        frozen = False
        
    
class AttendanceModel(BaseModel):
    practice_id: UUID4
    attendance_list: list[AttendanceEntryModel]
    notes: str | None = Field(default=None)
    
    class Config:
        frozen = False