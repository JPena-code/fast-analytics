from datetime import timedelta
from typing import TYPE_CHECKING

from pydantic.alias_generators import to_snake
from sqlalchemy import MetaData, Table

from . import statements as sql
from .schemas import HyperParams

if TYPE_CHECKING:
    from ...models import BaseTable


def extract_model_hyper_params(model: "type[BaseTable]") -> "HyperParams":
    time_interval = getattr(model, "__time_interval__", None)
    if time_interval is None:
        raise ValueError("Model must define a __time_interval__ attribute")
    if isinstance(time_interval, str):
        time_interval = time_interval.strip().upper()
        if not time_interval.startswith("INTERVAL "):
            raise ValueError(
                f"Invalid time interval format: {time_interval}. Must start with 'INTERVAL '"
            )
        time_interval = time_interval.replace("INTERVAL ", "", 1).strip()
    if isinstance(time_interval, timedelta):
        time_interval = int(time_interval.microseconds)

    table_name = orm_table_name(model)

    return HyperParams.model_validate(
        {
            "table_name": table_name,
            "time_column": getattr(model, "__time_column__", None),
            "chunk_time_interval": time_interval,
            "if_not_exists": True,
            "migrate_data": True,
        }
    )


def orm_table_name(model: "type[BaseTable]") -> "str":
    metadata = getattr(
        model,
        "__table__",
        Table(
            to_snake(model.__name__),
            MetaData(
                schema="public",
            ),
            schema="public",
        ),
    )

    table_name = getattr(model, "__tablename__", to_snake(model.__name__))
    if metadata.schema:
        table_name = f"{metadata.schema}.{table_name}"
    return table_name


def hypertable_sql(params: HyperParams) -> "str":
    query = None
    if isinstance(params.chunk_time_interval, str):
        query = sql.CREATE_HYPERTABLE_INTERVAL
    elif isinstance(params.chunk_time_interval, int):
        query = sql.CREATE_HYPERTABLE_INTEGER
    else:
        raise ValueError(
            f"Invalid interval type for hypertable, got {type(params.chunk_time_interval).__name__}"
        )
    return str(
        query.bindparams(**params.model_dump()).compile(
            compile_kwargs={
                "literal_binds": True,
            }
        )
    )
