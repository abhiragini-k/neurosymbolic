from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from typing import Annotated
from pydantic import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str
    disabled: Optional[bool] = False
    
class User(UserBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    disabled: Optional[bool] = False

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

        json_encoders = {ObjectId: str}

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
