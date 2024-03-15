"""
Modelos SQLAlchemy
"""

from database import Base

import sqlalchemy as _sql
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from passlib import hash
from typing import Optional

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

import logging
logger = logging.getLogger('models')

class UserDB(Base):
    __tablename__ = "users"
    id_user: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(_sql.String(100), index=True, unique=True)
    hashed_pass: Mapped[str] = mapped_column(_sql.String(100))
    personal_info: Mapped[list["UserPersonalDataDB"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan", lazy="joined",
    )
    created_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Function to verify password
    def verify_password(self, password: str) -> bool:
        return hash.bcrypt.verify(password, self.hashed_pass)

    def __repr__(self) -> str:
        return f"<User(id {self.id_user!r}, email {self.email!r})"


class UserPersonalDataDB(Base):
    __tablename__ = "user_personal_data"
    # id: Mapped[int] = mapped_column(primary_key=True)
    id_user: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"users.id_user"), primary_key=True
    )
    owner: Mapped["UserDB"] = relationship(back_populates="personal_info")
    # ponele
    nombre: Mapped[str] = mapped_column(_sql.String(100))
    apellido: Mapped[str] = mapped_column(_sql.String(100))
    direccion: Mapped[Optional[str]] = mapped_column(_sql.String(100))
    telefono: Mapped[Optional[str]] = mapped_column(_sql.String(100))
    def __repr__(self) -> str:
        return f"<UserPersonalData(id {self.id_user!r}, nombre {self.nombre!r}), apellido {self.apellido!r}>"


class EstacionUserDB(Base):
    __tablename__ = "estacion_usuario"
    id_estacion: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_user: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{UserDB.__tablename__}.id_user")
    )
    # Ubicación
    nombre: Mapped[str] = mapped_column(_sql.String(100))
    lat = mapped_column(_sql.Numeric(9, 7), nullable=False)
    lon = mapped_column(_sql.Numeric(9, 6), nullable=False)


class SueloUserDB(Base):
    __tablename__ = "suelo_usuario"
    id_suelo: Mapped[int] = mapped_column(primary_key=True)
    id_estacion: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{EstacionUserDB.__tablename__}.id_estacion")
    )
    tipo_suelo: Mapped[str] = mapped_column(_sql.String(100))
    # Datos total
    capacidad_campo = mapped_column(_sql.Numeric(7, 4))
    pmp = mapped_column(_sql.Numeric(7, 4))
    coef_escurrimiento = mapped_column(_sql.Numeric(2, 1))
    coef_percolacion = mapped_column(_sql.Numeric(9, 8))


### Copio lo del paquete para tenerlo aca
class TipoCultivoDB(Base):
    @classmethod
    async def __initialize__(cls, engine):
        logger = logging.getLogger(f"{__name__}.{__class__.__name__}")
        path = Path(__file__).parent
        tabla_inicial = pd.read_csv(
            path.joinpath("../tablas_iniciales/tipo_cultivo_fdc.csv")
        )
        # Agrego parche para que pueda insertar Nans
        tabla_inicial.replace(np.nan, None, inplace=True)
        # async with get_async_session(engine) as session:
        # session = AsyncSession(engine)
        # session.begin()
        # print('asd')
        async with AsyncSession(engine) as session:
            session.begin()
            # Pongo un coso para ver si algo falló
            try:
                await session.execute(
                    _sql.insert(TipoCultivoDB),
                    [
                        {
                            "codigo": tabla_inicial.iloc[i]["Codigo"],
                            "nombre": tabla_inicial.iloc[i]["Nombre"],
                        }
                        for i in range(len(tabla_inicial))
                    ],
                )
                await session.flush()
                await session.commit()
                logger.info("Todo fue insertado correctamente en 'tipos_cultivo'")
            except Exception as e:
                await session.rollback()
                raise e

    __tablename__ = "tipos_cultivo"
    id_tipo_cultivo: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(_sql.String(10), unique=True)
    nombre: Mapped[str] = mapped_column(_sql.String(100))

    def __repr__(self):
        return f"TipoCultivo(id_tipo_cultivo={self.id_tipo_cultivo!r}, codigo={self.codigo!r})"


class PatronKcDB(Base):
    async def __initialize__(engine):
        logger = logging.getLogger(f"{__name__}.{__class__.__name__}")
        path = Path(__file__).parent
        tabla_inicial = pd.read_csv(path.joinpath("../tablas_iniciales/patronkc.csv"))
        tabla_inicial.replace(np.nan, None, inplace=True)
        async with AsyncSession(engine) as session:
            try:
                await session.execute(
                    _sql.insert(PatronKcDB),
                    [
                        {
                            "codigo": tabla_inicial.iloc[i]["Codigo"],
                        }
                        for i in range(len(tabla_inicial))
                    ],
                )
                await session.flush()
                await session.commit()
                logger.info("Todo fue insertado correctamente en 'patron_kc' ")
            except Exception as e:
                await session.rollback()
                raise e

    __tablename__ = "patron_kc"
    id_patron: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(_sql.String(20), unique=True)

    def __repr__(self):
        return f"PatronKc(id_patron={self.id_patron!r}, codigo={self.codigo!r})"


class BalanceUserDB(Base):
    __tablename__ = "datos_balance_usuario"
    id_balance: Mapped[int] = mapped_column(primary_key=True)
    id_estacion: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{EstacionUserDB.__tablename__}.id_estacion")
    )
    id_suelo: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{SueloUserDB.__tablename__}.id_suelo")
    )
    id_tipo_cultivo: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{TipoCultivoDB.__tablename__}.id_tipo_cultivo")
    )
    id_patron: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{PatronKcDB.__tablename__}.id_patron")
    )

