from __future__ import annotations
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, Integer, BigInteger, Index, func, select, update
from datetime import datetime

# MariaDB/MySQL
user = os.getenv("DB_USER", "appuser")
pwd  = os.getenv("DB_PASSWORD", "apppass")
host = os.getenv("DB_HOST", "db")
port = os.getenv("DB_PORT", "3306")
db   = os.getenv("DB_DATABASE", "archive_tgbot")
DATABASE_URL = f"mysql+aiomysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4"

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "0") == "1",
    pool_size=10,
    max_overflow=10,
    pool_recycle=1800,
)
Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase): pass

class Doc(Base):
    __tablename__ = "docs"
    doc_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    target: Mapped[str] = mapped_column(Text, nullable=False)
    state:  Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    msg_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    flag:   Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    title:  Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now(), nullable=True)

    __table_args__ = (
        Index("idx_state", "state"),
        Index("idx_created_at", "created_at"),
        Index("idx_msg_id", "msg_id"),
        Index("idx_title", "title"),
    )

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)