from typing import Annotated

from fastapi import Depends, Query
from sqlmodel import Session as SqlSession

from .db import get_session
from .schemas import Page
from .schemas.queries import PageAggregate

Session = Annotated[SqlSession, Depends(get_session)]

PageQuery = Annotated[Page, Query()]
PageQueryAgg = Annotated[
    PageAggregate,
    Query(description="Pagination with aggregation over a time interval"),
]
