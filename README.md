# Aharam Setu (Pattinathil-Pasi)

Smart ML-powered excess food rescue routing system built from the PDF requirements.

## Implemented Workflow

1. Provider creates a live rescue request with surplus details and cause tag.
2. Backend filters NGOs by geo radius (Haversine distance).
3. ML feature builder creates pre-decision features (no leakage).
4. RandomForest predicts NGO acceptance probability.
5. Smart ranking computes final score:
   - `final_score = 0.5*acceptance_probability + 0.3*speed_score + 0.2*reliability_score`
6. Notification waves:
   - first 5 NGOs in first 5 minutes,
   - top 10 in next 5 minutes,
   - all thereafter.
7. First NGO to accept locks assignment server-side.
8. Live pickup status updates (`accepted -> on_the_way -> picked_up -> completed`).
9. Completion logs are stored for continuous learning.
10. Admin can retrain model from logs.
11. Provider fairness score excludes surplus quantity.

## Tech Stack

- Frontend: Streamlit (`dashboard.py`) with Provider / NGO / Admin panels
- Backend: FastAPI (`app/main.py`)
- ML: scikit-learn RandomForest (`app/ml.py`)
- DB: SQLite (local file `aharamsetu.db`, replaceable with PostgreSQL)

## Project Structure

- `app/main.py` - FastAPI backend with all endpoints
- `app/ml.py` - RandomForest model training and inference
- `app/services.py` - Haversine distance, NGO ranking, wave logic
- `app/database.py` - SQLite initialization and seeding
- `app/schemas.py` - Pydantic models
- `dashboard.py` - Streamlit UI with Provider / NGO / Admin tabs
- `aharamsetu.db` - Auto-created SQLite database
- `model.pkl` - Auto-trained model on startup

## Installation & Run

**Terminal 1 – Start API backend:**

```powershell
cd "c:\Users\NITHISHVARAN T P\OneDrive\Pictures\Screenshots\filez\sem 6\innov"
"C:/Users/NITHISHVARAN T P/AppData/Local/Programs/Python/Python313/python.exe" -m uvicorn app.main:app --reload
```

Backend will listen on `http://127.0.0.1:8000`. Visit `http://127.0.0.1:8000/docs` for Swagger API docs.

**Terminal 2 – Start Streamlit dashboard:**

```powershell
cd "c:\Users\NITHISHVARAN T P\OneDrive\Pictures\Screenshots\filez\sem 6\innov"
"C:/Users/NITHISHVARAN T P/AppData/Local/Programs/Python/Python313/python.exe" -m streamlit run dashboard.py
```

Dashboard will open on `http://localhost:8501`.

## Usage

### Provider Dashboard
1. Create a rescue request with meals, location, expiry time, and cause tag.
2. View all live rescues and their ranked NGOs per alert wave.

### NGO Dashboard
1. See rescue jobs available for your organization.
2. Accept a job (first acceptance locks assignment server-side).
3. Update pickup status: `accepted → on_the_way → picked_up → completed`.

### Admin Panel
1. View provider fairness scores (excludes surplus quantity).
2. Retrain ML model from historical logs.
3. See registered NGOs and their reliability metrics.
