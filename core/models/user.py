from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


# модель данных для таблицы пользователей
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
