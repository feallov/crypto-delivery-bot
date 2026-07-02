import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, BigInteger, String, JSON

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True)
    lang = Column(String, default='en')
    alerts_enabled = Column(JSON, default=True)

# Форматирование ссылки
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    # Добавляем параметры для стабильности, если их нет
    if "?ssl" not in DATABASE_URL:
        DATABASE_URL += "?ssl=require"

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession) if engine else None

async def init_db():
    if engine:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("--- DATABASE CONNECTED ---")
        except Exception as e:
            print(f"DATABASE ERROR: {e}")

async def get_user(user_id):
    if not async_session: return type('User', (), {'lang': 'en'})()
    try:
        async with async_session() as session:
            user = await session.get(User, user_id)
            if not user:
                user = User(user_id=user_id)
                session.add(user)
                await session.commit()
                await session.refresh(user)
            return user
    except:
        return type('User', (), {'lang': 'en'})()

async def update_user(user_id, **kwargs):
    if not async_session: return
    try:
        async with async_session() as session:
            user = await session.get(User, user_id)
            if user:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                await session.commit()
    except: pass
