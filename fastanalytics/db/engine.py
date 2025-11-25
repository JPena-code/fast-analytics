from functools import cache, wraps
from typing import TYPE_CHECKING, cast

import sqlmodel

from ..config import environ

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import ParamSpec

    from sqlalchemy.engine import Engine

    PEngine = ParamSpec("PEngine")


def _create_engine(
    func: "Callable[PEngine, Engine]",
    timezone: str = "UTC",
) -> "Callable[PEngine, Engine]":
    @wraps(func)
    def wrapper(*args: "PEngine.args", **kwargs: "PEngine.kwargs") -> "Engine":
        conn_args: dict[str, str] = cast("dict[str, str]", kwargs.get("connect_args", {}))
        conn_args["options"] = f"-c timezone={timezone}"
        return func(*args, **kwargs)

    return wrapper


@cache
def create_engine() -> "Engine":
    creator = _create_engine(sqlmodel.create_engine, environ.timezone)
    return creator(
        url=environ.pg_dsn.encoded_string(),
        future=True,
        echo=True,
        pool_size=100,
        pool_recycle=3600,
        pool_timeout=30,
    )
