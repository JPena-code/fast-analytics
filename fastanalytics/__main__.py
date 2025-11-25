import uvicorn

from . import __version__, get_logger
from .config import environ
from .entrypoints import init_app

logger = get_logger()
app = init_app(  # type: ignore [no-untyped-call]
    title="Web page events navigation",
    description="API to retrieve the analytics capture for an page",
    version=__version__,
    debug=environ.environment == "dev",
)


def main() -> None:
    logger.info("Starting application for environment %s", environ.environment)
    logger.info(
        "Starting Uvicorn server application at %s:%d",
        environ.app.host,
        environ.app.port,
    )
    uvicorn.run(
        "fastanalytics.__main__:app",
        host=environ.app.host,
        port=environ.app.port,
        server_header=environ.environment == "dev",
        access_log=False,
        reload=environ.environment == "dev",
        log_config=None,
    )
    logger.info("Server application finished")


if __name__ == "__main__":
    main()  # type: ignore [no-untyped-call]
