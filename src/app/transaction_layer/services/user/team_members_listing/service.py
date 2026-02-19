import uuid

from sqlalchemy import select

from app.db import get_session
from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.transaction_layer.pydantic_models.user import UserFullName, UserList


async def get_team_member_list(team_id: uuid.uuid4):
    async with await get_session() as session:
        
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
        
    return UserList(
        user_list=[
            UserFullName(
                id=m.id,
                first_name=m.id,
                last_name=m.last_name, 
            )
            for m in members
        ]
    )