from datetime import datetime, timezone
from typing import ClassVar

from pydantic import field_validator
from sqlmodel import DateTime, Field, SQLModel

from ..utils import get_utc_now

SCHEMA = "analytics"


class BaseHyperModel(SQLModel):
    __abstract__: ClassVar[bool] = True
    __time_column__: ClassVar = "time"
    __time_interval__: ClassVar = "INTERVAL 7 days"
    # TODO: add compression settings from timescaledb
    # and retention policies
    # __drop_after__: ClassVar = "INTERVAL 3 months"

    __table_args__ = {"schema": SCHEMA}

    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"autoincrement": True},
        nullable=False,
    )
    time: datetime = Field(
        default_factory=get_utc_now,
        nullable=False,
        sa_type=DateTime(timezone=True),  # type: ignore
        primary_key=True,
    )

    @field_validator("time", mode="after")
    @classmethod
    def has_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            value = value.replace(tzinfo=timezone.utc)
        return value
