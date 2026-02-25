"""
Aharam Setu - Home Dashboard
Smart Food Rescue System for faster and reliable food redistribution.
"""

import streamlit as st

from core import get_ngo_master_data, init_session_state

st.set_page_config(page_title="Aharam Setu", page_icon="🍱", layout="wide")
init_session_state()

st.title("🍱 Aharam Setu")
st.caption("Smart Food Rescue System for faster and reliable food redistribution.")

# --------------------------------------------------
# QUICK STATS
# --------------------------------------------------
left, middle, right = st.columns(3)

left.metric("Registered NGOs", len(get_ngo_master_data()))
middle.metric("Completed Rescues", len(st.session_state.completed_rescues))
right.metric("Interaction Records", len(st.session_state.history_df))

# --------------------------------------------------
# WORKFLOW OVERVIEW
# --------------------------------------------------
with st.container(border=True):
    st.markdown("### 🌍 Humanitarian Workflow")
    st.markdown(
        "1. **Food Provider** submits food details and location on the Food Provider Dashboard.\n"
        "2. **System ranks** top 3 NGOs based on distance + historical acceptance behavior.\n"
        "3. **NGO team** updates live pickup status (Accept → On Way → Picked Up → Completed).\n"
        "4. **Admin** monitors model performance and retrains based on feedback."
    )

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------
with st.container(border=True):
    st.markdown("### 🧭 Navigate to Pages")
    st.info(
        "**Use the left sidebar** to open:\n\n"
        "- **Food Provider Dashboard** — Submit food & location, find matching NGOs\n"
        "- **NGO Dashboard** — View ranked NGOs, update status, track rescues\n"
        "- **Admin Panel** — Monitor model accuracy, retrain, view logs"
    )

# --------------------------------------------------
# RECENT ACTIVITY
# --------------------------------------------------
st.divider()
st.subheader("📊 System Status")

col_status1, col_status2, col_status3 = st.columns(3)

with col_status1:
    model_trained = st.session_state.model_accuracy > 0
    st.metric(
        "Model Status",
        "✅ Trained" if model_trained else "⏳ Pending",
        help="Model training requires 5+ interaction records"
    )

with col_status2:
    acceptance_rate = (
        (st.session_state.history_df["accepted"].sum() / len(st.session_state.history_df) * 100)
        if len(st.session_state.history_df) > 0
        else 0
    )
    st.metric(
        "Acceptance Rate",
        f"{acceptance_rate:.1f}%" if acceptance_rate > 0 else "No data",
        help="% of rescues accepted by NGOs"
    )

with col_status3:
    avg_distance = (
        st.session_state.history_df["distance"].mean()
        if len(st.session_state.history_df) > 0
        else 0
    )
    st.metric(
        "Avg Distance",
        f"{avg_distance:.1f} km" if avg_distance > 0 else "No data",
        help="Average distance to ranked NGOs"
    )

# --------------------------------------------------
# KEY FEATURES
# --------------------------------------------------
st.divider()
st.subheader("✨ Key Features")

feat_col1, feat_col2, feat_col3 = st.columns(3)

with feat_col1:
    st.markdown(
        "#### 🗺️ Interactive Map\n"
        "Click to select pickup location or use browser geolocation."
    )

with feat_col2:
    st.markdown(
        "#### 🤖 ML-Based Ranking\n"
        "RandomForest model learns from feedback to improve predictions."
    )

with feat_col3:
    st.markdown(
        "#### 📱 Live Status Tracking\n"
        "Track NGO pickup status in real-time."
    )

st.divider()
st.caption("💡 **Tip:** Start by going to **Food Provider Dashboard** to submit a food rescue request.")
