from typing import Annotated, Literal

from pydantic import ConfigDict, Field, NonNegativeInt, PositiveInt
from pydantic.alias_generators import to_camel, to_snake

from ._base import Base

PageLimit = Annotated[PositiveInt, Field(ge=1, le=1000)]
PageOffset = Annotated[PositiveInt, Field(default=1)]
AggFunction = Literal["avg", "min", "max"]


class Page(Base):
    model_config = ConfigDict(
        alias_generator=to_snake,
        title="Pagination Query",
        extra="ignore",
        validate_by_name=True,
    )

    page_size: PageLimit = 500
    page: PageOffset = 1


class PageAggregate(Page):
    model_config = ConfigDict(str_to_lower=True)

    interval: str = Field(
        default="1 hour",
        description="Aggregation interval used for grouping over time",
        pattern=r"^\d+\s+(second|seconds|minute|minutes|hour|hours|day|days|week|weeks|month|months|year|years)$",
    )
    func: list[AggFunction] = Field(
        default=["avg"],
        description="List of aggregation functions to apply over the interval",
        min_length=1,
        examples=[["avg"], ["min", "count", "max"]],
    )


class PageMetaData(Page):
    model_config = ConfigDict(
        title="Pagination Meta Data",
        alias_generator=to_camel,
        extra="forbid",
    )

    total_records: NonNegativeInt
    total_pages: NonNegativeInt
