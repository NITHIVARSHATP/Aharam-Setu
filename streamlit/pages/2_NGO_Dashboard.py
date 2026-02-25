"""
Aharam Setu - Page 2: NGO Dashboard
View ranked NGOs, update pickup status, and complete rescues.
"""

import streamlit as st
import pandas as pd

from core import init_session_state, compute_reliability_score, log_rescue_completion, train_model, rank_ngos

st.set_page_config(page_title="NGO Dashboard", layout="wide")
init_session_state()

st.title("🚚 NGO Ranking & Reliability")
st.caption("View top-ranked NGOs and update rescue status.")

# --------------------------------------------------
# CHECK IF TOP3 IS AVAILABLE
# --------------------------------------------------
if st.session_state.top3 is None:
    st.warning(
        "⚠️ No NGOs ranked yet.\n\n"
        "👉 Go to **Food Provider Dashboard** to submit food details and find NGOs."
    )
else:
    # Get available NGOs (excluding rejected ones)
    available_ngos = st.session_state.top3[
        ~st.session_state.top3["ngo_id"].isin(st.session_state.rejected_ngo_ids)
    ]
    
    if len(available_ngos) == 0:
        # Auto-fetch next top 3 when all are rejected
        st.warning("⚠️ All top 3 NGOs have been rejected. Fetching next ranked NGOs...")
        
        if st.session_state.provider_lat is not None and st.session_state.provider_lon is not None:
            with st.spinner("🔄 Ranking next set of NGOs..."):
                # Get all NGOs ranked
                all_ranked = rank_ngos(
                    st.session_state.provider_lat,
                    st.session_state.provider_lon
                )
                # Skip rejected ones and get next 3
                remaining_ngos = all_ranked[
                    ~all_ranked["ngo_id"].isin(st.session_state.rejected_ngo_ids)
                ]
                
                if len(remaining_ngos) > 0:
                    st.session_state.top3 = remaining_ngos.head(3)
                    st.success("✅ Fetched next ranked NGOs!")
                    st.rerun()
                else:
                    st.error("❌ No more NGOs available. All have been rejected.")
        else:
            st.info("👉 Go to **Food Provider Dashboard** to submit food details and find NGOs.")
    else:
        # --------------------------------------------------
        # DISPLAY TOP RANKED NGO (HIGHLIGHTED)
        # --------------------------------------------------
        st.subheader("🥇 Top Ranked NGO")
        
        top_ngo = available_ngos.iloc[0]
        reliability = compute_reliability_score(top_ngo)
        
        with st.container(border=True):
            col_top_left, col_top_right = st.columns([2, 1])
            
            with col_top_left:
                st.markdown(f"### {top_ngo['ngo_name']}")
                prob_percent = round(top_ngo['predicted_probability'] * 100, 1)
                st.markdown(f"**Predicted Acceptance Probability:** {prob_percent}%")
            
            with col_top_right:
                st.metric("Reliability Score", f"{reliability}/100")
            
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            col_t1.metric("Distance", f"{round(top_ngo['distance'], 2)} km")
            col_t2.metric("Accept Rate", f"{int(top_ngo['accept_rate']*100)}%")
            col_t3.metric("Avg Response", f"{top_ngo['avg_response_time']} min")
            col_t4.metric("NGO ID", f"#{top_ngo['ngo_id']}")
            
            # Status buttons for top NGO
            st.markdown("#### 📊 Update Status")
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                if st.button("✅ Accept", key=f"accept_{top_ngo['ngo_id']}", use_container_width=True):
                    # Check if this NGO was already accepted in current session
                    is_duplicate = any(
                        (st.session_state.history_df["accept_rate"] == top_ngo["accept_rate"]) &
                        (st.session_state.history_df["distance"] == top_ngo["distance"]) &
                        (st.session_state.history_df["accepted"] == 1)
                    )
                    
                    if is_duplicate:
                        st.warning(f"⚠️ {top_ngo['ngo_name']} already accepted! No duplicate entry added.")
                    else:
                        # Log acceptance to history for model training
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
                        st.success(f"✅ {top_ngo['ngo_name']} accepted the rescue! Model updated.")
                        st.rerun()
            
            with col_btn2:
                if st.button("🚗 On the Way", key=f"onway_{top_ngo['ngo_id']}", use_container_width=True):
                    st.session_state.ngo_status[top_ngo['ngo_id']] = "on_the_way"
                    st.info(f"🚗 {top_ngo['ngo_name']} is on the way.")
            
            with col_btn3:
                if st.button("📦 Picked Up", key=f"pickup_{top_ngo['ngo_id']}", use_container_width=True):
                    st.session_state.ngo_status[top_ngo['ngo_id']] = "picked_up"
                    st.info(f"📦 Food picked up by {top_ngo['ngo_name']}!")
            
            with col_btn4:
                if st.button("✨ Completed", key=f"complete_{top_ngo['ngo_id']}", use_container_width=True):
                    # Check if this NGO was already marked completed in current session
                    is_duplicate = any(
                        (st.session_state.history_df["accept_rate"] == top_ngo["accept_rate"]) &
                        (st.session_state.history_df["distance"] == top_ngo["distance"]) &
                        (st.session_state.history_df["accepted"] == 1)
                    )
                    
                    if is_duplicate:
                        st.warning(f"⚠️ {top_ngo['ngo_name']} already logged as completed!")
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
                        st.success(
                            f"✨ Rescue completed by {top_ngo['ngo_name']}! "
                            f"Model updated with feedback."
                        )
                        st.rerun()
        
        # --------------------------------------------------
        # OTHER RANKED NGOs (RANKED TABLE)
        # --------------------------------------------------
        st.subheader("📊 All Ranked NGOs")
        
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
            "Accept Rate (%)",
            "Avg Response (min)",
            "Reliability /100",
            "Status"
        ]
        display_df_short["Accept Rate (%)"] = display_df_short["Accept Rate (%)"].apply(lambda x: f"{int(x*100)}%")
        display_df_short["Distance (km)"] = display_df_short["Distance (km)"].apply(lambda x: f"{round(x, 2)}")
        
        st.dataframe(display_df_short, use_container_width=True)
        
        # --------------------------------------------------
        # FOOD DETAILS RECAP
        # --------------------------------------------------
        st.divider()
        st.subheader("📋 Food Details (From Provider)")
        
        col_food1, col_food2, col_food3 = st.columns(3)
        col_food1.metric("Food Type", st.session_state.food_details.get("food_type", "-"))
        col_food2.metric("Number of Meals", st.session_state.food_details.get("num_meals", "-"))
        col_food3.metric("Event Type", st.session_state.food_details.get("event_type", "-"))
        
        st.caption(f"Cause: {st.session_state.food_details.get('cause_tag', '-')}")
        
        # --------------------------------------------------
        # FEEDBACK: ACCEPT / REJECT
        # --------------------------------------------------
        st.divider()
        st.subheader("📝 Quick Feedback (Reject Rescue)")
        
        st.caption(
            "If an NGO is unavailable or you want to try the next option, "
            "reject to skip this NGO and show the next ranked one."
        )
        
        reject_ngo_name = st.selectbox(
            "Select NGO to reject:",
            available_ngos["ngo_name"].tolist()
        )
        
        if st.button("❌ Reject This NGO & Show Next", use_container_width=True, type="secondary"):
            reject_ngo = available_ngos[available_ngos["ngo_name"] == reject_ngo_name].iloc[0]
            
            # Add to rejected list
            st.session_state.rejected_ngo_ids.append(reject_ngo["ngo_id"])
            
            # Log rejection feedback
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
            
            st.success(f"❌ {reject_ngo_name} rejected. Showing next ranked NGO...")
            st.rerun()
