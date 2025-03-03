from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from core.models import User
from .schemas import *

# Настройка хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Функция для получения пользователя по имени
async def get_user(db: AsyncSession, username: str) -> User:
    stmt = select(User).filter(User.username == username)
    result: Result = await db.execute(stmt)
    user = result.scalars().first()
    return user


async def get_all_users(db: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.id)
    result: Result = await db.execute(stmt)
    users = result.scalars().all()
    return list(users)


# Функция для создания пользователя
async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, password_hash=hashed_password, role="user")
    db.add(db_user)
    await db.commit()
    # await db.refresh(db_user)
    return db_user


# Функция для проверки пароля
def verify_password(plain_password: str, hashed_password: str) -> True | False:
    return pwd_context.verify(plain_password, hashed_password)


# Функция для смены роли пользователя
async def change_user_role(
    db: AsyncSession, username: str, new_role: str
) -> User | None:
    db_user = await get_user(db, username)
    if not db_user:
        return None
    db_user.role = new_role
    await db.commit()
    await db.refresh(db_user)
    return db_user


# Функция для удаления пользователя
async def user_delete(db: AsyncSession, username: str) -> User | None:
    db_user = await get_user(db, username)
    if not db_user:
        return None
    await db.delete(db_user)
    await db.commit()
    return db_user


# Функция для изменения пароля пользователя
async def change_user_password(
    db: AsyncSession, username: str, new_password: str
) -> User | None:
    db_user = await get_user(db, username)
    if not db_user:
        return None
    db_user.password = pwd_context.hash(new_password)
    await db.commit()
    await db.refresh(db_user)
    return db_user
