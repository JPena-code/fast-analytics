from contextlib import asynccontextmanager

from .. import get_logger
from ..config import environ
from ..db import init_engine
from .asgi import create_app
from .logger import setup_logger

__all__ = [
    "init_app",
]


def init_app(*args, **kwargs):
    logger = get_logger()
    external_span = kwargs.pop("lifespan", None)

    @asynccontextmanager
    async def _span(_app):
        ctx = {"logger": logger}
        engine = init_engine()
        if external_span:
            async with external_span() as ext_ctx:
                ctx.update(ext_ctx)
                yield ctx
        else:
            yield ctx
        logger.info("Shutting down application")
        logger.info("Cleaning SQL Engine")
        engine.dispose()

    setup_logger(environ.log_level)

    logger.info("Constructing ASGI APP")
    kwargs.update(lifespan=_span)
    app = create_app(**kwargs)
    logger.info("App created successfully")

    return app
