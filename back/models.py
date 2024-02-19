"""
Modelos SQLAlchemy
"""

from database import Base, get_session

import sqlalchemy as _sql
from sqlalchemy.orm import Mapped, mapped_column, relationship
from passlib import hash
from typing import Optional

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime



class User(Base):
    __tablename__ = "users"
    id_user: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    hashed_pass: Mapped[str] = mapped_column()
    personal_info: Mapped[list["UserPersonalData"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    created_time: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)
    # Function to verify password
    def verify_password(self, password: str) -> bool:
        return hash.bcrypt.verify(password, self.hashed_pass)
    
    def __repr__(self) -> str:
        return f"<User(id {self.id_user!r}, email {self.email!r})"
        
class UserPersonalData(User):
    __tablename__ = "user_personal_data"
    # id: Mapped[int] = mapped_column(primary_key=True)
    id_user: Mapped[int] = mapped_column(_sql.ForeignKey(f"{User.__tablename__}.id_user"), primary_key=True)
    user: Mapped["User"] = relationship(back_populates="personal_info")
    # ponele 
    direccion: Mapped[Optional[str]] = mapped_column()
    telefono: Mapped[Optional[str]] = mapped_column()

class EstacionUser(Base):
    __tablename__ = "estacion_usuario"
    id_estacion: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_user: Mapped[int] = mapped_column(_sql.ForeignKey(f"{User.__tablename__}.id_user"))
    # Ubicación
    nombre: Mapped[str] = mapped_column()
    lat = mapped_column(_sql.Numeric(9,7), nullable=False)
    lon = mapped_column(_sql.Numeric(9,6), nullable=False)

class SueloUser(Base):
    __tablename__ = "suelo_usuario"
    id_suelo: Mapped[int] = mapped_column(primary_key=True)
    id_estacion: Mapped[int] = mapped_column(_sql.ForeignKey(f"{EstacionUser.__tablename__}.id_estacion"))
    tipo_suelo: Mapped[str] = mapped_column()
    # Datos total
    capacidad_campo = mapped_column(_sql.Numeric(7,4))
    pmp = mapped_column(_sql.Numeric(7,4))
    coef_escurrimiento = mapped_column(_sql.Numeric(2,1))
    coef_percolacion = mapped_column(_sql.Numeric(9,8))

### Copio lo del paquete para tenerlo aca
class TipoCultivo(Base):
    def __initialize__():
        path = Path(__file__).parent
        tabla_inicial = pd.read_csv(path.joinpath('../tablas_iniciales/tipo_cultivo_fdc.csv'))
        # Agrego parche para que pueda insertar Nans
        tabla_inicial.replace(np.nan, None, inplace=True)
        with get_session() as session:
            # Pongo un coso para ver si algo falló
            try:
                session.bulk_insert_mappings(
                    TipoCultivo, [
                        {
                            "codigo":tabla_inicial.iloc[i]['Codigo'],
                            "nombre":tabla_inicial.iloc[i]['Nombre'],
                            # "etapa_siembra":tabla_inicial.iloc[i]['EtapaSiembra'],
                            # "etapa_cosecha":tabla_inicial.iloc[i]['EtapaCosecha'],
                            # "etapa_inicioPC_deficit":tabla_inicial.iloc[i]['EtapaInicioPCDeficit'],
                            # "delta_inicioPC_deficit":tabla_inicial.iloc[i]['DeltaInicioPCDeficit'],
                            # "etapa_finPC_deficit":tabla_inicial.iloc[i]['EtapaFinPCDeficit'],
                            # "delta_finPC_deficit":tabla_inicial.iloc[i]['DeltaFinPCDeficit'],
                            # "etapa_inicioPC_exceso":tabla_inicial.iloc[i]['EtapaInicioPCExceso'],
                            # "delta_inicioPC_exceso":tabla_inicial.iloc[i]['DeltaInicioPCExceso'],
                            # "etapa_finPC_exceso":tabla_inicial.iloc[i]['EtapaFinPCExceso'],
                            # "delta_finPC_exceso":tabla_inicial.iloc[i]['DeltaFinPCExceso'],
                        } for i in range(len(tabla_inicial))
                    ]
                )
                session.flush()
                session.commit()
                print("Todo fue insertado correctamente en 'tipos_cultivo'")
            except:
                session.rollback()
                print(f"Falló la inserción inicial en 'tipos_cultivo' ")
        return True

    __tablename__ = 'tipos_cultivo'
    id_tipo_cultivo: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column()
    nombre: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"TipoCultivo(id_tipo_cultivo={self.id_tipo_cultivo!r}, codigo={self.codigo!r})"

class PatronKc(Base):
    def __initialize__():
        path = Path(__file__).parent
        tabla_inicial = pd.read_csv(path.joinpath('../tablas_iniciales/patronkc.csv'))
        tabla_inicial.replace(np.nan, None, inplace=True)
        with get_session() as session:
            try:     
                session.bulk_insert_mappings(
                    PatronKc, [
                        {
                            "codigo":tabla_inicial.iloc[i]['Codigo'],
                        } for i in range(len(tabla_inicial))
                    ]
                )
                session.flush()
                session.commit()
                print("Todo fue insertado correctamente en 'patron_kc' ")
            except:
                session.rollback()
                print(f"Falló la inserción inicial en 'patron_kc' ")
        return True

    __tablename__ = 'patron_kc'
    id_patron = mapped_column(primary_key=True)
    codigo = mapped_column()

    def __repr__(self):
        return f"PatronKc(id_patron={self.id_patron!r}, codigo={self.codigo!r})"


class BalanceUser(Base):
    __tablename__ = 'datos_balance_usuario'
    id_balance: Mapped[int] = mapped_column(primary_key=True)
    id_estacion: Mapped[int] = mapped_column(_sql.ForeignKey(f"{EstacionUser.__tablename__}.id_estacion"))
    id_suelo: Mapped[int] = mapped_column(_sql.ForeignKey(f"{SueloUser.__tablename__}.id_suelo"))
    id_tipo_cultivo: Mapped[int] = mapped_column(_sql.ForeignKey(f"{TipoCultivo.__tablename__}.id_tipo_cultivo"))
    id_patron: Mapped[int] = mapped_column(_sql.ForeignKey(f"{PatronKc.__tablename__}.id_patron"))

