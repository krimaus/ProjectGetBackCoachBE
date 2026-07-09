from pydantic import UUID4, BaseModel

from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum


# class UserRoleModel(BaseModel):
#     team_id: UUID4
#     user_id: UUID4
#     role: UserRoleEnum
    
#     class Config:
#         frozen = False
        
        
class UserRoleItem(BaseModel):
    team_id: UUID4
    user_id: UUID4
    role: UserRoleEnum