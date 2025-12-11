import uuid

from sqlalchemy.orm import Mapped, mapped_column


class IdBearer:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)