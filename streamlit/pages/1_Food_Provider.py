"""
Aharam Setu - Page 1: Food Provider Dashboard
Submit food details and location to find matching NGOs.
"""

import streamlit as st
import folium

from core import init_session_state, rank_ngos

try:
    from streamlit_folium import st_folium
except ModuleNotFoundError:
    st_folium = None

try:
    from streamlit_geolocation import streamlit_geolocation
except ModuleNotFoundError:
    streamlit_geolocation = None

st.set_page_config(page_title="Food Provider Dashboard", layout="wide")
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
    
    .provider-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FF6B6B !important;
        margin-bottom: 0.5rem;
    }
    
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1a1a1a !important;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #FF6B6B;
        padding-bottom: 0.5rem;
    }
    
    .ngo-card {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe0cc 100%);
        border-left: 4px solid #FF6B6B;
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

st.markdown('<div class="provider-title">🍱 Food Rescue Request</div>', unsafe_allow_html=True)
st.markdown("Help us connect your excess food to hungry people. Submit details below.", unsafe_allow_html=True)

# --------------------------------------------------
# SECTION 1: FOOD DETAILS FORM
# --------------------------------------------------
st.markdown('<div class="section-header">📦 Food Details</div>', unsafe_allow_html=True)

form_col1, form_col2 = st.columns(2, gap="large")

with form_col1:
    st.markdown("**What type of food?**")
    food_type = st.selectbox(
        "Select food type",
        ["Rice & Curry", "Bread & Bakery", "Vegetables", "Fruits", "Cooked Meals", "Other"],
        label_visibility="collapsed"
    )
    
    st.markdown("**How many meals/portions?**")
    num_meals = st.number_input(
        "Number of meals",
        min_value=1,
        max_value=1000,
        value=50,
        label_visibility="collapsed"
    )

with form_col2:
    st.markdown("**When will it be ready?**")
    ready_time = st.time_input("Ready time", value=None, label_visibility="collapsed")
    
    st.markdown("**When does it expire?**")
    expiry_time = st.time_input("Expiry time", value=None, label_visibility="collapsed")

st.markdown("---")

col_event, col_cause = st.columns(2, gap="large")

with col_event:
    st.markdown("**What type of event?**")
    event_type = st.selectbox(
        "Event type",
        ["Wedding", "Conference", "Festival", "Catering", "Restaurant", "Hotel", "Other"],
        label_visibility="collapsed"
    )

with col_cause:
    st.markdown("**Why is this food available?**")
    cause_tag = st.selectbox(
        "Cause",
        ["Overestimated Attendance", "Guest No-Show", "Weather Issue", "Buffer Cooking", "Unknown"],
        label_visibility="collapsed"
    )

# --------------------------------------------------
# SECTION 2: PROVIDER LOCATION
# --------------------------------------------------
st.markdown('<div class="section-header">📍 Location Selection</div>', unsafe_allow_html=True)
st.caption("Click on the map to select your pickup location, use browser geolocation, or enter manually.")

if st_folium is None:
    st.error("⚠️ streamlit-folium is not installed. Please install it to use the map.")
