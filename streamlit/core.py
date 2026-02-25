"""
Aharam Setu - Core Module
Shared functions and data for the Smart Food Rescue System.
"""

import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# --------------------------------------------------
# NGO MASTER DATA
# --------------------------------------------------
def get_ngo_master_data():
    """Return master NGO database."""
    return pd.DataFrame({
        "ngo_id": [1, 2, 3, 4, 5],
        "ngo_name": [
            "Helping Hands",
            "Food Bank",
            "Annai Trust",
            "Care Givers",
            "Hope Foundation"
        ],
        "latitude": [11.0168, 11.0250, 11.0120, 11.0300, 11.0050],
        "longitude": [76.9558, 76.9600, 76.9400, 76.9500, 76.9700],
        "accept_rate": [0.85, 0.70, 0.65, 0.90, 0.60],
        "avg_response_time": [8, 12, 10, 6, 15]
    })


# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------
def init_session_state():
    """Initialize all session state variables."""
    
    if "history_df" not in st.session_state:
        st.session_state.history_df = pd.DataFrame(
            columns=["distance", "accept_rate", "avg_response_time", "accepted"]
        )
    
    if "model" not in st.session_state:
        st.session_state.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
    
    if "provider_lat" not in st.session_state:
        st.session_state.provider_lat = None
    
    if "provider_lon" not in st.session_state:
        st.session_state.provider_lon = None
    
    if "top3" not in st.session_state:
        st.session_state.top3 = None
    
    if "food_details" not in st.session_state:
        st.session_state.food_details = {
            "food_type": "",
            "num_meals": 0,
            "ready_time": "",
            "expiry_time": "",
            "event_type": "",
            "cause_tag": ""
        }
    
    if "ngo_status" not in st.session_state:
        st.session_state.ngo_status = {}
    
    if "completed_rescues" not in st.session_state:
        st.session_state.completed_rescues = []
    
    if "model_accuracy" not in st.session_state:
        st.session_state.model_accuracy = 0.0
    
    if "rejected_ngo_ids" not in st.session_state:
        st.session_state.rejected_ngo_ids = []


# --------------------------------------------------
# DISTANCE CALCULATION
# --------------------------------------------------
def calculate_distance(p_lat, p_lon, n_lat, n_lon):
    """Calculate geodesic distance between two coordinates in km."""
    return geodesic((p_lat, p_lon), (n_lat, n_lon)).km


# --------------------------------------------------
# MODEL TRAINING
# --------------------------------------------------
def train_model():
    """Train RandomForest model on historical acceptance data."""
    
    if len(st.session_state.history_df) >= 5:
        df = st.session_state.history_df.copy()
        df = df.dropna()
        df["accepted"] = df["accepted"].astype(int)
        
        X = df[["distance", "accept_rate", "avg_response_time"]]
        y = df["accepted"]
        
        if len(y.unique()) > 1:
            st.session_state.model.fit(X, y)
            
            accuracy = st.session_state.model.score(X, y)
            st.session_state.model_accuracy = round(accuracy, 3)
            
            return True
    
    return False


# --------------------------------------------------
# NGO RANKING
# --------------------------------------------------
def rank_ngos(p_lat, p_lon):
    """Rank NGOs based on distance and acceptance behavior."""
    
    ngo_df = get_ngo_master_data()
    features = []
    distances = []
    
    for _, row in ngo_df.iterrows():
        dist = calculate_distance(
            p_lat, p_lon,
            row["latitude"], row["longitude"]
        )
        distances.append(dist)
        
        features.append([
            dist,
            row["accept_rate"],
            row["avg_response_time"]
        ])
    
    feature_df = pd.DataFrame(
        features,
        columns=["distance", "accept_rate", "avg_response_time"]
    )
    
    # Use ML if trained, else fallback heuristic
    if len(st.session_state.history_df) >= 5 and \
       len(st.session_state.history_df["accepted"].unique()) > 1:
        probs = st.session_state.model.predict_proba(feature_df)[:, 1]
    else:
        # Distance-based fallback: closer = higher probability
        probs = 1 / (feature_df["distance"] + 1)
    
    result = ngo_df.copy()
    result["distance"] = distances
    result["predicted_probability"] = probs
    
    return result.sort_values(
        by="predicted_probability",
        ascending=False
    )


# --------------------------------------------------
# RELIABILITY SCORE
# --------------------------------------------------
def compute_reliability_score(ngo_row):
    """
    Compute a 0-100 reliability score for an NGO.
    Factors: acceptance rate (50%), response time (30%), distance (20%).
    """
    accept_score = ngo_row["accept_rate"] * 100 * 0.5
    
    response_score = max(0, 100 - ngo_row["avg_response_time"] * 5) * 0.3
    
    distance_score = max(0, 50 - ngo_row["distance"] * 2) * 0.2
    
    return round(accept_score + response_score + distance_score, 1)


# --------------------------------------------------
# LOG RESCUE COMPLETION
# --------------------------------------------------
def log_rescue_completion(ngo_name, food_type, num_meals):
    """Log a completed rescue to session state."""
    rescue_log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ngo_name": ngo_name,
        "food_type": food_type,
        "num_meals": num_meals,
        "distance_km": st.session_state.provider_lat is not None
    }
    st.session_state.completed_rescues.append(rescue_log)
