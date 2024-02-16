"""
Modelos SQLAlchemy
"""

from database import Base
import sqlalchemy as _sql
from sqlalchemy.orm import Mapped, mapped_column, relationship
from passlib import hash
from typing import Optional

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    hashed_pass: Mapped[str] = mapped_column()
    personal_info: Mapped[list["UserPersonalData"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    # Function to verify password
    def verify_password(self, password: str) -> bool:
        return hash.bcrypt.verify(password, self.hashed_pass)
    
    def __repr__(self) -> str:
        return f"<User(id {self.id!r}, email {self.email!r})"
        
class UserPersonalData(User):
    __tablename__ = "user_personal_data"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(_sql.ForeignKey(f"{User.__tablename__}.id"))
    user: Mapped["User"] = relationship(back_populates="personal_info")
    # ponele 
    direccion: Mapped[Optional[str]] = mapped_column()
    telefono: Mapped[Optional[str]] = mapped_column()


class Campo(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(_sql.ForeignKey(f"{User.__tablename__}.id"))

