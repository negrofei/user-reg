"""
Main
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import schemas_test 
import services_test

from pydantic import EmailStr
import logging
from pathlib import Path

from database_test import engine
from sqlalchemy.ext.asyncio import async_sessionmaker

this_dir = Path(__file__).parent

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(Path(this_dir.joinpath('./logs/test.log')), mode='w'),
        logging.StreamHandler()
    ],
    format='(%(name)s) - %(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('main')

### Armo el objeto de la app
app = FastAPI(
    title="prueba",
    description="API para el registro de usuarios",
)


# Armo la session
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


# Endpoint para crear un usuario (only email required)
@app.post("/users/", response_model=schemas_test.UserResponse)
async def create_user(
    user: schemas_test.UserCreate
    ):
    """Creates a new user with the given email and password"""
    logger.info(f'Creando usuario {user.name}')
    session = async_session()
    created_user = await services_test.create_user(user=user, async_session=session)
    await session.close()
    return created_user

@app.get("/users/", response_model=schemas_test.UserResponse)
async def get_user(
    id: int | None,
):
    """Gets user"""
    logger.info("Getting user ...")
    session = async_session()
    user = await services_test.get_user_by_id(id=id, async_session=session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.close()
    return user

@app.post("/users/address", response_model=schemas_test.AddressResponse)
async def create_user_address(
    user_id: int,
    address: schemas_test.AddressCreate
    ):
    """ Creates a new email address for the user """
    logger.info(f'Creando email address usuario {user_id}')
    session = async_session()
    created_address = await services_test.create_user_address(
        user_id=user_id, 
        address=address, 
        async_session=session
    )
    return created_address
