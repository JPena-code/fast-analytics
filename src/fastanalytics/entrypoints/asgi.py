# mypy: disable-error-code=arg-type

from typing import Any

from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware

from ..middleware import LoggerMiddleware
from ..routes import router


def create_app(**kwargs: dict[str, Any]) -> FastAPI:
    app = FastAPI(**kwargs)  # pyright: ignore[reportArgumentType]

    app.add_middleware(LoggerMiddleware)
    app.add_middleware(GZipMiddleware, compresslevel=7, minimum_size=700)

    app.include_router(
        router,
    )
    return app
