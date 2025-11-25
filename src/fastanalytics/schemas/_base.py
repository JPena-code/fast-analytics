from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

_CONFIG_MODEL: ConfigDict = {
    "extra": "forbid",
    "alias_generator": AliasGenerator(serialization_alias=to_camel),
}


class Base(BaseModel):
    """Base model with configuration class"""

    model_config = _CONFIG_MODEL

    @classmethod
    def field_by_alias(cls, field_alias: str) -> str | None:
        """Get a field by its alias name, if not found return None"""
        for field_name, field_info in cls.model_fields.items():
            if field_info.serialization_alias == field_alias:
                return field_name
        return None

    @classmethod
    def numeric_fields(cls) -> list[str]:
        """Get a list of numeric fields in the model"""
        return [
            field_name
            for field_name, field_info in cls.model_fields.items()
            if field_info.annotation in {int, float}
        ]
