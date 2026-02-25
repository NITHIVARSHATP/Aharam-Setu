"""
Aharam Setu - Page 3: Admin Panel
Monitor model performance, retrain, and view rescue logs.
"""

import streamlit as st
import pandas as pd

from core import init_session_state, train_model

st.set_page_config(page_title="Admin Panel", layout="wide")
init_session_state()

# Custom CSS
st.markdown("""
<style>
    /* Overall page background */
    .stApp {
        background-color: #f8f9fa !important;
        color: #1a1a1a !important;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
    }
    
    /* Ensure all text is visible */
    body, h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #1a1a1a !important;
    }
    
    /* Input field styling */
    input, textarea, select {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 2px solid #d0d0d0 !important;
        border-radius: 0.5rem !important;
    }
    
    input::placeholder {
        color: #999 !important;
    }
    
    /* Selectbox and other inputs */
    [data-testid="stSelectbox"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input,
    [data-testid="stTimeInput"] input {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 2px solid #d0d0d0 !important;
    }
    
    /* Dropdown menu and options */
    [data-testid="stPopover"],
    [role="listbox"],
    [role="option"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    [role="option"]:hover {
        background-color: #f0f0f0 !important;
        color: #1a1a1a !important;
    }
    
    /* BaseWeb select styling */
    [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    
    [data-baseweb="select"] input {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    .admin-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FF6B6B !important;
        margin-bottom: 0.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white !important;
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
    }
    
    .performance-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    [data-testid="metric-container"] {
        background: white !important;
        border-radius: 0.75rem;
        padding: 1.5rem !important;
        border: 2px solid #e0e0e0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="admin-title">⚙️ Admin Control Panel</div>', unsafe_allow_html=True)
st.markdown("Monitor system health, retrain the ML model, and review rescue history.", unsafe_allow_html=True)

# --------------------------------------------------
# SECTION 1: MODEL PERFORMANCE
# --------------------------------------------------
st.markdown("### 📊 Model Performance Metrics")

perf_col1, perf_col2, perf_col3 = st.columns(3, gap="large")

with perf_col1:
    accuracy_pct = f"{st.session_state.model_accuracy * 100:.1f}%"
    status = "✅ Trained" if st.session_state.model_accuracy > 0 else "⏳ Untrained"
    st.metric(
        label="🎯 Acceptance Accuracy",
        value=accuracy_pct,
        delta=status,
        delta_color="off"
    )

with perf_col2:
    avg_response = (
        st.session_state.history_df["avg_response_time"].mean()
        if len(st.session_state.history_df) > 0
        else 0
    )
    response_text = f"{avg_response:.1f} min" if avg_response > 0 else "-"
    st.metric(
        label="⏱️ Avg Response Time",
        value=response_text,
        help="Average response time from ranked NGOs"
    )

with perf_col3:
    total_records = len(st.session_state.history_df)
    status_msg = "✅ Ready" if total_records >= 5 else f"⏳ {total_records}/5"
    st.metric(
        label="📊 Training Samples",
        value=total_records,
        delta=status_msg,
        delta_color="off"
    )

# --------------------------------------------------
# SECTION 2: MODEL RETRAINING
# --------------------------------------------------
st.divider()
st.markdown("### 🔄 Retrain ML Model")

with st.container(border=True):
    st.markdown("**How it works:** The model learns from accept/reject feedback to improve NGO ranking accuracy.")
    
    st.markdown("""
    - ✅ Requires **minimum 5** interaction records
    - ✅ Needs **both** accepted and rejected cases
    - ✅ Updates in real-time
    """)
    
    col_train_info, col_train_button = st.columns([3, 1])
    
    with col_train_info:
        if len(st.session_state.history_df) < 5:
            st.warning(f"⏳ Need {5 - len(st.session_state.history_df)} more records to train")
        else:
            st.success(f"✅ Ready to train! ({len(st.session_state.history_df)} records)")
    
    with col_train_button:
        if st.button("🔄 Train Now", use_container_width=True, type="primary"):
            if len(st.session_state.history_df) < 5:
                st.error(f"❌ Need at least 5 records. Currently: {len(st.session_state.history_df)}")
            else:
                with st.spinner("🔄 Training model on interaction data..."):
                    success = train_model()
                
                if success:
                    accuracy_pct = f"{st.session_state.model_accuracy * 100:.1f}%"
                    st.success(f"✅ Model trained! Accuracy: {accuracy_pct}")
                else:
                    st.warning("⚠️ Training incomplete. Ensure there are both accepted and rejected cases.")

# --------------------------------------------------
# SECTION 3: INTERACTION HISTORY
# --------------------------------------------------
st.divider()
st.markdown("### 📚 Complete Interaction History")

if len(st.session_state.history_df) == 0:
    st.info("📭 No interactions yet. Complete rescues to populate logs.")
else:
    history_display = st.session_state.history_df.copy()
    history_display.insert(0, "#", range(1, len(history_display) + 1))
    
    history_display["Status"] = history_display["accepted"].apply(
        lambda x: "✅ Accepted" if x == 1 else "❌ Rejected"
    )
    
    # Rename and format columns for display
    history_display_formatted = history_display[[
        "#",
        "distance",
        "accept_rate",
        "avg_response_time",
        "Status"
    ]].copy()
    
    history_display_formatted.columns = [
        "#",
        "Distance (km)",
        "Accept Rate (%)",
        "Response Time (min)",
        "Outcome"
    ]
    
    history_display_formatted["Distance (km)"] = history_display_formatted["Distance (km)"].apply(
        lambda x: f"{x:.2f}"
    )
    history_display_formatted["Accept Rate (%)"] = history_display_formatted["Accept Rate (%)"].apply(
        lambda x: f"{int(x*100)}%"
    )
    
    st.dataframe(history_display_formatted, use_container_width=True, hide_index=True)
    
    # Summary statistics
    st.divider()
    st.markdown("### 📈 Summary Statistics")
    
    accepted_count = (history_display["accepted"] == 1).sum()
    rejected_count = (history_display["accepted"] == 0).sum()
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    summary_col1.metric("✅ Accepted", accepted_count)
    summary_col2.metric("❌ Rejected", rejected_count)
    summary_col3.metric("📊 Success Rate", f"{(accepted_count / len(history_display) * 100):.1f}%")
    
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
