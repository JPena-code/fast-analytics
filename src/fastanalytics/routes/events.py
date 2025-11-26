# mypy: disable-error-code=no-untyped-def

from typing import TYPE_CHECKING

from fastapi import HTTPException, Request, status
from fastapi.routing import APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import col, func, select

from ..db import approximate_row_count
from ..db.timescale.functions import time_bucket
from ..depends import PageQuery, PageQueryAgg, Session
from ..models import Event, is_numeric
from ..schemas import (
    EventAggregate,
    EventCreate,
    EventSchema,
    Page,
    Response,
    ResponsePage,
    StatusEnum,
)

if TYPE_CHECKING:
    from typing import Any

    from sqlalchemy.sql import SQLColumnExpression

router = APIRouter(tags=["events"])


@router.get(
    "",
    response_model_by_alias=True,
    response_model_exclude_none=True,
    response_model=ResponsePage[EventSchema],
)
def read_events(request: Request, session: Session, page: PageQuery):
    limit = page.page_size
    offset = (page.page - 1) * limit
    query = select(Event).limit(limit).offset(offset)
    try:
        events = session.exec(query).all()
        aprox_size = session.exec(select(approximate_row_count(Event))).one()
    except SQLAlchemyError as e_sql:
        request.state.logger.error(
            "Datase error fetching events (Type=%s) (Msg=%s)",
            type(e_sql).__name__,
            e_sql._message(),
            extra={
                "sql_query": query.compile(
                    bind=session.bind, compile_kwargs={"literal_binds": True}
                )
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponsePage(
                status=StatusEnum.error,
                message="Internal server error",
                total_records=0,
                page=Page.model_validate(page.model_dump()),
            ).model_dump(exclude_none=True, exclude_unset=True),
        ) from None
    return ResponsePage(
        results=events,
        status=StatusEnum.success,
        message="Successfully retrieved the model #Events",
        total_records=aprox_size,
        # TODO: passing the actual page query object gives a
        # pydantic validation error indicating that the field is not
        # a valid Page instance
        page=Page.model_validate(page.model_dump()),
    )


@router.get(
    "/aggregate/{field}",
    status_code=status.HTTP_200_OK,
    response_model_by_alias=True,
    response_model_exclude_none=True,
    response_model=ResponsePage[EventAggregate],
)
def agg_events(
    request: Request,
    session: Session,
    field: str,
    page: PageQueryAgg,
):
    field_name = EventSchema.field_by_alias(field)
    if not field_name:
        request.state.logger.warning("Invalid field for avg aggregation %s", field)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponsePage(
                status=StatusEnum.error,
                message=f"Invalid field for aggregation: {field}",
                page=Page.model_validate(page, from_attributes=True),
            ).model_dump(exclude_none=True, exclude_unset=True),
        )
    if is_numeric(Event, field_name):
        request.state.logger.warning("Numeric field for aggregation %s", field)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponsePage(
                status=StatusEnum.error,
                message="It is only allowed to aggregate non-numeric fields",
                page=Page.model_validate(page.model_dump()),
            ).model_dump(exclude_none=True, exclude_unset=True),
        )
    col_field = col(getattr(Event, field_name))
    limit = page.page_size
    offset = (page.page - 1) * limit

    bucket_interval = time_bucket(page.interval, col(Event.time)).label("interval")
    columns: list[SQLColumnExpression[Any]] = [
        bucket_interval,
        col_field.label("field"),
        func.count(col_field).label("count"),
    ]
    for agg in page.func:
        if agg == "avg":
            columns.append(func.avg(Event.duration).label("avg_duration"))
        elif agg == "min":
            columns.append(func.min(Event.duration).label("min_duration"))
        elif agg == "max":
            columns.append(func.max(Event.duration).label("max_duration"))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ResponsePage(
                    status=StatusEnum.error,
                    message=f"Unknow aggregation function {agg}",
                    page=Page.model_validate(page.model_dump()),
                ).model_dump(exclude_none=True, exclude_unset=True),
            )
    query = select(*columns).group_by(bucket_interval, col_field)
    try:
        # Intentionally use the execute method marked as deprecated
        # due to the SQLmodel sessions exec method convert the results
        # into tuples that cannot be interpreted as pydantic models
        results = session.execute(query).all()
        paged_results = [
            EventAggregate(**result._asdict()) for result in results[offset : limit * page.page]
        ]
    except SQLAlchemyError as e_sql:
        request.state.logger.error(
            "Datase error fetching event aggregates (Type=%s) (Msg=%s)",
            type(e_sql).__name__,
            e_sql._message(),
            extra={
                "sql_query": query.compile(
                    bind=session.bind, compile_kwargs={"literal_binds": True}
                )
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponsePage(
                status=StatusEnum.error,
                message="Internal server error",
                page=Page.model_validate(page.model_dump()),
            ).model_dump(exclude_none=True, exclude_unset=True),
        ) from None
    return ResponsePage(
        status=StatusEnum.success,
        message=f"Aggregated #Event.{field}",
        results=paged_results,
        total_records=len(results),
        page=Page.model_validate(page.model_dump()),
    )


@router.get(
    "/{event_id}",
    status_code=status.HTTP_200_OK,
    response_model_by_alias=True,
    response_model_exclude_none=True,
    response_model=Response[EventSchema],
)
def find_event(request: Request, session: Session, event_id: int):
    event = session.exec(select(Event).where(Event.id == event_id)).first()
    if not event:
        request.state.logger.warning("Event with id %s not found", event_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Response(
                status=StatusEnum.error,
                message=f"Event with id {event_id} not found",
            ),
        )
    return Response(
        result=event,
        status=StatusEnum.success,
        message="Processed successfully",
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Response[EventSchema],
    response_model_by_alias=True,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    name="Create single event",
)
def create_event(request: Request, session: Session, payload: EventCreate):
    raw_obj = payload.model_dump()
    raw_obj["referrer"] = str(raw_obj["referrer"]) if raw_obj["referrer"] else None
    db_obj = Event.model_validate(raw_obj)
    try:
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
    except SQLAlchemyError as e_sql:
        session.rollback()
        request.state.logger.exception(
            # TODO: Add a correlational middleware to have a request ID
            "Database error: processing request ...",
            # request.headers.get(constants.REQ_ID_HEADER),
            exc_info=e_sql,
        )
        raise HTTPException(
            status_code=500,
            detail=Response(
                status=StatusEnum.error,
                message="Internal server error",
            ).model_dump(exclude_none=True, exclude_unset=True),
        ) from None
    return Response(
        result=db_obj,
        status=StatusEnum.success,
        message="Event created successfully",
    )
