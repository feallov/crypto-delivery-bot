import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, BigInteger, String, Float, Integer, Boolean, select

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True)
    lang = Column(String, default='en')

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    symbol = Column(String)
    target_price = Column(Float)
    direction = Column(String)
    spam_count = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

async def get_user(user_id):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(user_id=user_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

async def add_alert(user_id, symbol, target, direction, spam):
    async with async_session() as session:
        new_alert = Alert(user_id=user_id, symbol=symbol, target_price=target, direction=direction, spam_count=spam)
        session.add(new_alert)
        await session.commit()

async def get_active_alerts():
    async with async_session() as session:
        res = await session.execute(select(Alert).where(Alert.is_active == True))
        return res.scalars().all()

async def deactivate_alert(alert_id):
    async with async_session() as session:
        alert = await session.get(Alert, alert_id)
        if alert:
            alert.is_active = False
            await session.commit()

async def update_user(user_id, **kwargs):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            for k, v in kwargs.items(): setattr(user, k, v)
            await session.commit()
