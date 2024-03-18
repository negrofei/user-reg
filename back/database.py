"""
Conexión a la base de datos de usuarios
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    AsyncAttrs,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from credentials import user, host, db, pwd


class Base(AsyncAttrs, DeclarativeBase):
    pass



async def setup_database(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


engine = create_async_engine(f"mysql+aiomysql://{user}:{pwd}@{host}/{db}", echo=True)

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
