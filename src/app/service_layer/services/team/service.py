from app.db_layer.orm_models.team import Team
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.service_layer.pydantic_models import TeamItem
from src.app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from src.app.db_layer.orm_models.user_role import UserRole
from src.app.service_layer.pydantic_models.team import CreateTeamInput


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
    
async def create_team_service(session: AsyncSession, user: dict, payload: CreateTeamInput) -> TeamItem:
    team = Team(
        name=payload.name
    )
    
    session.add(team)
    await session.commit()
    await session.refresh(team)
    
    user_role = UserRole(
        team_id=team.id,
        user_id=user['id'],
        role=UserRoleEnum.COACH
    )
    
    session.add(user_role)
    await session.commit()
    
    return TeamItem(
        id=team.id,
        name=team.name
    )