import uuid

from sqlalchemy import select

from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.service_layer.pydantic_models import UserFullName
from sqlalchemy.ext.asyncio import AsyncSession


async def get_team_member_list(session: AsyncSession, team_id: uuid.UUID) -> list[UserFullName]:
  
    stmt = (
        select(User)
        .join(UserRole, User.id == UserRole.user_id)
        .where(
            UserRole.team_id == team_id
        )
        .order_by(User.last_name)
    )
    
    result = await session.execute(stmt)
    members = result.scalars().all()
        
    return [
            UserFullName(
                id=m.id,
                first_name=m.first_name,
                last_name=m.last_name, 
            )
            for m in members
        ]