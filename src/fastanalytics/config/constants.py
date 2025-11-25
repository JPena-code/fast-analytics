from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal

REQ_ID_HEADER: 'Literal["X-Request-ID"]' = "X-Request-ID"
RES_TIME_ELAPSE: 'Literal["X-Elapsed-Time"]' = "X-Elapsed-Time"
