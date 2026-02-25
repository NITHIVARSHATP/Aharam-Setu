from __future__ import annotations

from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .auth import get_current_user, require_role
from .db import db
from .models import DonationCreate, DonationStatus, DonationStatusUpdate, Role, User, UserCreate

app = FastAPI(title="Aharam Setu - Food Bridge API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATUS_FLOW = {
    DonationStatus.posted: DonationStatus.ngo_accepted,
    DonationStatus.ngo_accepted: DonationStatus.pickup_started,
    DonationStatus.pickup_started: DonationStatus.food_collected,
    DonationStatus.food_collected: DonationStatus.delivered,
}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "message": "Every meal shared saves a life."}


@app.post("/auth/register")
def register(payload: UserCreate) -> User:
    user = User(userId=f"usr_{len(db.users) + 1}", name=payload.name, email=payload.email, role=payload.role)
    return db.create_user(user)


@app.post("/provider/donations")
def create_donation(payload: DonationCreate, user: User = Depends(get_current_user)) -> dict:
    require_role(user, Role.provider)
    donation = db.add_donation({**payload.model_dump(), "providerId": user.userId})
    return {
        "message": "Donation posted successfully. Your kindness can feed many.",
        "donation": donation,
    }


@app.get("/provider/donations/me")
def provider_donations(user: User = Depends(get_current_user)) -> list[dict]:
    require_role(user, Role.provider)
    result = [item.model_dump() for item in db.donations.values() if item.providerId == user.userId]
    return result


@app.get("/ngo/donations/live")
def ngo_live_donations(user: User = Depends(get_current_user)) -> list[dict]:
    require_role(user, Role.ngo)
    return [
        item.model_dump()
        for item in db.donations.values()
        if item.status in {
            DonationStatus.posted,
            DonationStatus.ngo_accepted,
            DonationStatus.pickup_started,
            DonationStatus.food_collected,
        }
    ]


@app.post("/ngo/donations/{donation_id}/accept")
def ngo_accept(donation_id: str, user: User = Depends(get_current_user)) -> dict:
    require_role(user, Role.ngo)
    donation = db.donations.get(donation_id)
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if donation.status != DonationStatus.posted:
        raise HTTPException(status_code=400, detail="Donation is no longer open")
    donation.status = DonationStatus.ngo_accepted
    donation.assignedNgo = user.userId
    donation.updatedAt = datetime.utcnow()
    db.impact.ngosActive = len({d.assignedNgo for d in db.donations.values() if d.assignedNgo})
    return {"message": "Donation accepted. Rescue in progress.", "donation": donation}


@app.patch("/ngo/donations/{donation_id}/status")
def ngo_update_status(donation_id: str, payload: DonationStatusUpdate, user: User = Depends(get_current_user)) -> dict:
    require_role(user, Role.ngo)
    donation = db.donations.get(donation_id)
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if donation.assignedNgo != user.userId:
        raise HTTPException(status_code=403, detail="Only assigned NGO can update this donation")

    expected = STATUS_FLOW.get(donation.status)
    if payload.status != expected:
        raise HTTPException(status_code=400, detail=f"Invalid transition. Next allowed: {expected}")

    donation.status = payload.status
    donation.volunteerName = payload.volunteerName or donation.volunteerName
    donation.updatedAt = datetime.utcnow()

    if donation.status == DonationStatus.delivered:
        db.impact.foodSavedKg += donation.quantity
        db.impact.mealsServed += int(donation.quantity * 2)

    return {"message": "Status updated", "donation": donation}


@app.get("/ngo/analytics/me")
def ngo_analytics(user: User = Depends(get_current_user)) -> dict:
    require_role(user, Role.ngo)
    items = [d for d in db.donations.values() if d.assignedNgo == user.userId]
    delivered = [d for d in items if d.status == DonationStatus.delivered]
    return {
        "totalRescued": round(sum(d.quantity for d in delivered), 2),
        "mealsServed": sum(int(d.quantity * 2) for d in delivered),
        "responseSpeed": "Starter metric",
        "motivation": "Your service brings dignity, nutrition, and hope.",
    }


@app.get("/admin/overview")
def admin_overview(user: User = Depends(get_current_user)) -> dict:
    require_role(user, Role.admin)
    ngo_perf: dict[str, int] = {}
    for donation in db.donations.values():
        if donation.assignedNgo:
            ngo_perf[donation.assignedNgo] = ngo_perf.get(donation.assignedNgo, 0) + 1

    return {
        "donations": len(db.donations),
        "users": len(db.users),
        "impact": db.impact.model_dump(),
        "ngoPerformance": ngo_perf,
    }


@app.patch("/admin/donations/{donation_id}/reassign/{ngo_user_id}")
def admin_reassign(donation_id: str, ngo_user_id: str, user: User = Depends(get_current_user)) -> dict:
    require_role(user, Role.admin)
    donation = db.donations.get(donation_id)
    ngo_user = db.users.get(ngo_user_id)
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if not ngo_user or ngo_user.role != Role.ngo:
        raise HTTPException(status_code=404, detail="NGO user not found")

    donation.assignedNgo = ngo_user_id
    if donation.status == DonationStatus.posted:
        donation.status = DonationStatus.ngo_accepted
    donation.updatedAt = datetime.utcnow()
    return {"message": "Reassigned to NGO", "donation": donation}


@app.get("/impact/summary")
def impact_summary() -> dict:
    return {
        "impactMetrics": db.impact.model_dump(),
        "banner": "Together we bridge food to those who need it most.",
    }
