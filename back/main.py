"""
Main
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from schemas import UserCreate, UserBase, User, UserPersonalData
import services

from pydantic import EmailStr

# asyncio.run(services.initialize_db(from_scratch=False))

app = FastAPI(
    title="prueba",
    description="API para el registro de usuarios",
)


@app.post("/users/", response_model=UserBase)
async def create_user_api(
    user: UserCreate, 
    db: AsyncSession = Depends(services.get_async_session)
):
    db_user = await services.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400, detail="woops the email is in use"
        )
    created_user = await services.create_user(db=db, user=user)
    return created_user


@app.get("/users/{user_email}", response_model=User)
async def get_user_by_email_api(
    user_email: EmailStr,
    db: AsyncSession = Depends(services.get_async_session),
):
    db_user = await services.get_user_by_email(db=db, email=user_email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/{user_id}/personal_data/", response_model=UserPersonalData)
async def create_personal_data(
    user_id: int,
    personal_data: UserPersonalData,
    db: AsyncSession = Depends(services.get_async_session),
):
    db_user = await services.get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    created_personal_data = await services.create_user_personal_data(
        db=db, user_id=user_id, personal_data=personal_data
    )
    return created_personal_data