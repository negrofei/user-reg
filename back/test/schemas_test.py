"""
Modelos Pydantic
"""

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    name: str
    fullname: str
    nickname: str


class UserCreate(UserBase):
    password: str


class AddressBase(BaseModel):
    pass


class AddressCreate(AddressBase):
    email_address: str

class AddressResponse(AddressCreate):
    id: int
    user_id: int

    model_config = ConfigDict(
        from_attributes=True
    )

class UserResponse(UserBase):
    id: int
    addresses: list[AddressResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )
