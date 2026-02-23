from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

CauseTag = Literal[
    "overestimated_attendance",
    "guest_no_show",
    "weather_issue",
    "buffer_cooking_policy",
    "unknown",
]


RescueStatus = Literal["live", "assigned", "accepted", "on_the_way", "picked_up", "completed", "closed"]

PickupStatus = Literal["accepted", "on_the_way", "picked_up", "completed"]


class NGOCreate(BaseModel):
    name: str
    lat: float
    lng: float
    accept_rate: float = Field(ge=0, le=1)
    avg_response_minutes: float = Field(gt=0)
    past_pickups: int = Field(ge=0)
    recent_activity_count: int = Field(ge=0)


class ProviderCreate(BaseModel):
    name: str


class RescueCreate(BaseModel):
    provider_id: int
    meals_available: int = Field(gt=0)
    food_type: str
    ready_time: datetime
    pickup_deadline: datetime
    expiry_time: datetime
    lat: float
    lng: float
    event_type: str
    cause_tag: CauseTag


class PickupStatusUpdate(BaseModel):
    status: PickupStatus


class RescueRankedNGO(BaseModel):
    ngo_id: int
    ngo_name: str
    distance_km: float
    acceptance_probability: float
    speed_score: float
    reliability_score: float
    final_score: float


class RescueRankingResponse(BaseModel):
    rescue_id: int
    alert_wave: int
    ngos_notified: list[RescueRankedNGO]


class AcceptResponse(BaseModel):
    assigned: bool
    message: str
