from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        rescue_id = cursor.lastrowid
        rescue_row = conn.execute("SELECT * FROM rescues WHERE id = ?", (rescue_id,)).fetchone()
        ngos = [dict(row) for row in conn.execute("SELECT * FROM ngos").fetchall()]
        if rescue_row:
            dispatch_alerts(conn, dict(rescue_row), ngos)
        return {"rescue_id": rescue_id, "status": "live"}


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
    with get_conn() as conn:
        dispatch_alerts(conn, rescue, ngos)
    return RescueRankingResponse(rescue_id=rescue_id, alert_wave=wave, ngos_notified=ranked)


@app.get("/ngos/{ngo_id}/jobs")
def ngo_jobs(ngo_id: int) -> list[dict]:
    with get_conn() as conn:
        ngo = conn.execute("SELECT id FROM ngos WHERE id = ?", (ngo_id,)).fetchone()
        if not ngo:
            raise HTTPException(status_code=404, detail="NGO not found")

        rows = conn.execute(
            """
            SELECT
                a.rescue_id,
                a.wave,
                a.notified_at,
                a.response_status,
                a.response_minutes,
                r.status AS rescue_status,
                r.meals_available,
                r.food_type,
                r.event_type,
                p.name AS provider_name
            FROM rescue_alerts a
            JOIN rescues r ON r.id = a.rescue_id
            JOIN providers p ON p.id = r.provider_id
            WHERE a.ngo_id = ?
              AND r.status IN ('live', 'assigned', 'accepted', 'on_the_way', 'picked_up', 'completed')
            ORDER BY a.notified_at DESC
            """,
            (ngo_id,),
        ).fetchall()
        return [dict(row) for row in rows]


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

        if rescue["status"] in ("completed", "closed"):
            return AcceptResponse(assigned=False, message="Rescue is already closed")

        alert = conn.execute(
            "SELECT * FROM rescue_alerts WHERE rescue_id = ? AND ngo_id = ?",
            (rescue_id, ngo_id),
        ).fetchone()
        if not alert:
            return AcceptResponse(assigned=False, message="This NGO was not notified for this rescue")

        if rescue["assigned_ngo_id"] is not None:
            assigned_name_row = conn.execute("SELECT name FROM ngos WHERE id = ?", (rescue["assigned_ngo_id"],)).fetchone()
            assigned_name = assigned_name_row["name"] if assigned_name_row else "another NGO"
            return AcceptResponse(assigned=False, message=f"Already assigned to {assigned_name}")

        now_iso = datetime.now(timezone.utc).isoformat()
        response_minutes = elapsed_minutes_between(alert["notified_at"], now_iso)

        conn.execute(
            """
            UPDATE rescues
            SET assigned_ngo_id = ?, assigned_at = ?, status = 'accepted'
            WHERE id = ? AND assigned_ngo_id IS NULL
            """,
            (ngo_id, now_iso, rescue_id),
        )
        conn.execute(
            """
            UPDATE rescue_alerts
            SET response_status = 'accepted', responded_at = ?, response_minutes = ?
            WHERE rescue_id = ? AND ngo_id = ?
            """,
            (now_iso, response_minutes, rescue_id, ngo_id),
        )

        conn.execute(
            """
            UPDATE rescue_alerts
            SET response_status = 'no_response', responded_at = ?,
                response_minutes = (julianday(?) - julianday(notified_at)) * 24.0 * 60.0
            WHERE rescue_id = ?
              AND ngo_id != ?
              AND response_status = 'pending'
            """,
            (now_iso, now_iso, rescue_id, ngo_id),
        )
        conn.execute(
            "INSERT INTO rescue_logs(rescue_id, ngo_id, accepted, response_minutes, cause_tag) VALUES (?, ?, ?, ?, ?)",
            (rescue_id, ngo_id, 1, response_minutes, rescue["cause_tag"]),
        )

        non_selected_rows = conn.execute(
            """
            SELECT ngo_id, response_minutes
            FROM rescue_alerts
            WHERE rescue_id = ? AND ngo_id != ? AND response_status = 'no_response' AND responded_at = ?
            """,
            (rescue_id, ngo_id, now_iso),
        ).fetchall()
        for row in non_selected_rows:
            conn.execute(
                "INSERT INTO rescue_logs(rescue_id, ngo_id, accepted, response_minutes, cause_tag) VALUES (?, ?, ?, ?, ?)",
                (rescue_id, row["ngo_id"], 0, row["response_minutes"], rescue["cause_tag"]),
            )

        conn.execute(
            """
            UPDATE rescues
            SET status = 'assigned'
            WHERE id = ?
            """,
            (rescue_id,),
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
            created_at = parse_dt(rescue["created_at"])
            now = datetime.now(timezone.utc)
            pickup_minutes = max((now - created_at).total_seconds() / 60.0, 0.0)
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
                    str(created_at.astimezone(timezone.utc).hour),
                    created_at.weekday(),
                    rescue["cause_tag"],
                    1.0 if now <= parse_dt(rescue["expiry_time"]) else 0.0,
                ),
            )

            provider_score = compute_provider_score(conn, rescue["provider_id"])
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


def parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def elapsed_minutes_between(start_iso: str, end_iso: str) -> float:
    return max((parse_dt(end_iso) - parse_dt(start_iso)).total_seconds() / 60.0, 0.0)


def dispatch_alerts(conn, rescue: dict, ngos: list[dict]) -> None:
    if rescue["status"] in ("completed", "closed"):
        return

    wave, notified = rank_ngos_for_rescue(rescue, ngos)
    for item in notified:
        conn.execute(
            """
            INSERT OR IGNORE INTO rescue_alerts(rescue_id, ngo_id, wave, response_status)
            VALUES (?, ?, ?, 'pending')
            """,
            (rescue["id"], item["ngo_id"], wave),
        )


def compute_provider_score(conn, provider_id: int) -> float:
    rows = conn.execute(
        """
        SELECT id, created_at, ready_time, pickup_deadline, expiry_time, status, food_type, event_type, cause_tag,
               meals_available, lat, lng
        FROM rescues
        WHERE provider_id = ?
        """,
        (provider_id,),
    ).fetchall()
    rescues = [dict(row) for row in rows]
    if not rescues:
        return 0.5

    completed = [item for item in rescues if item["status"] == "completed"]
    if not completed:
        return 0.5

    timely_count = 0
    handover_ready_count = 0
    expiry_safe_count = 0
    complete_rows = 0

    for rescue in completed:
        created_at = parse_dt(rescue["created_at"])
        ready_time = parse_dt(rescue["ready_time"])
        deadline = parse_dt(rescue["pickup_deadline"])
        expiry_time = parse_dt(rescue["expiry_time"])

        lead_minutes = (ready_time - created_at).total_seconds() / 60.0
        if lead_minutes >= -10:
            timely_count += 1

        assigned_at = conn.execute("SELECT assigned_at FROM rescues WHERE id = ?", (rescue["id"],)).fetchone()
        if assigned_at and assigned_at["assigned_at"]:
            if parse_dt(assigned_at["assigned_at"]) <= deadline:
                handover_ready_count += 1

        pickup_log = conn.execute(
            """
            SELECT created_at FROM rescue_logs
            WHERE rescue_id = ? AND ngo_id IS NOT NULL AND accepted = 1 AND pickup_minutes IS NOT NULL
            ORDER BY id DESC LIMIT 1
            """,
            (rescue["id"],),
        ).fetchone()
        if pickup_log and parse_dt(pickup_log["created_at"]) <= expiry_time:
            expiry_safe_count += 1

        required_fields = [
            rescue["food_type"],
            rescue["event_type"],
            rescue["cause_tag"],
            rescue["meals_available"],
            rescue["lat"],
            rescue["lng"],
        ]
        if all(value is not None and str(value) != "" for value in required_fields):
            complete_rows += 1

    total = len(completed)
    reporting_timeliness = timely_count / total
    handover_readiness = handover_ready_count / total
    expiry_accuracy = expiry_safe_count / total
    data_completeness = complete_rows / total

    score = (
        0.3 * reporting_timeliness
        + 0.3 * expiry_accuracy
        + 0.2 * handover_readiness
        + 0.2 * data_completeness
    )
    return round(min(max(score, 0.0), 1.0), 4)
