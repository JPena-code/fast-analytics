from typing import TYPE_CHECKING

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from .. import get_logger
from ..config import environ
from .activator import activate_ext
from .engine import create_engine
from .timescale.functions import approximate_row_count, time_bucket
from .timescale.hypertables import sync_hypertables

if TYPE_CHECKING:
    from collections.abc import Generator

    from sqlalchemy import Engine


__all__ = [
    "activate_ext",
    "sync_hypertables",
    "time_bucket",
    "approximate_row_count",
    "init_engine",
]


def init_engine() -> "Engine":
    """Initialize the database connection and the related setup
    In a lifespan cycle for the application

    Return: `sqlalchemy.Engine`
    """
    logger = get_logger()
    logger.info("Creating SQL engine using timezone %s", environ.timezone)
    engine = create_engine()
    with engine.begin() as conn:
        try:
            logger.debug('Creating extensions in database ["timescaledb", "uuid-ossp"]')
            activate_ext(conn, "timescaledb")
            activate_ext(conn, "uuid-ossp")
        except SQLAlchemyError as e_sql:
            logger.error(
                "SQL Error encounter init_db (%s) (%d) (%s)",
                type(e_sql).__name__,
                e_sql.code,
                e_sql._message(),
            )
            raise e_sql
        except:
            logger.exception("Unexpected error encounter init_db")
            raise
    return engine


def get_session() -> "Generator[Session, None, None]":
    """Get the a new session connected to the database"""
    # TODO: should we use a sessionmaker here?
    with Session(create_engine()) as session:
        yield session
