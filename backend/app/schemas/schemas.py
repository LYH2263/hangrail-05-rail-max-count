from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

# NULL 表示不限制件数；配置时必须为正整数
OptionalMaxItems = Annotated[int | None, Field(default=None, ge=1)]


class StoreOut(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class RailOut(BaseModel):
    id: int
    store_id: int
    label: str
    length_cm: float
    max_items: int | None = None
    active_count: int = 0
    model_config = {"from_attributes": True}


class RailUpdate(BaseModel):
    max_items: OptionalMaxItems = None


class OrderOut(BaseModel):
    id: int
    store_id: int
    ticket_code: str
    garment_name: str
    length_cm: float
    status: str
    due_at: datetime
    hung_at: datetime | None
    model_config = {"from_attributes": True}


class HangRequest(BaseModel):
    order_id: int
    rail_id: int | None = None


class PickupRequest(BaseModel):
    ticket_code: str


class OccupancySeg(BaseModel):
    order_id: int
    ticket_code: str
    garment_name: str
    start_cm: float
    end_cm: float


class OccupancyOut(BaseModel):
    rail_id: int
    label: str
    length_cm: float
    max_items: int | None = None
    active_count: int = 0
    segments: list[OccupancySeg]
