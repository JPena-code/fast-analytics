# mypy: ignore-errors
import uuid
from typing import Annotated

from pydantic import IPvAnyAddress, NonNegativeFloat, StringConstraints
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import INET, TEXT
from sqlmodel import Field, Uuid, desc

from .._types import Page
from .base import BaseHyperModel


class Event(BaseHyperModel, table=True):
    __tablename__ = "events"  # type: ignore[assignment]

    page: Page = Field(sa_type=TEXT)
    agent: Annotated[str, StringConstraints(min_length=10)] = Field(sa_type=TEXT)
    ip_address: IPvAnyAddress = Field(
        sa_type=INET,
    )
    referrer: str | None = Field(sa_type=TEXT, nullable=True)
    session_id: uuid.UUID = Field(sa_type=Uuid)
    duration: NonNegativeFloat = 0


Index("page_time_desc", Event.page, desc(Event.time))
