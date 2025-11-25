from collections.abc import Sequence
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Generic, TypeVar

from fastapi import Request
from pydantic import BaseModel, Field, NonNegativeInt, model_validator

from ._base import Base
from .queries import Page, PageMetaData

_TModel = TypeVar("_TModel", bound=BaseModel)
_ExcludedStatus = Annotated["StatusEnum", Field(exclude=True)]
_ExcludedMessage = Annotated[str, Field(exclude=True)]
_ExcludedRequest = Annotated[Request, Field(exclude=True)]
_ExcludedNonNegativeInt = Annotated[NonNegativeInt, Field(exclude=True)]


class StatusEnum(str, Enum):
    success = "success"
    error = "error"


class MetaData(Base):
    status: StatusEnum
    message: str
    pagination: PageMetaData | None = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now().astimezone(timezone.utc).isoformat()
    )


class _Envelope(Base, arbitrary_types_allowed=True, validate_by_name=True):
    metadata: MetaData | None = Field(default=None, init=False)
    request: _ExcludedRequest
    status: _ExcludedStatus
    message: _ExcludedMessage
    # TODO: Define an schema of error details to return to clients
    errors: list[dict[str, str]] | None = None


class Response(_Envelope, Generic[_TModel]):
    """Generic response model for API responses"""

    result: _TModel | None = None

    @model_validator(mode="after")
    def validate_meta(self) -> "Response[_TModel]":
        self.metadata = MetaData(status=self.status, message=self.message)
        return self


class ResponsePage(_Envelope, Generic[_TModel]):
    """Generic response model for API responses with pagination"""

    results: Sequence[_TModel] | None = None
    total_records: _ExcludedNonNegativeInt = Field(default=0)
    page: Annotated[Page, Field(exclude=True)]

    @model_validator(mode="after")
    def validate_meta(self) -> "ResponsePage[_TModel]":
        total_pages = (self.total_records // self.page.page_size) + (
            1 if self.total_records % self.page.page_size > 0 else 0
        )
        self.metadata = MetaData(
            status=self.status,
            message=self.message,
            pagination=PageMetaData(
                total_records=self.total_records,
                page=self.page.page,
                total_pages=total_pages,
                page_size=self.page.page_size,
            ),
        )
        return self
