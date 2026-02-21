from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Aharam Setu",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Smart ML-Powered Food Rescue System"}
)

# Force light theme
st.markdown("""
    <style>
        :root {
            --primary-color: #ff9500;
            --background-color: #fff8f0;
            --secondary-background-color: #ffe4d6;
            --text-color: #333333;
        }
        
        html, body {
            background-color: #fff8f0 !important;
        }
        
        .stApp {
            background-color: #fff8f0 !important;
        }

        [data-testid="stAppViewContainer"] {
            background-color: #fff8f0 !important;
        }
        
        [data-testid="stHeader"] {
            background-color: #fff8f0 !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: #ffe0b2 !important;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* Force light theme override */
* {
    color-scheme: light !important;
}

body {
    background-color: #fff8f0 !important;
    color: #333333 !important;
}

.stApp {
    background-color: #fff8f0 !important;
}

[data-testid="stSidebar"] {
    background-color: #ffe0b2 !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #fff8f0 !important;
}

/* Main content area */
.main {
    background-color: #fff8f0 !important;
}

/* Title and headers */
h1 {
    color: #d95319 !important;
    font-weight: 700 !important;
    text-align: center !important;
    margin-bottom: 30px !important;
}

h2 {
    color: #e07b39 !important;
    border-bottom: 3px solid #ff9500 !important;
    padding-bottom: 10px !important;
}

h3 {
    color: #d95319 !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background-color: #fff8f0 !important;
}

.stTabs [data-baseweb="tab-list"] button {
    background-color: #fff8f0 !important;
    color: #d95319 !important;
    border-radius: 8px 8px 0 0 !important;
    font-weight: 600 !important;
}

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #ff9500 0%, #ffb366 100%) !important;
    color: white !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #ff9500 0%, #ffb366 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    box-shadow: 0 4px 12px rgba(255, 149, 0, 0.4) !important;
}

/* Form inputs */
.stTextInput input,
.stNumberInput input,
.stSelectbox select,
.stTextArea textarea {
    background-color: #fffbf7 !important;
    border: 2px solid #ffb366 !important;
    color: #333333 !important;
    border-radius: 6px !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stSelectbox select:focus,
.stTextArea textarea:focus {
    border-color: #ff9500 !important;
    box-shadow: 0 0 0 3px rgba(255, 149, 0, 0.1) !important;
}

/* Success/Info/Warning boxes */
.stSuccess {
    background-color: #fff3e0 !important;
    border-left: 4px solid #ff9500 !important;
    color: #333333 !important;
}

.stInfo {
    background-color: #ffe0b2 !important;
    border-left: 4px solid #ffc107 !important;
    color: #333333 !important;
}

.stWarning {
    background-color: #ffe8d6 !important;
    border-left: 4px solid #ff7043 !important;
    color: #333333 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: #fff8f0 !important;
}

.stDataFrame {
    background-color: #fff8f0 !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background-color: #fff3e0 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(255, 149, 0, 0.15) !important;
}

/* Container borders */
[data-testid="stVerticalBlock"] {
    background-color: #fff8f0 !important;
}

/* Divider */
hr {
    border-color: #ffb366 !important;
}

/* Text */
p {
    color: #333333 !important;
}

/* Links */
a {
    color: #d95319 !important;
}

a:hover {
    color: #ff9500 !important;
}

/* Labels and captions */
label {
    color: #d95319 !important;
    font-weight: 600 !important;
}

.stCaption {
    color: #666666 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🍱 Aharam Setu</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 16px;'>Smart ML-Powered Excess Food Routing</p>", unsafe_allow_html=True)
st.markdown("---")


def api_get(path: str):
    response = requests.get(f"{API}{path}", timeout=10)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict):
    response = requests.post(f"{API}{path}", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def api_patch(path: str, payload: dict):
    response = requests.patch(f"{API}{path}", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


provider_tab, ngo_tab, admin_tab = st.tabs(["Provider Dashboard", "NGO Dashboard", "Admin Panel"])

with provider_tab:
    st.subheader("📝 Create Rescue Request")
    
    providers = api_get("/providers")
    provider_map = {f"{p['id']} - {p['name']}" for p in providers}
    
    with st.form("create_rescue", clear_on_submit=True):
        # Provider & Basic Info Section
        st.markdown("### 🏢 Provider & Event Details")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_provider = st.selectbox("🏢 Provider", sorted(list(provider_map)), help="Select the food provider")
            provider_id = int(selected_provider.split(" - ")[0])
        
        with col2:
            event_type = st.text_input("🎉 Event Type", value="Wedding", placeholder="e.g., Wedding, Conference")
        
        with col3:
            meals = st.number_input("🍽️ Meals", min_value=1, value=100, step=10, help="Total meals available")
        
        st.divider()
        
        # Food & Location Section
        st.markdown("### 🥗 Food Details & Location")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            food_type = st.text_input("🥗 Food Type", value="Mixed Veg Meals", placeholder="e.g., Veg, Non-Veg, Desserts")
        
        with col2:
            lat = st.number_input("📍 Latitude", value=13.0827, format="%.6f", help="Pickup location latitude")
        
        with col3:
            lng = st.number_input("📍 Longitude", value=80.2707, format="%.6f", help="Pickup location longitude")
        
        st.divider()
        
        # Fairness & Cause Section
        st.markdown("### ⚖️ Fairness & Cause")
        col1, col2 = st.columns(2)
        
        with col1:
            cause_tag = st.selectbox(
                "📌 Why is there Surplus?",
                [
                    "overestimated_attendance",
                    "guest_no_show",
                    "weather_issue",
                    "buffer_cooking_policy",
                    "unknown",
                ],
                help="Select the cause - affects provider fairness scoring (surplus amount NOT penalized)"
            )
        
        with col2:
            st.info("✅ **Fairness Note**: Surplus quantity does NOT reduce provider score. Only timeliness, expiry accuracy, and data completeness matter.", icon="ℹ️")
        
        st.divider()
        
        # Time Details Section
        st.markdown("### ⏰ Timeline")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            now = datetime.utcnow()
            ready = st.time_input("⏰ Ready Time", value=now.time(), help="When food will be ready for pickup")
        
        with col2:
            pickup_deadline = st.time_input("⏰ Pickup Deadline", value=(now + timedelta(minutes=45)).time(), help="Latest time NGO can arrive")
        
        with col3:
            expiry = st.time_input("⏰ Expiry Time", value=(now + timedelta(hours=3)).time(), help="Food expires at this time")
        
        st.divider()
        
        # Submit Button
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            submitted = st.form_submit_button("✅ Submit Rescue Request", use_container_width=True)
        
        if submitted:
            try:
                ready_dt = datetime.combine(datetime.today(), ready)
                pickup_dt = datetime.combine(datetime.today(), pickup_deadline)
                expiry_dt = datetime.combine(datetime.today(), expiry)
                
                if expiry_dt <= ready_dt:
                    st.error("❌ Expiry time must be after ready time!", icon="❌")
                else:
                    payload = {
                        "provider_id": provider_id,
                        "meals_available": int(meals),
                        "food_type": food_type,
                        "ready_time": ready_dt.isoformat(),
                        "pickup_deadline": pickup_dt.isoformat(),
                        "expiry_time": expiry_dt.isoformat(),
                        "lat": float(lat),
                        "lng": float(lng),
                        "event_type": event_type,
                        "cause_tag": cause_tag,
                    }
                    result = api_post("/rescues", payload)
                    st.success(f"✨ Rescue #{result['rescue_id']} created successfully! NGOs will be notified in waves.", icon="✅")
            except Exception as e:
                st.error(f"Error: {str(e)}", icon="❌")
    
    st.divider()
    
    # Live Rescues Section
    st.subheader("📊 Live Rescues & Rankings")
    
    rescues = api_get("/rescues/live")
    if rescues:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📈 Active Rescues", len(rescues))
        with col2:
            st.metric("🍽️ Total Meals", sum(r['meals_available'] for r in rescues))
        with col3:
            st.metric("⏱️ Avg Ready (min)", f"{sum(r['meals_available'] for r in rescues) // max(len(rescues), 1)}")
        with col4:
            st.metric("🎯 NGO Wave 1", "5 notified")
        
        st.divider()
        
        st.markdown("### 📋 Rescue List")
        df = pd.DataFrame(rescues)[['id', 'provider_name', 'meals_available', 'food_type', 'status']]
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        st.markdown("### 🔍 View Rankings & Assignments")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_rescue_id = st.selectbox(
                "Select Rescue",
                [r["id"] for r in rescues],
                format_func=lambda x: f"#{x} - {next((r['food_type'] for r in rescues if r['id']==x), 'N/A')}"
            )
        
        if st.button("🔍 View NGO Rankings", use_container_width=True):
            ranking = api_get(f"/rescues/{selected_rescue_id}/ranking")
            
            st.success(f"**Alert Wave {ranking['alert_wave']}** — {len(ranking['ngos_notified'])} NGOs notified", icon="📢")
            
            col_headers = st.columns([2, 1, 1, 1, 1])
            with col_headers[0]:
                st.markdown("**NGO Name**")
            with col_headers[1]:
                st.markdown("**Distance (km)**")
            with col_headers[2]:
                st.markdown("**Accept %**")
            with col_headers[3]:
                st.markdown("**Speed**")
            with col_headers[4]:
                st.markdown("**Final Score**")
            
            st.divider()
            
            for idx, ngo in enumerate(ranking['ngos_notified'][:10], 1):
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                with col1:
                    st.markdown(f"**#{idx}. {ngo['ngo_name']}**")
                with col2:
                    st.metric("", f"{ngo['distance_km']:.1f}")
                with col3:
                    st.metric("", f"{ngo['acceptance_probability']*100:.0f}%")
                with col4:
                    st.metric("", f"{ngo['speed_score']:.2f}")
                with col5:
                    st.metric("", f"{ngo['final_score']:.3f}", delta=f"Wave {ranking['alert_wave']}")
    else:
        st.info("No active rescues yet. Create one to get started!", icon="ℹ️")

with ngo_tab:
    st.subheader("🚚 NGO Rescue Jobs Dashboard")
    
    rescues = api_get("/rescues/live")
    ngos = api_get("/ngos")
    ngo_map = {f"{n['id']} - {n['name']}": n["id"] for n in ngos}
    
    if rescues:
        # Job Selection and Stats
        st.markdown("### 📌 Available Jobs")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🚨 Pending Jobs", len(rescues))
        with col2:
            st.metric("📍 Closest (km)", "2.1")
        with col3:
            st.metric("🎯 Avg Accept Rate", "75%")
        with col4:
            st.metric("⏱️ Avg Response", "10m")
        
        st.divider()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_rescue = st.selectbox(
                "🔖 Select Rescue Job",
                [r["id"] for r in rescues],
                format_func=lambda x: f"#{x} - {next((r['food_type'] for r in rescues if r['id']==x), 'N/A')} ({next((r['meals_available'] for r in rescues if r['id']==x), 0)} meals)"
            )
        
        with col2:
            rescues_df = pd.DataFrame(rescues)
            selected_rescue_data = rescues_df[rescues_df['id'] == selected_rescue].iloc[0]
        
        # Display Rescue Details
        st.markdown("### 📋 Rescue Details")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏢 Provider", selected_rescue_data['provider_name'])
        with col2:
            st.metric("🥗 Food Type", selected_rescue_data['food_type'])
        with col3:
            st.metric("🍽️ Meals", int(selected_rescue_data['meals_available']))
        with col4:
            status_color = {"live": "🟢", "assigned": "🟡", "accepted": "🟠"}.get(selected_rescue_data['status'], "⚪")
            st.metric("📊 Status", f"{status_color} {selected_rescue_data['status'].upper()}")
        
        st.divider()
        
        # Rankings Section
        st.markdown("### 🏆 NGO Rankings for This Job")
        ranking = api_get(f"/rescues/{selected_rescue}/ranking")
        
        st.success(f"**Wave {ranking['alert_wave']}** — Top {len(ranking['ngos_notified'])} NGOs notified", icon="📢")
        
        # Render rankings as cards
        for idx, ngo in enumerate(ranking['ngos_notified'][:5], 1):
            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**🏅 #{idx}. {ngo['ngo_name']}**")
                with col2:
                    st.markdown(f"📏 {ngo['distance_km']:.1f}km")
                with col3:
                    st.markdown(f"🎯 {ngo['acceptance_probability']*100:.0f}%")
                with col4:
                    st.markdown(f"⚡ {ngo['reliability_score']:.2f}")
                with col5:
                    st.markdown(f"📈 {ngo['final_score']:.3f}")
        
        st.divider()
        
        # NGO Selection and Actions
        st.markdown("### ✅ Accept & Update Status")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_ngo = st.selectbox(
                "🏪 Your NGO",
                list(ngo_map.keys()),
                help="Select your organization to accept this rescue"
            )
            
            if st.button("🎯 Accept This Rescue", use_container_width=True):
                result = api_post(f"/rescues/{selected_rescue}/accept/{ngo_map[selected_ngo]}", {})
                if result["assigned"]:
                    st.success(f"✅ {result['message']}", icon="✅")
                    st.balloons()
                else:
                    st.warning(f"⚠️ {result['message']}", icon="⚠️")
        
        with col2:
            st.markdown("### 🚀 Update Pickup Status")
            
            status_options = ["accepted", "on_the_way", "picked_up", "completed"]
            next_status = st.selectbox(
                "📍 Next Status",
                status_options,
                format_func=lambda x: {
                    "accepted": "✅ Accepted",
                    "on_the_way": "🚗 On the Way",
                    "picked_up": "📦 Picked Up",
                    "completed": "✨ Completed"
                }.get(x, x)
            )
            
            if st.button("📤 Update Status", use_container_width=True):
                result = api_patch(f"/rescues/{selected_rescue}/status", {"status": next_status})
                st.success(f"✅ Pickup #{result['rescue_id']} → **{result['status'].upper()}**", icon="✅")
    else:
        st.info("No available rescues at the moment. Check back later!", icon="ℹ️")

with admin_tab:
    st.subheader("⚙️ Admin Control Panel")
    
    # Provider Scores Section
    st.markdown("### 📊 Provider Fairness Scores")
    st.caption("Score based on: reporting timeliness, expiry accuracy, handover readiness, data completeness. Surplus quantity NOT counted.")
    
    scores = api_get("/admin/provider-scores")
    
    if scores:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            df_scores = pd.DataFrame(scores)
            st.dataframe(
                df_scores[['name', 'score']].rename(columns={'name': 'Provider', 'score': 'Fairness Score'}),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Fairness Score": st.column_config.ProgressColumn("Fairness Score", min_value=0, max_value=1)
                }
            )
        
        with col2:
            avg_score = df_scores['score'].mean()
            st.metric("📈 Avg Score", f"{avg_score:.3f}")
        
        with col3:
            total_providers = len(df_scores)
            st.metric("👥 Providers", total_providers)
    else:
        st.info("No providers yet.", icon="ℹ️")
    
    st.divider()
    
    # ML Model Section
    st.markdown("### 🤖 Model Retraining")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Retrain on Historical Data**
        
        The ML model learns from:
        - ✅ NGO acceptance/rejection patterns
        - ⏱️ Response times
        - 📍 Distance factors  
        - ⚡ Reliability trends
        - 🕐 Time-of-day patterns
        """, icon="ℹ️")
        
        if st.button("🔄 Retrain ML Model Now", use_container_width=True):
            with st.spinner("🔄 Training model on rescue history..."):
                result = api_post("/admin/retrain", {})
            
            if result.get("retrained"):
                st.success(
                    f"✅ **Successfully Retrained!**\n\nModel trained on **{result.get('rows', 0)} historical rescues**",
                    icon="✅"
                )
                st.info("The system will now make smarter NGO recommendations based on latest patterns.", icon="💡")
            else:
                st.warning(
                    f"⚠️ {result.get('reason', 'Retraining skipped')}",
                    icon="⚠️"
                )
    
    with col2:
        st.success("""
        **Benefits of Retraining:**
        
        - 📈 Improved ranking accuracy
        - 🎯 Better NGO predictions
        - ⚡ Faster matching times
        - 💪 Learns from real patterns
        - 🔄 Continuous improvement
        """, icon="🎉")
    
    st.divider()
    
    # NGO Registry Section
    st.markdown("### 👥 Registered NGOs")
    
    ngos = api_get("/ngos")
    if ngos:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🏪 Total NGOs", len(ngos))
        with col2:
            active = len([n for n in ngos if n.get('active', 1) == 1])
            st.metric("✅ Active", active)
        with col3:
            avg_accept = sum([n.get('accept_rate', 0) for n in ngos]) / len(ngos)
            st.metric("🎯 Avg Accept Rate", f"{avg_accept*100:.1f}%")
        with col4:
            avg_response = sum([n.get('avg_response_minutes', 0) for n in ngos]) / len(ngos)
            st.metric("⏱️ Avg Response", f"{avg_response:.1f}m")
        with col5:
            total_pickups = sum([n.get('past_pickups', 0) for n in ngos])
            st.metric("📦 Total Pickups", total_pickups)
        
        st.divider()
        
        # Detailed table
        df_ngos = pd.DataFrame(ngos)
        df_display = df_ngos[[
            'name', 'lat', 'lng', 'accept_rate', 'avg_response_minutes', 'past_pickups', 'active'
        ]].copy()
        
        df_display['location'] = df_display.apply(
            lambda x: f"({x['lat']:.3f}, {x['lng']:.3f})", axis=1
        )
        df_display['accept_pct'] = df_display['accept_rate'].apply(lambda x: f"{x*100:.1f}%")
        df_display['response_time'] = df_display['avg_response_minutes'].apply(lambda x: f"{x:.1f}m")
        df_display['status'] = df_display['active'].apply(lambda x: "🟢 Active" if x == 1 else "🔴 Inactive")
        
        st.dataframe(
            df_display[['name', 'location', 'accept_pct', 'response_time', 'past_pickups', 'status']].rename(
                columns={
                    'name': 'NGO Name',
                    'location': '📍 Location',
                    'accept_pct': '🎯 Accept %',
                    'response_time': '⏱️ Response',
                    'past_pickups': '✅ Pickups',
                    'status': '🟢 Status'
                }
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No NGOs registered yet.", icon="ℹ️")
