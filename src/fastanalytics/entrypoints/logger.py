import json
import logging
import logging.config
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from typing_extensions import override

from .. import _LOGGER_NAME

LOG_RECORD_BUILTIN_ATTRS = {
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "fastanalytics.entrypoints.logger.JsonFormatter",
            "fmt_json": {
                "level": "levelname",
                "logger": "name",
                "file_name": "filename",
                "function": "funcName",
                "line": "lineno",
                "thread": "threadName",
                "process_name": "processName",
                "process_id": "process",
            },
        },
        "standard": {
            "()": "uvicorn.logging.DefaultFormatter",
            "use_colors": True,
            "format": "%(levelprefix)s[%(name)s|%(process)s] - %(message)s",
        },
    },
    "handlers": {
        "console-standard": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stderr",
        },
        "console-json": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        _LOGGER_NAME: {
            "handlers": ["console-json"],
            "propagate": False,
        },
        "sqlalchemy": {"handlers": ["console-json"], "propagate": False},
    },
}


class JsonFormatter(logging.Formatter):
    def __init__(
        self,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        fmt_json: dict[str, str] | None = None,
    ):
        super().__init__(datefmt=datefmt, style=style)
        self._fmt_json = {}
        for key, value in (fmt_json or {}).items():
            if value not in LOG_RECORD_BUILTIN_ATTRS:
                raise ValueError(f"LogRecord has no attribute '{value}'")
            self._fmt_json[key] = value
        self._fmt_json = fmt_json if fmt_json else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        dict_record = self.__prepare_record(record)
        return json.dumps(dict_record, default=str)

    def __prepare_record(self, record: logging.LogRecord) -> dict[Any, Any]:
        _record = record.__dict__
        created = datetime.fromtimestamp(record.created, timezone.utc)
        dict_record = {
            "level": record.levelname,
            "timestamp": created.isoformat()
            if not self.datefmt
            else created.strftime(self.datefmt),
            "msg": record.getMessage(),
        }
        if record.exc_info:
            dict_record["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            dict_record["stack"] = self.formatStack(record.stack_info)

        for key, value in self._fmt_json.items():
            dict_record[key] = _record.get(value, "Attr not found")

        if extra := _record.get("request", None):
            dict_record["request"] = extra
        if extra := _record.get("response", None):
            dict_record["response"] = extra
        if extra := _record.get("sql_query", None):
            dict_record["sql_query"] = extra

        return dict_record


def setup_logger(log_level: str, logger_config: Path | None = None) -> None:
    if logger_config is not None:
        assert logger_config.exists(), "The logger json file does not exists"
        logging.config.fileConfig(logger_config)
    else:
        logging.config.dictConfig(LOGGING_CONFIG)
    logging.getLogger(_LOGGER_NAME).setLevel(log_level)
