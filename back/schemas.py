"""
Modelos Pydantic
"""

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserPersonalData(BaseModel):
    nombre: str
    apellido: str
    direccion: str
    telefono: str


class User(UserBase):
    id_user: int
    # hashed_pass: str
    personal_data: list[UserPersonalData] = []
