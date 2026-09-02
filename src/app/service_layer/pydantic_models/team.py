from typing import Literal
from uuid import UUID

from pydantic import UUID4, BaseModel

from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum


# class TeamModel(BaseModel):
#     id: UUID4
#     name: str
    
#     class Config:
#         frozen = False

class TeamItem(BaseModel):
    id: UUID4
    name: str
    
class CreateTeamInput(BaseModel):
    name: str
    
    
class InviteMembersInput(BaseModel):
    id_list: list[UUID]
    
    
class DeleteMembersInput(BaseModel):
    id_list: list[UUID]
    
    
class ChangeNameInput(BaseModel):
    name: str
    
    
class ChangeRankInput(BaseModel):
    role: Literal[UserRoleEnum.MEMBER, UserRoleEnum.COACH]
    
    
class DeleteInviteInput(BaseModel):
    id_list: list[UUID]