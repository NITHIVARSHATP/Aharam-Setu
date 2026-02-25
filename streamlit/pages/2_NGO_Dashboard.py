"""
Aharam Setu - Page 2: NGO Dashboard
View ranked NGOs, update pickup status, and complete rescues.
"""

import streamlit as st
import pandas as pd

from core import init_session_state, compute_reliability_score, log_rescue_completion, train_model, rank_ngos

st.set_page_config(page_title="NGO Dashboard", layout="wide")
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
    
    .ngo-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4ECDC4 !important;
        margin-bottom: 0.5rem;
    }
    
    .top-ngo-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    
    .status-button {
        width: 100%;
        padding: 0.75rem;
        border-radius: 0.5rem;
        font-weight: 600;
        margin: 0.5rem 0;
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

st.markdown('<div class="ngo-title">🚚 NGO Ranking & Status</div>', unsafe_allow_html=True)
st.markdown("View ranked NGOs and update rescue status in real-time.", unsafe_allow_html=True)

# --------------------------------------------------
# CHECK IF TOP3 IS AVAILABLE
# --------------------------------------------------
if st.session_state.top3 is None:
    st.info("📍 No ranked NGOs yet. Go to **Food Provider Dashboard** to submit food and find NGOs.")
else:
    # Get available NGOs (excluding rejected ones)
    available_ngos = st.session_state.top3[
        ~st.session_state.top3["ngo_id"].isin(st.session_state.rejected_ngo_ids)
    ]
    
    if len(available_ngos) == 0:
        # Auto-fetch next top 3 when all are rejected
        st.warning("⚠️ All top 3 NGOs rejected. Looking for more options...")
        
        if st.session_state.provider_lat is not None and st.session_state.provider_lon is not None:
            with st.spinner("🔄 Finding next set of NGOs..."):
                all_ranked = rank_ngos(
                    st.session_state.provider_lat,
                    st.session_state.provider_lon
                )
                remaining_ngos = all_ranked[
                    ~all_ranked["ngo_id"].isin(st.session_state.rejected_ngo_ids)
                ]
                
                if len(remaining_ngos) > 0:
                    st.session_state.top3 = remaining_ngos.head(3)
                    st.success("✅ Found next batch of NGOs!")
                    st.rerun()
                else:
                    st.error("❌ No more NGOs available.")
        else:
            st.info("👉 Go to **Food Provider Dashboard** first.")
    else:
        # --------------------------------------------------
        # DISPLAY TOP RANKED NGO (HIGHLIGHTED)
        # --------------------------------------------------
        st.markdown("### 🥇 Top Recommended NGO")
        
        top_ngo = available_ngos.iloc[0]
        reliability = compute_reliability_score(top_ngo)
        
        with st.container(border=True):
            col_top_left, col_top_right = st.columns([3, 1])
            
            with col_top_left:
                prob_percent = round(top_ngo['predicted_probability'] * 100, 1)
                st.markdown(f"## {top_ngo['ngo_name']}")
                st.markdown(f"**📊 Predicted Acceptance:** {prob_percent}% chance of accepting")
            
            with col_top_right:
                reliability_color = "🟢" if reliability > 75 else "🟡" if reliability > 50 else "🔴"
                st.metric(f"{reliability_color} Reliability", f"{reliability}/100")
            
            st.divider()
            
            metric_cols = st.columns(4, gap="large")
            metric_cols[0].metric("📍 Distance", f"{round(top_ngo['distance'], 2)} km")
            metric_cols[1].metric("✅ Acceptance", f"{int(top_ngo['accept_rate']*100)}%")
            metric_cols[2].metric("⏱️ Avg Response", f"{top_ngo['avg_response_time']} min")
            metric_cols[3].metric("🏢 NGO ID", f"#{top_ngo['ngo_id']}")
            
            st.divider()
            
            # Status buttons for top NGO
            st.markdown("#### 📊 Update Rescue Status")
            
            status_cols = st.columns(4, gap="small")
            
            with status_cols[0]:
                if st.button("✅ Accepted", key=f"accept_{top_ngo['ngo_id']}", use_container_width=True, type="primary"):
                    is_duplicate = any(
                        (st.session_state.history_df["accept_rate"] == top_ngo["accept_rate"]) &
                        (st.session_state.history_df["distance"] == top_ngo["distance"]) &
                        (st.session_state.history_df["accepted"] == 1)
                    )
                    
                    if is_duplicate:
                        st.warning(f"⚠️ Already logged!")
                    else:
                        new_row = pd.DataFrame([{
                            "distance": top_ngo["distance"],
                            "accept_rate": top_ngo["accept_rate"],
                            "avg_response_time": top_ngo["avg_response_time"],
                            "accepted": 1
                        }])
                        st.session_state.history_df = pd.concat(
                            [st.session_state.history_df, new_row],
                            ignore_index=True
                        )
                        train_model()
                        st.session_state.ngo_status[top_ngo['ngo_id']] = "accepted"
                        st.success(f"✅ Logged! Model updated.")
                        st.rerun()
            
            with status_cols[1]:
                if st.button("🚗 On Way", key=f"onway_{top_ngo['ngo_id']}", use_container_width=True):
                    st.session_state.ngo_status[top_ngo['ngo_id']] = "on_the_way"
                    st.info(f"🚗 {top_ngo['ngo_name']} is en route")
            
            with status_cols[2]:
                if st.button("📦 Picked Up", key=f"pickup_{top_ngo['ngo_id']}", use_container_width=True):
                    st.session_state.ngo_status[top_ngo['ngo_id']] = "picked_up"
                    st.info(f"📦 Food collected!")
            
            with status_cols[3]:
                if st.button("✨ Completed", key=f"complete_{top_ngo['ngo_id']}", use_container_width=True):
                    is_duplicate = any(
                        (st.session_state.history_df["accept_rate"] == top_ngo["accept_rate"]) &
                        (st.session_state.history_df["distance"] == top_ngo["distance"]) &
                        (st.session_state.history_df["accepted"] == 1)
                    )
                    
                    if is_duplicate:
                        st.warning(f"⚠️ Already logged!")
                    else:
                        new_row = pd.DataFrame([{
                            "distance": top_ngo["distance"],
                            "accept_rate": top_ngo["accept_rate"],
                            "avg_response_time": top_ngo["avg_response_time"],
                            "accepted": 1
                        }])
                        st.session_state.history_df = pd.concat(
                            [st.session_state.history_df, new_row],
                            ignore_index=True
                        )
                        train_model()
                        log_rescue_completion(
                            top_ngo['ngo_name'],
                            st.session_state.food_details.get("food_type", "Unknown"),
                            st.session_state.food_details.get("num_meals", 0)
                        )
                        st.session_state.ngo_status[top_ngo['ngo_id']] = "completed"
                        st.success(f"✨ Rescue completed & logged!")
                        st.rerun()
        
        # --------------------------------------------------
        # OTHER RANKED NGOs (RANKED TABLE)
        # --------------------------------------------------
        st.divider()
        st.markdown("### 📊 All Ranked NGOs")
        
        display_df = available_ngos.copy()
        display_df["reliability"] = display_df.apply(compute_reliability_score, axis=1)
        display_df["status"] = display_df["ngo_id"].apply(
            lambda ngo_id: st.session_state.ngo_status.get(ngo_id, "pending")
        )
        
        display_cols = [
            "ngo_name",
            "distance",
            "accept_rate",
            "avg_response_time",
            "reliability",
            "status"
        ]
        
        display_df_short = display_df[display_cols].copy()
        display_df_short.columns = [
            "NGO Name",
            "Distance (km)",
            "Acceptance (%)",
            "Avg Response (min)",
            "Reliability",
            "Status"
        ]
        display_df_short["Acceptance (%)"] = display_df_short["Acceptance (%)"].apply(lambda x: f"{int(x*100)}%")
        display_df_short["Distance (km)"] = display_df_short["Distance (km)"].apply(lambda x: f"{round(x, 2)}")
        
        st.dataframe(display_df_short, use_container_width=True, hide_index=True)
        
        # --------------------------------------------------
        # FOOD DETAILS RECAP
        # --------------------------------------------------
        st.divider()
        st.markdown("### 📋 Food Details Summary")
        
        recap_cols = st.columns(4)
        recap_cols[0].metric("🍱 Food Type", st.session_state.food_details.get("food_type", "-"))
        recap_cols[1].metric("🍽️ Quantity", st.session_state.food_details.get("num_meals", "-"))
        recap_cols[2].metric("🎪 Event", st.session_state.food_details.get("event_type", "-"))
        recap_cols[3].metric("💡 Reason", st.session_state.food_details.get("cause_tag", "-"))
        
        # --------------------------------------------------
        # FEEDBACK: ACCEPT / REJECT
        # --------------------------------------------------
        st.divider()
        st.markdown("### 🔄 Try Another NGO")
        
        st.caption("If an NGO is unavailable, reject to skip and show the next option.")
        
        reject_col1, reject_col2 = st.columns([2, 1])
        
        with reject_col1:
            reject_ngo_name = st.selectbox(
                "Select NGO to skip:",
                available_ngos["ngo_name"].tolist(),
                label_visibility="collapsed"
            )
        
        with reject_col2:
            if st.button("❌ Skip This NGO", use_container_width=True):
                reject_ngo = available_ngos[available_ngos["ngo_name"] == reject_ngo_name].iloc[0]
                
                st.session_state.rejected_ngo_ids.append(reject_ngo["ngo_id"])
                
                new_row = pd.DataFrame([{
                    "distance": reject_ngo["distance"],
                    "accept_rate": reject_ngo["accept_rate"],
                    "avg_response_time": reject_ngo["avg_response_time"],
                    "accepted": 0
                }])
                st.session_state.history_df = pd.concat(
                    [st.session_state.history_df, new_row],
                    ignore_index=True
                )
                train_model()
                
                st.success(f"⏭️ Skipped {reject_ngo_name}!")
                st.rerun()
