from __future__ import annotations

from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt

from .ml import NGOFeatureRow, predict_acceptance

def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))
    return r * c


def reliability_score(accept_rate: float, avg_response_minutes: float, past_pickups: int) -> float:
    return accept_rate * (1.0 / max(avg_response_minutes, 1e-6)) * (1 + (past_pickups / 100.0))


def _elapsed_minutes(created_at_text: str) -> float:
    created = datetime.fromisoformat(created_at_text.replace("Z", "+00:00"))
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    return max((now - created).total_seconds() / 60.0, 0.0)


def wave_from_elapsed(elapsed_minutes: float) -> int:
    if elapsed_minutes < 5:
        return 1
    if elapsed_minutes < 10:
        return 2
    return 3


def pick_notified_candidates(sorted_candidates: list[dict], elapsed_minutes: float) -> tuple[int, list[dict]]:
    wave = wave_from_elapsed(elapsed_minutes)
    if wave == 1:
        return wave, sorted_candidates[:5]
    if wave == 2:
        return wave, sorted_candidates[:10]
    return wave, sorted_candidates


def rank_ngos_for_rescue(rescue: dict, ngos: list[dict], radius_km: float = 15.0) -> tuple[int, list[dict]]:
    created_at = rescue["created_at"]
    elapsed = _elapsed_minutes(created_at)

    candidates = []
    feature_rows = []
    current_time = datetime.now()
    time_of_day = current_time.hour
    day_of_week = current_time.weekday()

    for ngo in ngos:
        if ngo["active"] != 1:
            continue
        distance = haversine_km(rescue["lat"], rescue["lng"], ngo["lat"], ngo["lng"])
        if distance > radius_km:
            continue
        rel = reliability_score(ngo["accept_rate"], ngo["avg_response_minutes"], ngo["past_pickups"])
        feature_rows.append(
            NGOFeatureRow(
                distance_km=distance,
                time_of_day=time_of_day,
                day_of_week=day_of_week,
                ngo_accept_rate=ngo["accept_rate"],
                ngo_avg_response_time=ngo["avg_response_minutes"],
                past_pickups=ngo["past_pickups"],
                recent_activity_count=ngo["recent_activity_count"],
                is_active=ngo["active"],
                ngo_reliability_score=rel,
            )
        )
        candidates.append({"ngo": ngo, "distance_km": distance, "reliability": rel})

    probabilities = predict_acceptance(feature_rows)

    ranked = []
    for candidate, probability in zip(candidates, probabilities):
        ngo = candidate["ngo"]
        distance = candidate["distance_km"]
        speed_score = 1.0 / max(distance + ngo["avg_response_minutes"] / 10.0, 0.1)
        reliability_norm = min(candidate["reliability"] * 2.5, 1.0)
        final_score = 0.5 * probability + 0.3 * speed_score + 0.2 * reliability_norm
        ranked.append(
            {
                "ngo_id": ngo["id"],
                "ngo_name": ngo["name"],
                "distance_km": round(distance, 2),
                "acceptance_probability": round(float(probability), 4),
                "speed_score": round(float(speed_score), 4),
                "reliability_score": round(float(reliability_norm), 4),
                "final_score": round(float(final_score), 4),
            }
        )

    ranked.sort(key=lambda item: item["final_score"], reverse=True)
    wave, notified = pick_notified_candidates(ranked, elapsed)
    return wave, notified
