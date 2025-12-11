import dataclasses
import datetime as dt
import uuid


@dataclasses.dataclass
class AttendanceItem:
    # user_id: uuid.UUID
    real: bool
    planned: bool

@dataclasses.dataclass
class AttendanceListingItem:
    date: dt.date
    attendance: list[AttendanceItem]

class TeamAttendanceListing:

    @classmethod
    async def service(cls, team_id: uuid.UUID):
        # TODO: remember to sort results by player names!!!

        return [
            AttendanceListingItem(
                date=dt.date.today(),
                attendance=[
                    AttendanceItem(
                        real=False,
                        planned=False,
                    ),
                    AttendanceItem(
                        real=False,
                        planned=True,
                    ),
                    AttendanceItem(
                        real=True,
                        planned=True,
                    )
                ]
            )
        ]
