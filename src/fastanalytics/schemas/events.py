import uuid
from datetime import datetime
from typing import Annotated, Any

from pydantic import AnyHttpUrl, Field, IPvAnyAddress, NonNegativeFloat
from pydantic.types import StringConstraints

from .._types import Page
from ..utils import get_utc_now
from ._base import Base


class EventAggregate(Base):
    field: Any
    interval: datetime
    count: int
    avg_duration: NonNegativeFloat | None = None
    min_duration: NonNegativeFloat | None = None
    max_duration: NonNegativeFloat | None = None


class EventCreate(Base):
    """Schema for the creation of a new event. i.e. POST /events"""

    page: Page = Field(examples=["/hone", "/products"])
    agent: Annotated[str, StringConstraints(min_length=10)]
    ip_address: IPvAnyAddress
    referrer: Annotated[AnyHttpUrl | None, Field(None)] = None
    session_id: uuid.UUID
    duration: NonNegativeFloat = 0


class Event(EventCreate):
    """Schema for the event model. i.e. GET /events/{id}"""

    id: int
    time: datetime = Field(default_factory=get_utc_now)
