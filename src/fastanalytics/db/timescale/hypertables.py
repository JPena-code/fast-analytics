from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from ...models import BaseTable
from . import statements as sql
from .schemas import HyperTableSchema
from .utils import extract_model_hyper_params, hypertable_sql

if TYPE_CHECKING:
    import logging


def sync_hypertables(logger: "logging.Logger", conn: Connection) -> None:
    """Synchronize all tables associated with a model to be an hypertable in the database"""
    models = [
        model
        for model in BaseTable.__subclasses__()
        if getattr(model, "__table__", None) is not None
    ]
    logger.debug("Found %d models to check for hypertables", len(models))
    current_tables = {table.hypertable_name for table in hypertables(conn)}
    models = [
        model for model in models if getattr(model, "__tablename__", None) not in current_tables
    ]
    if not models:
        logger.debug("No new models to create hypertables for")
        return
    logger.info(
        'Creating hypertables for models "%s"', ",".join(model.__name__ for model in models)
    )
    for model in models:
        logger.debug("Creating hypertable for model %s", model.__name__)
        try:
            create_hypertable(conn, model)
        except SQLAlchemyError as e_sql:
            logger.error(
                "Could not create hypertable for model %s (%s) (%s) (%s)",
                model.__name__,
                type(e_sql).__name__,
                e_sql.code,
                e_sql._message(),
            )
            raise e_sql


def create_hypertable(conn: Connection, model: type[BaseTable]) -> None:
    """Create a hypertable for a given model, the associated table must exists in the database."""
    if model is None:
        raise ValueError("Model is required, cannot be None")
    if getattr(model, "__table__", None) is None:
        raise ValueError(f"Model {type(model).__name__} does not have been instantiated as a table")
    params = extract_model_hyper_params(model)
    statement = hypertable_sql(params)
    conn.execute(text(statement))


def hypertables(conn: Connection) -> list[HyperTableSchema]:
    """Fetch all the hypertables in the database"""
    tables = [
        HyperTableSchema.model_validate(table._asdict())
        for table in conn.execute(sql.AVAILABLE_HYPERTABLES).all()
    ]
    return tables
