# app/db.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# we use class as opposed to old Base = declarative_base() due to type hints( new way has type hints)
class Base(DeclarativeBase):
    pass


_engine= None
_session_factory =None


def get_engine():
    """
    Connecting to a database is actually very slow (you have to verify passwords, open network ports, etc.).

    Instead of doing that 100 times for 100 kids, the Engine keeps a "Pool" of connections
    so we establishes the connection pool eg: 10 to be used 

    creates an async singleton engine-created once and reused for rvery request
    """

    global _engine

    if _engine is None:
        db_url = settings.database_url

        _engine = create_async_engine(
            db_url,
            echo=settings.debug,
            pool_size=10,
            max_overflow=20 # allows 20 extra when traffoic spikes
        )
        print('Engine initialized')

    return _engine


def get_session_factory():
    """
    The Session singleton factory 

    when 100 users come the factory spaws 100 helpers with data given like connection pool, on_commit =false 

    create async helpers
    This code is the blueprint for a Robot Factory that creates those helper robots whenever a customer places an order.
    """
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,  # create async helpers 
            expire_on_commit=False,  # Keeps data in memory post-commit
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency:
    Yields a clean database session for 1 request, then closes it automatically.
    usage in a router:
    async def my_route(db: AsyncSession = Depends(get_db)):
    """

    factory = get_session_factory()
    # help py close and open gracefully
    async with factory() as session:
        yield session