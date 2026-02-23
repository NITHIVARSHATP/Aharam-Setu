import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "aharamsetu.db"

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score REAL DEFAULT 0.5
            );

            CREATE TABLE IF NOT EXISTS ngos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                lat REAL NOT NULL,
                lng REAL NOT NULL,
                accept_rate REAL NOT NULL,
                avg_response_minutes REAL NOT NULL,
                past_pickups INTEGER NOT NULL,
                recent_activity_count INTEGER NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS rescues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id INTEGER NOT NULL,
                meals_available INTEGER NOT NULL,
                food_type TEXT NOT NULL,
                ready_time TEXT NOT NULL,
                pickup_deadline TEXT NOT NULL,
                expiry_time TEXT NOT NULL,
                lat REAL NOT NULL,
                lng REAL NOT NULL,
                event_type TEXT NOT NULL,
                cause_tag TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'live',
                assigned_ngo_id INTEGER,
                assigned_at TEXT,
                FOREIGN KEY(provider_id) REFERENCES providers(id),
                FOREIGN KEY(assigned_ngo_id) REFERENCES ngos(id)
            );

            CREATE TABLE IF NOT EXISTS rescue_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rescue_id INTEGER NOT NULL,
                ngo_id INTEGER,
                accepted INTEGER NOT NULL,
                response_minutes REAL,
                pickup_minutes REAL,
                distance_km REAL,
                time_band TEXT,
                day_of_week INTEGER,
                cause_tag TEXT,
                expiry_accuracy_score REAL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(rescue_id) REFERENCES rescues(id),
                FOREIGN KEY(ngo_id) REFERENCES ngos(id)
            );

            CREATE TABLE IF NOT EXISTS rescue_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rescue_id INTEGER NOT NULL,
                ngo_id INTEGER NOT NULL,
                wave INTEGER NOT NULL,
                notified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                response_status TEXT NOT NULL DEFAULT 'pending',
                responded_at TEXT,
                response_minutes REAL,
                UNIQUE(rescue_id, ngo_id),
                FOREIGN KEY(rescue_id) REFERENCES rescues(id),
                FOREIGN KEY(ngo_id) REFERENCES ngos(id)
            );
            """
        )


def seed_data() -> None:
    with get_conn() as conn:
        provider_count = conn.execute("SELECT COUNT(*) FROM providers").fetchone()[0]
        ngo_count = conn.execute("SELECT COUNT(*) FROM ngos").fetchone()[0]
        if provider_count == 0:
            conn.executemany(
                "INSERT INTO providers(name, score) VALUES (?, ?)",
                [
                    ("Grand Palace Hall", 0.7),
                    ("Sunrise Caterers", 0.65),
                ],
            )
        if ngo_count == 0:
            conn.executemany(
                """
                INSERT INTO ngos(name, lat, lng, accept_rate, avg_response_minutes, past_pickups, recent_activity_count, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    ("Hope Meals Foundation", 13.0827, 80.2707, 0.86, 8.0, 220, 6, 1),
                    ("City Food Rescue", 13.0500, 80.2120, 0.74, 11.0, 145, 4, 1),
                    ("No Hunger Volunteers", 13.1200, 80.2500, 0.69, 14.0, 101, 3, 1),
                    ("Rapid Relief Network", 13.0000, 80.3000, 0.81, 9.0, 165, 5, 1),
                    ("Community Kitchen Crew", 13.1600, 80.2900, 0.58, 18.0, 88, 2, 1),
                    ("People First NGO", 13.0700, 80.3300, 0.77, 10.0, 133, 4, 1),
                ],
            )
