from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlmodel import SQLModel


def is_numeric(model: "type[SQLModel]", field_name: str) -> bool:
    field_info = model.model_fields.get(field_name)
    if field_info is not None:
        return field_info.annotation in {int, float}
    return False
