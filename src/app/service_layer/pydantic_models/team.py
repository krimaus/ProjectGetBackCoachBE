from uuid import UUID

from pydantic import UUID4, BaseModel


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
    
    
class AddMembersInput(BaseModel):
    id_list: list[UUID]
    
    
class DeleteMembersInput(BaseModel):
    id_list: list[UUID]