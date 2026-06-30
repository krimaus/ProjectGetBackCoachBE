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