from pydantic import UUID4, BaseModel


# class UserModel(BaseModel):
#     id: UUID4
#     first_name: str
#     last_name: str
#     username: str
    
#     class Config:
#         frozen = False

class UserFullName(BaseModel):
    id: UUID4
    first_name: str
    last_name: str
    
class UserList(BaseModel):
    # team_id: UUID4
    user_list: list[UserFullName]