from database_test import engine_to_database, drop_all_tables, setup_database
from models_test import UserModel, AddressModel

import schemas_test
from passlib import hash
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import uuid4

import logging
logger = logging.getLogger('services')


def hash_password(password):
    return hash.bcrypt.hash(password)


async def get_async_session():
    session = async_sessionmaker(bind=engine_to_database, expire_on_commit=False)
    session.begin()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def create_user(
        user: schemas_test.UserCreate, 
        async_session: AsyncSession,
    ):
    hashed_password = hash_password(user.password)
    logger.info('Creando usuario')
    db_user = UserModel(
        name=user.name, 
        hashed_pass=hashed_password,
        fullname=user.fullname,
        nickname=user.nickname,
        )
    async_session.begin()
    async_session.add(db_user)
    try:
        await async_session.commit()
    except Exception as e:
        await async_session.rollback()
        raise e
    await async_session.refresh(db_user)
    return db_user

async def get_user_by_id(
        id: int,
        async_session: AsyncSession, 
):
    stmt = select(UserModel).where(UserModel.id == id)
    async_session.begin()
    try:
        result = await async_session.execute(stmt)
    except Exception as e:
        await async_session.rollback()
        raise e
    return result.scalars().first()                                    
    

async def get_address_by_id(
        id: int, 
        async_session: AsyncSession,
):
    stmt = select(AddressModel).where(AddressModel.user_id == id)
    async_session.begin()
    try:
        result = await async_session.execute(stmt)
    except Exception as e:
        await async_session.rollback()
        raise e
    return result.scalars().first()

async def create_user_address(
        user_id: int,
        address: schemas_test.AddressCreate,
        async_session: AsyncSession,
    ):
    logger.info('Obtengo usuario')
    user = await get_user_by_id(id=user_id, async_session=async_session)
    logger.info('Creando la dirección')
    db_address = AddressModel(
        user_id = user.id,
        email_address = address.email_address
    )
    async_session.begin()
    async_session.add(db_address)
    try:
        await async_session.commit()
    except Exception as e:
        await async_session.rollback()
        raise e
    await async_session.refresh(db_address)
    return db_address



# async def get_user(
#     user_id: int,
#     async_session: async_sessionmaker[AsyncSession]
#     ):
#     logger.info(f'Getting user {user_id}')
#     async with async_session() as session:
#         try:
#             stmt = select(UserModel).join(UserModel.addresses).where(UserModel.id == user_id)
#             result = await session.execute(stmt)
#         except Exception as e:
#             session.rollback()
#             logger.exception(e)
#             raise e
#         finally:
#             await session.close()
#     return result.scalars().first()


