from __future__ import annotations

from datetime import datetime

import pandas as pd
from fastapi import FastAPI, HTTPException

from .database import get_conn, init_db, seed_data
from .ml import retrain_from_frame, train_initial_model
from .schemas import (
    AcceptResponse,
    NGOCreate,
    PickupStatusUpdate,
    ProviderCreate,
    RescueCreate,
    RescueRankingResponse,
)
from .services import haversine_km, rank_ngos_for_rescue

app = FastAPI(title="Aharam Setu API", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_data()
    train_initial_model()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/providers")
def create_provider(payload: ProviderCreate) -> dict:
    with get_conn() as conn:
        cursor = conn.execute("INSERT INTO providers(name, score) VALUES (?, ?)", (payload.name, 0.5))
        return {"id": cursor.lastrowid, "name": payload.name}


@app.get("/providers")
def list_providers() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name, score FROM providers ORDER BY id").fetchall()
        return [dict(row) for row in rows]


@app.post("/ngos")
def create_ngo(payload: NGOCreate) -> dict:
    with get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT INTO ngos(name, lat, lng, accept_rate, avg_response_minutes, past_pickups, recent_activity_count, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                payload.name,
                payload.lat,
                payload.lng,
                payload.accept_rate,
                payload.avg_response_minutes,
                payload.past_pickups,
                payload.recent_activity_count,
            ),
        )
        return {"id": cursor.lastrowid, "name": payload.name}


@app.get("/ngos")
def list_ngos() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM ngos ORDER BY id").fetchall()
        return [dict(row) for row in rows]


@app.post("/rescues")
def create_rescue(payload: RescueCreate) -> dict:
    if payload.expiry_time <= payload.ready_time:
        raise HTTPException(status_code=400, detail="expiry_time must be greater than ready_time")
    with get_conn() as conn:
        provider = conn.execute("SELECT id FROM providers WHERE id = ?", (payload.provider_id,)).fetchone()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        cursor = conn.execute(
            """
            INSERT INTO rescues(
                provider_id, meals_available, food_type, ready_time, pickup_deadline, expiry_time,
                lat, lng, event_type, cause_tag, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'live')
            """,
            (
                payload.provider_id,
                payload.meals_available,
                payload.food_type,
                payload.ready_time.isoformat(),
                payload.pickup_deadline.isoformat(),
                payload.expiry_time.isoformat(),
                payload.lat,
                payload.lng,
                payload.event_type,
                payload.cause_tag,
            ),
        )
        return {"rescue_id": cursor.lastrowid, "status": "live"}


@app.get("/rescues/live")
def list_live_rescues() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT r.*, p.name AS provider_name, n.name AS assigned_ngo_name
            FROM rescues r
            JOIN providers p ON p.id = r.provider_id
            LEFT JOIN ngos n ON n.id = r.assigned_ngo_id
            WHERE r.status IN ('live', 'assigned', 'accepted', 'on_the_way', 'picked_up')
            ORDER BY r.id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


@app.get("/rescues/{rescue_id}/ranking", response_model=RescueRankingResponse)
def get_rescue_ranking(rescue_id: int) -> RescueRankingResponse:
    with get_conn() as conn:
        rescue_row = conn.execute("SELECT * FROM rescues WHERE id = ?", (rescue_id,)).fetchone()
        if not rescue_row:
            raise HTTPException(status_code=404, detail="Rescue not found")
        rescue = dict(rescue_row)
        ngos = [dict(row) for row in conn.execute("SELECT * FROM ngos").fetchall()]

    if rescue["status"] == "completed":
        raise HTTPException(status_code=400, detail="Rescue already completed")

    wave, ranked = rank_ngos_for_rescue(rescue, ngos)
    return RescueRankingResponse(rescue_id=rescue_id, alert_wave=wave, ngos_notified=ranked)


@app.post("/rescues/{rescue_id}/accept/{ngo_id}", response_model=AcceptResponse)
def accept_rescue(rescue_id: int, ngo_id: int) -> AcceptResponse:
    with get_conn() as conn:
        ngo = conn.execute("SELECT id FROM ngos WHERE id = ?", (ngo_id,)).fetchone()
        if not ngo:
            raise HTTPException(status_code=404, detail="NGO not found")

        conn.execute("BEGIN IMMEDIATE")
        rescue = conn.execute("SELECT * FROM rescues WHERE id = ?", (rescue_id,)).fetchone()
        if not rescue:
            raise HTTPException(status_code=404, detail="Rescue not found")

        if rescue["assigned_ngo_id"] is not None:
            assigned_name_row = conn.execute("SELECT name FROM ngos WHERE id = ?", (rescue["assigned_ngo_id"],)).fetchone()
            assigned_name = assigned_name_row["name"] if assigned_name_row else "another NGO"
            return AcceptResponse(assigned=False, message=f"Already assigned to {assigned_name}")

        conn.execute(
            """
            UPDATE rescues
            SET assigned_ngo_id = ?, assigned_at = ?, status = 'accepted'
            WHERE id = ? AND assigned_ngo_id IS NULL
            """,
            (ngo_id, datetime.utcnow().isoformat(), rescue_id),
        )
        conn.execute(
            "INSERT INTO rescue_logs(rescue_id, ngo_id, accepted, response_minutes, cause_tag) VALUES (?, ?, ?, ?, ?)",
            (rescue_id, ngo_id, 1, 0.0, rescue["cause_tag"]),
        )
        return AcceptResponse(assigned=True, message="Assignment locked")


@app.patch("/rescues/{rescue_id}/status")
def update_pickup_status(rescue_id: int, payload: PickupStatusUpdate) -> dict:
    with get_conn() as conn:
        rescue = conn.execute("SELECT * FROM rescues WHERE id = ?", (rescue_id,)).fetchone()
        if not rescue:
            raise HTTPException(status_code=404, detail="Rescue not found")

        if rescue["assigned_ngo_id"] is None:
            raise HTTPException(status_code=400, detail="Rescue not assigned")

        new_status = payload.status
        conn.execute("UPDATE rescues SET status = ? WHERE id = ?", (new_status, rescue_id))

        if new_status == "completed":
            created_at = datetime.fromisoformat(rescue["created_at"].replace("Z", "+00:00"))
            now = datetime.utcnow()
            pickup_minutes = max((now - created_at.replace(tzinfo=None)).total_seconds() / 60.0, 0.0)
            distance = None
            ngo = conn.execute("SELECT lat, lng FROM ngos WHERE id = ?", (rescue["assigned_ngo_id"],)).fetchone()
            if ngo:
                distance = haversine_km(rescue["lat"], rescue["lng"], ngo["lat"], ngo["lng"])

            conn.execute(
                """
                INSERT INTO rescue_logs(
                    rescue_id, ngo_id, accepted, response_minutes, pickup_minutes,
                    distance_km, time_band, day_of_week, cause_tag, expiry_accuracy_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rescue_id,
                    rescue["assigned_ngo_id"],
                    1,
                    0.0,
                    pickup_minutes,
                    distance,
                    str(created_at.hour),
                    created_at.weekday(),
                    rescue["cause_tag"],
                    0.9,
                ),
            )

            provider_score = compute_provider_score(
                reporting_timeliness=0.85,
                expiry_accuracy=0.9,
                handover_readiness=0.88,
                data_completeness=1.0,
            )
            conn.execute("UPDATE providers SET score = ? WHERE id = ?", (provider_score, rescue["provider_id"]))

        return {"rescue_id": rescue_id, "status": new_status}


@app.get("/admin/provider-scores")
def provider_scores() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name, score FROM providers ORDER BY score DESC").fetchall()
        return [dict(row) for row in rows]


@app.post("/admin/retrain")
def retrain_model() -> dict:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
              COALESCE(distance_km, 8.0) AS distance_km,
              CAST(COALESCE(time_band, '12') AS INTEGER) AS time_of_day,
              COALESCE(day_of_week, 2) AS day_of_week,
              COALESCE(n.accept_rate, 0.6) AS ngo_accept_rate,
              COALESCE(n.avg_response_minutes, 12.0) AS ngo_avg_response_time,
              COALESCE(n.past_pickups, 50) AS past_pickups,
              COALESCE(n.recent_activity_count, 2) AS recent_activity_count,
              COALESCE(n.active, 1) AS is_active,
              (COALESCE(n.accept_rate, 0.6) * (1.0 / COALESCE(n.avg_response_minutes, 12.0)) * (1 + COALESCE(n.past_pickups, 50)/100.0)) AS ngo_reliability_score,
              accepted
            FROM rescue_logs l
            LEFT JOIN ngos n ON n.id = l.ngo_id
            """
        ).fetchall()

    frame = pd.DataFrame([dict(r) for r in rows])
    result = retrain_from_frame(frame)
    return result


def compute_provider_score(
    reporting_timeliness: float,
    expiry_accuracy: float,
    handover_readiness: float,
    data_completeness: float,
) -> float:
    score = (
        0.3 * reporting_timeliness
        + 0.3 * expiry_accuracy
        + 0.2 * handover_readiness
        + 0.2 * data_completeness
    )
    return round(min(max(score, 0.0), 1.0), 4)
