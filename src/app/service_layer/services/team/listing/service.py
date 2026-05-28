from app.db_layer.orm_models.team import Team
from app.service_layer.pydantic_models.team import TeamItem
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select


async def get_team_names(session: AsyncSession) -> list[TeamItem]:
    stmt = (
        select(Team.id, Team.name)
        .order_by(Team.name)
    )

    result = await session.execute(stmt)
    rows = result.all()

    return [
        TeamItem(
            id=row.id,
            name=row.name
        )
        for row in rows
    ]