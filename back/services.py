from database import engine_to_database, drop_all_tables, setup_database, MySessionAsync
from models import UserDB, UserPersonalDataDB, TipoCultivoDB, PatronKcDB

import schemas
from passlib import hash
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import select
import asyncio

# from contextlib import asynccontextmanager
# @asynccontextmanager
async def initialize_db(from_scratch=True):
    engine = await engine_to_database()
    if from_scratch:
        await drop_all_tables(engine)
        await setup_database(engine)
        await TipoCultivoDB.__initialize__(engine)
        await PatronKcDB.__initialize__(engine)
    # yield engine
    await engine.dispose()


# @contextlib.asynccontextmanager
async def get_async_session():
    session = MySessionAsync
    session.begin()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_user_by_email(
    email: str,
    db: AsyncSession = MySessionAsync,
):
    """Gets a user by their email."""
    # query = select(User).where(User.email == email)
    # result = await db.execute(query)
    # return result.scalars().first()
    async with db.begin():
        try:
            stmt = select(UserDB).where(UserDB.email == email)
            result = await db.execute(stmt)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            await db.close()
    return result.scalars().first()


def hash_password(password):
    return hash.bcrypt.hash(password)


async def create_user(
    user: schemas.UserCreate,
    db: AsyncSession = MySessionAsync

):
    hashed_password = hash_password(user.password)
    db_user = UserDB(email=user.email, hashed_pass=hashed_password)
    async with db.begin():
        db.add(db_user)
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e
        finally:
            await db.close()
    return db_user


async def get_user_by_id(
    user_id: int,
    db: AsyncSession = MySessionAsync,
):
    """Gets a user by their id."""
    async with db.begin():
        try:
            stmt = select(UserDB).where(UserDB.id_user == user_id)
            result = await db.execute(stmt)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            await db.close()
    return result.scalars().first()


async def create_user_personal_data(
    user_id: int,
    personal_data: schemas.UserPersonalData,
    db: AsyncSession = MySessionAsync
):
    """Creates a user personal data."""
    db_user = await get_user_by_id(user_id=user_id, db=db)
    print(db_user)
    db_personal_data = UserPersonalDataDB(
        id_user=user_id,
        user=db_user,
        nombre=personal_data.nombre,
        apellido=personal_data.apellido,
        direccion=personal_data.direccion,
        telefono=personal_data.telefono,
    )
    async with db.begin():
        db.add(db_personal_data)
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e
        finally:
            await db.close()
    return db_personal_data


async def get_personal_data_by_user_id(
    user_id: int,
    db: AsyncSession = MySessionAsync,
):
    """Gets a personal data by user id."""
    async with db.begin():
        try:
            stmt = select(UserPersonalDataDB).where(UserPersonalDataDB.id_user == user_id)
            result = await db.execute(stmt)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            await db.close()
    return result.scalars().first()