else:
    # Map display
    map_tab, manual_tab = st.tabs(["🗺️ Interactive Map", "📝 Manual Entry"])
    
    with map_tab:
        india_lat = 20.5937
        india_lon = 78.9629
        
        map_center_lat = st.session_state.provider_lat or india_lat
        map_center_lon = st.session_state.provider_lon or india_lon
        
        location_map = folium.Map(
            location=[map_center_lat, map_center_lon],
            zoom_start=5,
            tiles="OpenStreetMap"
        )
        
        if st.session_state.provider_lat is not None and st.session_state.provider_lon is not None:
            folium.Marker(
                [st.session_state.provider_lat, st.session_state.provider_lon],
                popup="Your Pickup Location",
                tooltip="Pickup Location",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(location_map)
        
        map_data = st_folium(location_map, height=450, width=None, key="provider_map")
        
        if map_data and map_data.get("last_clicked"):
            clicked = map_data["last_clicked"]
            st.session_state.provider_lat = float(clicked["lat"])
            st.session_state.provider_lon = float(clicked["lng"])
            st.success(f"✅ Location saved: {st.session_state.provider_lat:.6f}, {st.session_state.provider_lon:.6f}")
            st.rerun()
        
        # Quick buttons under map
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        
        with btn_col1:
            if st.button("📡 Use Browser Geolocation", use_container_width=True):
                if streamlit_geolocation is None:
                    st.warning("streamlit_geolocation is not installed.")
                else:
                    location_data = streamlit_geolocation()
                    if location_data and location_data.get("latitude") is not None:
                        st.session_state.provider_lat = float(location_data["latitude"])
                        st.session_state.provider_lon = float(location_data["longitude"])
                        st.success("✅ Location captured from browser!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Allow location permission in browser.")
        
        with btn_col2:
            if st.button("🧹 Clear Location", use_container_width=True):
                st.session_state.provider_lat = None
                st.session_state.provider_lon = None
                st.rerun()
        
        with btn_col3:
            if st.session_state.provider_lat is not None:
                st.success(f"✅ Selected: {round(st.session_state.provider_lat, 4)}, {round(st.session_state.provider_lon, 4)}")
            else:
                st.info("📍 Click on map or use button above")
    
    with manual_tab:
        st.caption("Enter latitude and longitude manually if map selection doesn't work.")
        
        man_col1, man_col2 = st.columns(2)
        
        with man_col1:
            manual_lat = st.number_input(
                "Latitude (Default: Kochi)",
                value=11.0200,
                format="%.6f"
            )
        
        with man_col2:
            manual_lon = st.number_input(
                "Longitude (Default: Kochi)",
                value=76.9500,
                format="%.6f"
            )
        
        if st.button("✅ Confirm Manual Location", use_container_width=True):
            st.session_state.provider_lat = manual_lat
            st.session_state.provider_lon = manual_lon
            st.success("✅ Location confirmed!")
            st.rerun()

# --------------------------------------------------
# FIND TOP NGOs BUTTON
# --------------------------------------------------
st.divider()

action_col1, action_col2, action_col3 = st.columns([2, 1, 1])

with action_col1:
    if st.button("🔍 Find Top 3 NGOs for Me", use_container_width=True, type="primary"):
        if st.session_state.provider_lat is None or st.session_state.provider_lon is None:
            st.error("❌ Please select a location first using map or manual entry.")
        else:
            with st.spinner("🔄 Analyzing location and ranking NGOs..."):
                ranked = rank_ngos(
                    st.session_state.provider_lat,
                    st.session_state.provider_lon
                )
                st.session_state.top3 = ranked.head(3)
                st.session_state.rejected_ngo_ids = []
                st.session_state.food_details = {
                    "food_type": food_type,
                    "num_meals": num_meals,
                    "ready_time": str(ready_time),
                    "expiry_time": str(expiry_time),
                    "event_type": event_type,
                    "cause_tag": cause_tag
                }
            
            st.success("✅ Found top 3 NGOs!")
            st.info("👉 Check the **NGO Dashboard** to view detailed rankings and select an NGO.")

with action_col2:
    st.empty()

with action_col3:
    st.empty()

# --------------------------------------------------
# DISPLAY TOP 3 PREVIEW
# --------------------------------------------------
if st.session_state.top3 is not None:
    st.divider()
    st.markdown('<div class="section-header">🏆 Top 3 Matches</div>', unsafe_allow_html=True)
    
    preview_cols = st.columns(3, gap="medium")
    
    for idx, ((_, row), col) in enumerate(zip(st.session_state.top3.iterrows(), preview_cols), 1):
        with col:
            with st.container(border=True):
                if idx == 1:
                    st.markdown("### 🥇 #1 Top Match")
                elif idx == 2:
                    st.markdown("### 🥈 #2 Good Match")
                else:
                    st.markdown("### 🥉 #3 Fair Match")
                
                st.markdown(f"**{row['ngo_name']}**")
                st.divider()
                
                st.metric("Distance", f"{round(row['distance'], 2)} km")
                st.metric("Acceptance Rate", f"{int(row['accept_rate']*100)}%")
                st.metric("Avg Response Time", f"{row['avg_response_time']} min")
