"""
Aharam Setu - Page 3: Admin Panel
Monitor model performance, retrain, and view rescue logs.
"""

import streamlit as st
import pandas as pd

from core import init_session_state, train_model

st.set_page_config(page_title="Admin Panel", layout="wide")
init_session_state()

st.title("🛠️ Admin - Model Retraining & Logs")
st.caption("Monitor system health, retrain ML model, and review rescue history.")

# --------------------------------------------------
# SECTION 1: MODEL PERFORMANCE
# --------------------------------------------------
st.subheader("📊 Model Performance Metrics")

col_perf1, col_perf2, col_perf3 = st.columns(3)

with col_perf1:
    st.metric(
        "Acceptance Accuracy",
        f"{st.session_state.model_accuracy * 100:.1f}%",
        delta="Model trained" if st.session_state.model_accuracy > 0 else "Not trained yet"
    )

with col_perf2:
    avg_response = (
        st.session_state.history_df["avg_response_time"].mean()
        if len(st.session_state.history_df) > 0
        else 0
    )
    st.metric(
        "Avg Response Time (Predicted)",
        f"{avg_response:.1f} min" if avg_response > 0 else "-"
    )

with col_perf3:
    total_records = len(st.session_state.history_df)
    st.metric(
        "Interaction Records",
        total_records,
        delta=f"Training samples" if total_records >= 5 else "Need 5+ records"
    )

# --------------------------------------------------
# SECTION 2: MODEL RETRAINING
# --------------------------------------------------
st.divider()
st.subheader("🔄 Retrain Model")

st.info(
    "The model learns from provider feedback (Accept/Reject). "
    "Once you have 5+ interaction records with both accepted and rejected cases, "
    "click **Retrain** to improve ranking accuracy."
)

if st.button("🔄 Retrain Model Now", use_container_width=True, type="primary"):
    if len(st.session_state.history_df) < 5:
        st.error(f"❌ Need at least 5 interaction records. Currently: {len(st.session_state.history_df)}")
    else:
        with st.spinner("🔄 Training model..."):
            success = train_model()
        
        if success:
            st.success(
                f"✅ Model retrained successfully!\n"
                f"Accuracy: {st.session_state.model_accuracy * 100:.1f}%"
            )
        else:
            st.warning("⚠️ Model training incomplete. Need both accepted and rejected cases.")

# --------------------------------------------------
# SECTION 3: INTERACTION HISTORY
# --------------------------------------------------
st.divider()
st.subheader("📚 Interaction History")

if len(st.session_state.history_df) == 0:
    st.info("No interaction records yet. Complete rescues to populate this log.")
else:
    history_display = st.session_state.history_df.copy()
    history_display["accepted"] = history_display["accepted"].apply(
        lambda x: "✅ Accepted" if x == 1 else "❌ Rejected"
    )
    history_display.columns = [
        "Distance (km)",
        "Accept Rate (%)",
        "Avg Response (min)",
        "Outcome"
    ]
    history_display["Distance (km)"] = history_display["Distance (km)"].apply(lambda x: f"{x:.2f}")
    history_display["Accept Rate (%)"] = history_display["Accept Rate (%)"].apply(lambda x: f"{x*100:.0f}%")
    
    st.dataframe(history_display, use_container_width=True)
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        accepted_count = (st.session_state.history_df["accepted"] == 1).sum()
        st.metric("Accepted Rescues", int(accepted_count))
    
    with col_exp2:
        rejected_count = (st.session_state.history_df["accepted"] == 0).sum()
        st.metric("Rejected Rescues", int(rejected_count))

# --------------------------------------------------
# SECTION 4: COMPLETED RESCUES LOG
# --------------------------------------------------
st.divider()
st.subheader("✨ Completed Rescues")

if len(st.session_state.completed_rescues) == 0:
    st.info("No completed rescues yet. Mark a rescue as 'Completed' in NGO Dashboard.")
else:
    rescues_df = pd.DataFrame(st.session_state.completed_rescues)
    
    st.dataframe(rescues_df, use_container_width=True)
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.metric("Total Completed", len(st.session_state.completed_rescues))
    
    with summary_col2:
        if len(st.session_state.completed_rescues) > 0:
            total_meals = st.session_state.completed_rescues[-1].get("num_meals", 0)
            st.metric("Last Rescue Meals", total_meals)
        else:
            st.metric("Last Rescue Meals", "-")
    
    with summary_col3:
        if len(st.session_state.completed_rescues) > 0:
            last_ngo = st.session_state.completed_rescues[-1].get("ngo_name", "-")
            st.metric("Last NGO", last_ngo)
        else:
            st.metric("Last NGO", "-")

# --------------------------------------------------
# SECTION 5: SYSTEM LOGS
# --------------------------------------------------
st.divider()
st.subheader("🔍 System Logs")

with st.expander("📋 View Detailed System Logs"):
    st.caption("Debug and audit information for system operations.")
    
    log_text = f"""
    **System Status:** Active
    **Total Interaction Records:** {len(st.session_state.history_df)}
    **Total Completed Rescues:** {len(st.session_state.completed_rescues)}
    **Model Accuracy:** {st.session_state.model_accuracy * 100:.1f}%
    **Registered NGOs:** 5
    **Model Algorithm:** RandomForest (100 estimators)
    **Training Samples Required:** 5+ records
    
    **Last Model Status:**
    - Trained: {st.session_state.model_accuracy > 0}
    - Accuracy: {st.session_state.model_accuracy * 100:.1f}%
    - Classes Seen: Accepted, Rejected
    
    **Recent Activities:**
    - Food Provider Dashboard: Location map selector enabled
    - NGO Dashboard: Status tracking active
    - Admin Panel: Model retrain available
    """
    
    st.code(log_text, language="text")

# --------------------------------------------------
# SECTION 6: RESET (DANGER ZONE)
# --------------------------------------------------
st.divider()
st.subheader("⚠️ Danger Zone")

col_danger1, col_danger2 = st.columns(2)

with col_danger1:
    if st.button("🗑️ Clear All Interaction Data", use_container_width=True, type="secondary"):
        st.session_state.history_df = st.session_state.history_df.iloc[0:0]
        st.warning("⚠️ All interaction data cleared.")
        st.rerun()

with col_danger2:
    if st.button("🗑️ Clear Completed Rescues", use_container_width=True, type="secondary"):
        st.session_state.completed_rescues = []
        st.warning("⚠️ All completed rescue logs cleared.")
        st.rerun()
