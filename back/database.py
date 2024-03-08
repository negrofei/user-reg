"""
Conexión a la base de datos de usuarios
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
    AsyncAttrs,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from credentials import user, host, db, pwd


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def engine_to_database() -> AsyncEngine:
    """
    Armamos el objeto engine que se comunica con la base de datos
    """
    try:
        engine = create_async_engine(
            f"mysql+aiomysql://{user}:{pwd}@{host}/{db}", echo=True
        )
        return engine
    except Exception as e:
        raise


async def setup_database(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# async def get_async_session(engine: AsyncEngine):
#     session = AsyncSession(engine)
#     session.begin()
#     try:
#         yield session
#     except Exception:
#         session.rollback()
#         raise
#     finally:
#         await session.close()

# engine = engine_to_database()
        
engine = create_async_engine(
            f"mysql+aiomysql://{user}:{pwd}@{host}/{db}", echo=True
        )

# MySessionAsync = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

MySessionAsync = AsyncSession(engine)

async def drop_all_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        result = await conn.execute(text("SHOW TABLES"))
        tables = result.fetchall()
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for table in tables:
            table_name = table[0]
            await conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
