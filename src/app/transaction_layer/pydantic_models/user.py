from pydantic import UUID4, BaseModel


class UserModel(BaseModel):
    id: UUID4
    first_name: str
    last_name: str
    username: str
    
    class Config:
        frozen = False