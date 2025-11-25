from datetime import timedelta
from typing import Annotated

from pydantic import StringConstraints

Page = Annotated[str, StringConstraints(pattern=r"^/.*$")]
TPartitionInterval = str | int | timedelta
