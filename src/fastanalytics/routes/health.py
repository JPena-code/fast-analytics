# mypy: disable-error-code=no-untyped-def

from fastapi import Request


def health_check(request: Request):
    """Health check endpoint for the API."""
    # TODO: Implement a proper health check that can retrieve
    # the status of the database and the usage of the service itself.
    request.state.logger.debug("Call of the health check")
    return {"status": "ok", "message": "All working fine"}
