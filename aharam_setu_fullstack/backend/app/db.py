from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from .models import Donation, DonationStatus, ImpactMetric, User


class InMemoryDB:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.donations: dict[str, Donation] = {}
        self.impact = ImpactMetric(mealsServed=0, foodSavedKg=0, ngosActive=0, responseTime=0)

    def create_user(self, user: User) -> User:
        self.users[user.userId] = user
        return user

    def add_donation(self, payload: dict) -> Donation:
        now = datetime.utcnow()
        donation = Donation(
            donationId=str(uuid4()),
            providerId=payload["providerId"],
            foodType=payload["foodType"],
            quantity=payload["quantity"],
            category=payload["category"],
            freshnessTime=payload["freshnessTime"],
            pickupLocation=payload["pickupLocation"],
            imageUrl=payload.get("imageUrl"),
            status=DonationStatus.posted,
            assignedNgo=None,
            volunteerName=None,
            createdAt=now,
            updatedAt=now,
            availableFrom=payload["availableFrom"],
            availableTo=payload["availableTo"],
            isVeg=payload["isVeg"],
        )
        self.donations[donation.donationId] = donation
        return donation


db = InMemoryDB()


# -----------------------------
# Optional Firestore integration
# -----------------------------
# Replace InMemoryDB with this adapter when deploying on Firebase/Google Cloud.
# import firebase_admin
# from firebase_admin import credentials, firestore
# cred = credentials.Certificate("service-account.json")
# firebase_admin.initialize_app(cred)
# fs = firestore.client()
#
# collections:
# - donations
# - users
# - impactMetrics
