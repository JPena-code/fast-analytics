# mypy : disable-erro-code=arg-type
from typing import TYPE_CHECKING

import pytz
from sqlmodel import func, text

from .utils import orm_table_name

if TYPE_CHECKING:
    from datetime import datetime
    from typing import Any

    from sqlalchemy.orm import Mapped
    from sqlalchemy.sql.functions import Function

    from ...models.base import BaseHyperModel


def approximate_row_count(model: "type[BaseHyperModel]") -> "Function[int]":
    table_name = orm_table_name(model)
    return func.approximate_row_count(table_name)


def time_bucket(
    width: str,
    column: "Mapped[Any]",
    timezone: "datetime | None" = None,
    origin: str | None = None,
    offset: str | None = None,
) -> "Function[datetime]":
    bucket_width = text(f"'{width}'::INTERVAL")
    args: list[Any] = [bucket_width, column]
    if timezone:
        args.append(timezone)
    if origin:
        try:
            pytz.timezone(origin)
        except pytz.UnknownTimeZoneError as e_tz:
            raise ValueError("Incorrect timezone provided", timezone) from e_tz
        args.append(origin)
    if offset:
        args.append(text(f"'{offset}'::INTERVAL"))
    return func.time_bucket(*args)
