from database import engine_to_database, drop_all_tables, setup_database, MySessionAsync
from models import UserDB, UserPersonalDataDB, TipoCultivoDB, PatronKcDB

import schemas
from passlib import hash
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import select
import asyncio

import logging

logger = logging.getLogger(__name__)


async def initialize_db(from_scratch=True):
    engine = await engine_to_database()
    if from_scratch:
        await drop_all_tables(engine)
        await setup_database(engine)
        await TipoCultivoDB.__initialize__(engine)
        await PatronKcDB.__initialize__(engine)
    # yield engine
    await engine.dispose()


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


def hash_password(password):
    return hash.bcrypt.hash(password)


async def create_user(user: schemas.UserCreate, async_session: AsyncSession):
    hashed_password = hash_password(user.password)
    logger.info("Creating user")
    db_user = UserDB(email=user.email, hashed_pass=hashed_password)

    async_session.begin()
    async_session.add(db_user)
    try:
        await async_session.commit()
    except Exception as e:
        await async_session.rollback()
        raise e
    return db_user


async def get_user(
    async_session: AsyncSession,
    user_id: int | None = None,
    email: str | None = None,
):
    """Gets a user by either their email or id."""
    logger.info(f"Getting user {user_id} {email}")
    await async_session.begin()
    try:
        if user_id:
            stmt = select(UserDB).where(UserDB.id_user == user_id)
        elif email:
            stmt = select(UserDB).where(UserDB.email == email)
        else:
            return None
        result = await async_session.execute(stmt)
    except Exception as e:
        await async_session.rollback()
        logger.exception(e)
        raise e
    return result.scalars().first()


async def get_users(
    async_session: AsyncSession,
):
    """Gets a user by either their email or id."""
    logger.info(f"Getting all users")
    await async_session.begin()
    try:
        stmt = select(UserDB)
        result = await async_session.execute(stmt)
    except Exception as e:
        await async_session.rollback()
        logger.exception(e)
        raise e
    return result.scalars().all()


async def create_user_personal_data(
    user_id: int,
    personal_data: schemas.UserPersonalData,
    async_session: AsyncSession
):
    """Creates a user personal data."""
    logger.info(f"Creando personal data para usuario {user_id}")
    user = await get_user(async_session=async_session, user_id=user_id)
    db_personal_data = UserPersonalDataDB(
        id_user=user.id_user,
        # owner=user,
        nombre=personal_data.nombre,
        apellido=personal_data.apellido,
        direccion=personal_data.direccion,
        telefono=personal_data.telefono,
    )
    async_session.add(db_personal_data)
    try:
        await async_session.commit()
    except Exception as e:
        await async_session.rollback()
        raise e
    return db_personal_data


async def get_personal_data_by_user_id(
    user_id: int,
    async_session: AsyncSession,
):
    """Gets a personal data by user id."""
    async_session.begin()
    try:
        stmt = select(UserPersonalDataDB).where(
            UserPersonalDataDB.id_user == user_id
        )
        result = await async_session.execute(stmt)
    except Exception as e:
        async_session.rollback()
        raise e
    return result.scalars().first()


if __name__ == "__main__":
    import asyncio
    from pathlib import Path
    this_dir = Path(__file__).parent

    logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(Path(this_dir.joinpath('./logs/db_creation.log')), mode='w'),
        logging.StreamHandler()
    ],
    format='(%(name)s) - %(asctime)s - %(levelname)s - %(message)s',
)
    logger = logging.getLogger(__name__)

    asyncio.run(initialize_db(from_scratch=True))
