from dataclasses import dataclass
from pydantic import BaseModel, UUID4, Field


class AttendanceEntry(BaseModel):
    user_id: UUID4
    planned_attendance: bool | None = Field(default=None)
    actual_attendance: bool | None = Field(default=None)

    class Config:
        frozen = False
        
    
class Attendance(BaseModel):
    practice_id: UUID4
    attendance_list: list[AttendanceEntry]
    notes: str | None = Field(default=None)
    
    class Config:
        frozen = False