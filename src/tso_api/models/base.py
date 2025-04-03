from datetime import datetime
import humps
from pydantic import BaseModel, ConfigDict


def camel(s: str):
    return humps.camelize(s)


class TSOBase(BaseModel):
    model_config = ConfigDict(alias_generator=camel, populate_by_name=True)


class Timestamps(TSOBase):
    created_at: datetime
    updated_at: datetime
