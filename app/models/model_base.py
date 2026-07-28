from datetime import datetime

from sqlalchemy import Column, Integer, Float
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    __abstract__ = True
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class BareBaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    # NOTE: defaults must be callables so SQLAlchemy evaluates them per row at
    # INSERT/UPDATE time. Using ``datetime.now().timestamp`` (a bound method
    # captured at import time) would stamp every row with the process start time
    # and never update ``updated_at``.
    created_at = Column(Float, default=lambda: datetime.now().timestamp())
    updated_at = Column(
        Float,
        default=lambda: datetime.now().timestamp(),
        onupdate=lambda: datetime.now().timestamp(),
    )
