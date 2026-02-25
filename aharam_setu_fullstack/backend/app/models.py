from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Role(str, Enum):
    provider = "provider"
    ngo = "ngo"
    admin = "admin"


class DonationStatus(str, Enum):
    posted = "Posted"
    ngo_accepted = "NGO Accepted"
    pickup_started = "Pickup Started"
    food_collected = "Food Collected"
    delivered = "Delivered"


class UserCreate(BaseModel):
    name: str
    email: str
    role: Role


class User(BaseModel):
    userId: str
    name: str
    email: str
    role: Role


class DonationCreate(BaseModel):
    foodType: str
    quantity: float = Field(gt=0)
    category: str
    freshnessTime: datetime
    pickupLocation: str
    availableFrom: datetime
    availableTo: datetime
    imageUrl: str | None = None
    isVeg: bool = True


class Donation(BaseModel):
    donationId: str
    providerId: str
    foodType: str
    quantity: float
    category: str
    freshnessTime: datetime
    pickupLocation: str
    imageUrl: str | None
    status: DonationStatus
    assignedNgo: str | None
    volunteerName: str | None
    createdAt: datetime
    updatedAt: datetime
    availableFrom: datetime
    availableTo: datetime
    isVeg: bool


class DonationStatusUpdate(BaseModel):
    status: DonationStatus
    volunteerName: str | None = None


class ImpactMetric(BaseModel):
    mealsServed: int
    foodSavedKg: float
    ngosActive: int
    responseTime: float
