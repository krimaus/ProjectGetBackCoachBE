import uuid

from app.db_layer.orm_models.team import Team
from app.transaction_layer.pydantic_models.team import TeamItem

from sqlalchemy import select

from app.db import get_session


async def get_team_names(cls):
    async with await get_session() as session:
    
        stmt = (
            select(Team.id, Team.name)
            .order_by(Team.name)
        )
        
        result = await session.execute(stmt)
        rows = result.all()

    return [
        TeamItem(
            id=id,
            name=name
        )
        for id, name in rows
    ]