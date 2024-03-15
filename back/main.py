"""
Main
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from schemas import UserCreate, UserBase, User, UserPersonalData
import services
from database import engine

from pydantic import EmailStr
import logging
from pathlib import Path

### Preparación
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

# Armo la session
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

# Armo el objeto de la app
app = FastAPI(
    title="prueba",
    description="API para el registro de usuarios",
)


# Endpoint para crear un usuario (only email required)
@app.post("/users/", response_model=UserBase)
async def create_user(
    user: UserCreate, 
):
    """Creates a new user with the given email and password"""
    logger.info(f'Creando usuario {user.email}')
    session = async_session()
    db_user = await services.get_user(async_session=session, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="That mail is already in use!")
    created_user = await services.create_user(async_session=session, user=user)
    session.close()
    return created_user


@app.get("/users/", response_model=User)
async def get_user(
    user_id: int | None = None,
    email: EmailStr | None = None,
):
    session = async_session()
    if not (email or user_id):
        raise HTTPException(status_code=404, detail="You must provide user id or email")
    db_user = await services.get_user(async_session=session, user_id=user_id, email=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.close()
    return db_user

@app.get("/users/all", response_model=list[User])
async def get_users():
    session = async_session()
    db_users = await services.get_users(async_session=session)
    await session.close()
    return db_users


@app.post("/users/{user_id}/personal_data/", response_model=UserPersonalData)
async def create_personal_data(
    user_id: int,
    personal_data: UserPersonalData,
):
    """Creates a user personal data by ID"""
    logger.info(f'Creando personal data para usuario {user_id}')
    session = async_session()
    db_user = await services.get_user(async_session=session, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.close()
    created_personal_data = await services.create_user_personal_data(
        async_session=session, user_id=user_id, personal_data=personal_data
    )
    await session.close()
    return created_personal_data


@app.get("/users/{user_id}/personal_data/", response_model=UserPersonalData)
async def get_personal_data(
    user_id: int,
):
    """Gets a user personal data by ID"""
    logger.info(f"Getting {user_id} personal data")
    session = async_session()
    db_personal_user = await services.get_personal_data_by_user_id(async_session=session, user_id=user_id)
    await session.close()
    return db_personal_user
