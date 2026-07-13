from pydantic import UUID4, BaseModel


# class UserModel(BaseModel):
#     id: UUID4
#     first_name: str
#     last_name: str
#     username: str
    
#     class Config:
#         frozen = False

class CreateUserInput(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    
    
class UpdateUserInput(BaseModel):
    first_name: str
    last_name: str
    username: str


class UserItem(BaseModel):
    id: UUID4
    first_name: str
    last_name: str
    full_name: str
    username: str