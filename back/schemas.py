"""
Modelos Pydantic
"""

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str

class UserPersonalDataBase(BaseModel):
    pass

class UserPersonalDataCreate(UserPersonalDataBase):
    nombre: str
    apellido: str
    direccion: str
    telefono: str


class UserPersonalData(UserPersonalDataCreate):
    model_config = ConfigDict(
        from_attributes=True
    )



class User(UserBase):
    id_user: int
    personal_data: list[UserPersonalData] = []

    model_config = ConfigDict(
        from_attributes=True
    )

