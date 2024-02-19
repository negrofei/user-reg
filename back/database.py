"""
Conexión a la base de datos de usuarios
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base

def engine_to_database() -> Engine:
    """
    Armamos el objeto engine que se comunica con la base de datos
    """
    # TODO: Mejorar el tema de las credenciales.
    from credentials import user,  host, db, pwd
    # user = credentials.user
    # host = credentials.host
    # db = credentials.db
    # pwd = credentials.pwd
    engine = create_async_engine('mysql+aiomysql://{user}:{pwd}@{host}/{db}'.format(user=user, pwd=pwd, host=host, db=db))
    return engine

engine = engine_to_database()

Base = declarative_base()

async def get_session():
    # session = Session(bind=engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session = AsyncSession(engine)

    try:
        yield session
    except Exception:
        session.rollback()
    finally:
        await session.close()