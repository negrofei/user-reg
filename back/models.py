"""
Modelos SQLAlchemy
"""

from database import Base
from database import engine_to_database, setup_database, drop_all_tables

import sqlalchemy as _sql
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from passlib import hash
from typing import Optional

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

import asyncio


class User(Base):
    __tablename__ = "users"
    id_user: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(_sql.String(100), index=True, unique=True)
    hashed_pass: Mapped[str] = mapped_column(_sql.String(100))
    personal_info: Mapped[list["UserPersonalData"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    created_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Function to verify password
    def verify_password(self, password: str) -> bool:
        return hash.bcrypt.verify(password, self.hashed_pass)

    def __repr__(self) -> str:
        return f"<User(id {self.id_user!r}, email {self.email!r})"


class UserPersonalData(User):
    __tablename__ = "user_personal_data"
    # id: Mapped[int] = mapped_column(primary_key=True)
    id_user: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{User.__tablename__}.id_user"), primary_key=True
    )
    user: Mapped["User"] = relationship(back_populates="personal_info")
    # ponele
    direccion: Mapped[Optional[str]] = mapped_column(_sql.String(100))
    telefono: Mapped[Optional[str]] = mapped_column(_sql.String(100))


class EstacionUser(Base):
    __tablename__ = "estacion_usuario"
    id_estacion: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_user: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{User.__tablename__}.id_user")
    )
    # Ubicación
    nombre: Mapped[str] = mapped_column(_sql.String(100))
    lat = mapped_column(_sql.Numeric(9, 7), nullable=False)
    lon = mapped_column(_sql.Numeric(9, 6), nullable=False)


class SueloUser(Base):
    __tablename__ = "suelo_usuario"
    id_suelo: Mapped[int] = mapped_column(primary_key=True)
    id_estacion: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{EstacionUser.__tablename__}.id_estacion")
    )
    tipo_suelo: Mapped[str] = mapped_column(_sql.String(100))
    # Datos total
    capacidad_campo = mapped_column(_sql.Numeric(7, 4))
    pmp = mapped_column(_sql.Numeric(7, 4))
    coef_escurrimiento = mapped_column(_sql.Numeric(2, 1))
    coef_percolacion = mapped_column(_sql.Numeric(9, 8))


### Copio lo del paquete para tenerlo aca
class TipoCultivo(Base):
    @classmethod
    async def __initialize__(cls, engine):
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
                    _sql.insert(TipoCultivo),
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
                print("Todo fue insertado correctamente en 'tipos_cultivo'")
            except Exception as e:
                await session.rollback()
                raise e

    __tablename__ = "tipos_cultivo"
    id_tipo_cultivo: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(_sql.String(10), unique=True)
    nombre: Mapped[str] = mapped_column(_sql.String(100))

    def __repr__(self):
        return f"TipoCultivo(id_tipo_cultivo={self.id_tipo_cultivo!r}, codigo={self.codigo!r})"


class PatronKc(Base):
    async def __initialize__(engine):
        path = Path(__file__).parent
        tabla_inicial = pd.read_csv(path.joinpath("../tablas_iniciales/patronkc.csv"))
        tabla_inicial.replace(np.nan, None, inplace=True)
        async with AsyncSession(engine) as session:
            try:
                await session.execute(
                    _sql.insert(PatronKc),
                    [
                        {
                            "codigo": tabla_inicial.iloc[i]["Codigo"],
                        }
                        for i in range(len(tabla_inicial))
                    ],
                )
                await session.flush()
                await session.commit()
                print("Todo fue insertado correctamente en 'patron_kc' ")
            except Exception as e:
                await session.rollback()
                raise e

    __tablename__ = "patron_kc"
    id_patron: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(_sql.String(20), unique=True)

    def __repr__(self):
        return f"PatronKc(id_patron={self.id_patron!r}, codigo={self.codigo!r})"


class BalanceUser(Base):
    __tablename__ = "datos_balance_usuario"
    id_balance: Mapped[int] = mapped_column(primary_key=True)
    id_estacion: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{EstacionUser.__tablename__}.id_estacion")
    )
    id_suelo: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{SueloUser.__tablename__}.id_suelo")
    )
    id_tipo_cultivo: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{TipoCultivo.__tablename__}.id_tipo_cultivo")
    )
    id_patron: Mapped[int] = mapped_column(
        _sql.ForeignKey(f"{PatronKc.__tablename__}.id_patron")
    )


if __name__ == "__main__":

    async def initialize_db(from_scratch=True):
        engine = await engine_to_database()
        if from_scratch:
            await drop_all_tables(engine)
            await setup_database(engine)
        await TipoCultivo.__initialize__(engine)
        await PatronKc.__initialize__(engine)
        await engine.dispose()

    asyncio.run(initialize_db(from_scratch=False))
