import copy
import uuid
from http import HTTPStatus
from typing import TYPE_CHECKING

from starlette.datastructures import URL, MutableHeaders

from .. import get_logger
from ..config import constants

if TYPE_CHECKING:
    from typing import TypeAlias

    from starlette.types import ASGIApp, Message, Receive, Scope, Send

    THasHeaders: TypeAlias = Scope | Message
    TASGILoggerInfo: TypeAlias = dict[str, str | dict[str, str]]


def _copy_headers(asgi: "THasHeaders") -> dict[str, str]:
    headers = copy.deepcopy(asgi["headers"])
    return {key.decode("latin1"): value.decode("latin1") for key, value in headers}


def _extract_req_info(scope: "Scope") -> "TASGILoggerInfo":
    url = URL(scope=scope)
    return {
        "http": f"{scope['scheme'].upper()}/{scope['http_version']}",
        "method": scope["method"],
        "path": url.path,
        "query": url.query,
        "headers": _copy_headers(scope),
        "client": "{!s}:{!s}".format(*scope["client"]) if scope["client"] else "-:-",
    }


def _extract_res_info(message: "Message") -> "TASGILoggerInfo":
    return {
        "status_code": message["status"],
        "phrase": HTTPStatus(message["status"]).phrase,
        "headers": _copy_headers(message),
    }


class LoggerMiddleware:
    def __init__(self, app: "ASGIApp") -> None:
        self.app = app
        logger = None
        if hasattr(self.app, "state"):
            logger = getattr(app.state, "logger", None)  # type: ignore
        if not logger:
            logger = get_logger()
        self.logger = logger

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        async def logger_send(message: "Message") -> None:
            if message["type"] == "http.response.start":
                extra_info["response"] = _extract_res_info(message)
            await send(message)

        extra_info = {}
        if scope["type"] not in {"http", "https"}:
            return await self.app(scope, receive, send)

        extra_info["request"] = _extract_req_info(scope)
        headers = MutableHeaders(scope=scope)
        if not headers.get(constants.REQ_ID_HEADER):
            headers.update({constants.REQ_ID_HEADER: str(uuid.uuid4())})
        try:
            await self.app(scope, receive, logger_send)
        finally:
            # Here is where the log message goes
            self.logger.info("Trace access ASGI connection", extra=extra_info)
