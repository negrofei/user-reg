"""
Conexión a la base de datos de usuarios
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncAttrs,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from credentials_test import user, host, db, pwd


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


async def drop_all_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        result = await conn.execute(text("SHOW TABLES"))
        tables = result.fetchall()
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for table in tables:
            table_name = table[0]
            await conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))


engine = create_async_engine(
            f"mysql+aiomysql://{user}:{pwd}@{host}/{db}", echo=True
        )

if __name__ == "__main__":
    async def initialize_db(from_scratch=True):
        if from_scratch:
            await drop_all_tables(engine)
            await setup_database(engine)
        await engine.dispose()
    import asyncio
    asyncio.run(initialize_db(from_scratch=True))