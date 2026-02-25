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

st.title("🍱 Food Rescue Request")
st.caption("Help us connect your excess food to hungry people. Submit details below.")

# --------------------------------------------------
# SECTION 1: FOOD DETAILS FORM
# --------------------------------------------------
st.subheader("📦 Food Details")

col1, col2 = st.columns(2)

with col1:
    food_type = st.selectbox(
        "Food Type",
        ["Rice & Curry", "Bread & Bakery", "Vegetables", "Fruits", "Cooked Meals", "Other"]
    )
    num_meals = st.number_input(
        "Number of Meals",
        min_value=1,
        max_value=1000,
        value=50
    )

with col2:
    ready_time = st.time_input("Ready Time", value=None)
    expiry_time = st.time_input("Expiry Time", value=None)

event_type = st.selectbox(
    "Event Type",
    ["Wedding", "Conference", "Festival", "Catering", "Restaurant", "Hotel", "Other"]
)

cause_tag = st.selectbox(
    "Why is this food available? (Cause Tag)",
    [
        "Overestimated Attendance",
        "Guest No-Show",
        "Weather Issue",
        "Buffer Cooking",
        "Unknown"
    ]
)

# --------------------------------------------------
# SECTION 2: PROVIDER LOCATION
# --------------------------------------------------
st.subheader("📍 Location")
st.caption("Click on the map to select your pickup location. Or use browser geolocation fallback.")

if st_folium is None:
    st.error("⚠️ streamlit-folium is not installed. Please install it to use the map.")
else:
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
    
    map_data = st_folium(location_map, height=400, width=None, key="provider_map")
    
    if map_data and map_data.get("last_clicked"):
        clicked = map_data["last_clicked"]
        st.session_state.provider_lat = float(clicked["lat"])
        st.session_state.provider_lon = float(clicked["lng"])
        st.rerun()

# --------------------------------------------------
# LOCATION FALLBACK OPTIONS
# --------------------------------------------------
col_geo, col_clear = st.columns(2)

if col_geo.button("📡 Use Browser Geolocation (Fallback)"):
    if streamlit_geolocation is None:
        st.warning("streamlit_geolocation is not installed.")
    else:
        location_data = streamlit_geolocation()
        if location_data and \
           location_data.get("latitude") is not None and \
           location_data.get("longitude") is not None:
            st.session_state.provider_lat = float(location_data["latitude"])
            st.session_state.provider_lon = float(location_data["longitude"])
            st.success("✅ Browser location captured!")
        else:
            st.warning("Browser location not available. Allow location permission.")

if col_clear.button("🧹 Clear Selected Location"):
    st.session_state.provider_lat = None
    st.session_state.provider_lon = None
    st.rerun()

# Manual fallback
if st.session_state.provider_lat is None or st.session_state.provider_lon is None:
    st.warning("📍 No location selected yet. Use map or geolocation above, or enter manually:")
    col_man1, col_man2 = st.columns(2)
    
    with col_man1:
        manual_lat = st.number_input(
            "Latitude (Manual Fallback)",
            value=11.0200,
            format="%.6f"
        )
    
    with col_man2:
        manual_lon = st.number_input(
            "Longitude (Manual Fallback)",
            value=76.9500,
            format="%.6f"
        )
    
    if st.button("✅ Confirm Manual Location"):
        st.session_state.provider_lat = manual_lat
        st.session_state.provider_lon = manual_lon
        st.success("✅ Location confirmed!")
        st.rerun()
else:
    st.success(
        f"✅ Location Selected: {round(st.session_state.provider_lat, 6)}, "
        f"{round(st.session_state.provider_lon, 6)}"
    )

# --------------------------------------------------
# FIND TOP NGOs BUTTON
# --------------------------------------------------
st.divider()

if st.button("🔍 Find Top 3 NGOs", use_container_width=True, type="primary"):
    if st.session_state.provider_lat is None or st.session_state.provider_lon is None:
        st.error("❌ Please select a location first.")
    else:
        with st.spinner("🔄 Ranking NGOs..."):
            ranked = rank_ngos(
                st.session_state.provider_lat,
                st.session_state.provider_lon
            )
            st.session_state.top3 = ranked.head(3)
            st.session_state.rejected_ngo_ids = []  # Reset rejected list
            st.session_state.food_details = {
                "food_type": food_type,
                "num_meals": num_meals,
                "ready_time": str(ready_time),
                "expiry_time": str(expiry_time),
                "event_type": event_type,
                "cause_tag": cause_tag
            }
        
        st.success("✅ Top 3 NGOs ranked successfully!")
        st.info("👉 Go to **NGO Dashboard** to view results and select an NGO.")

# --------------------------------------------------
# DISPLAY TOP 3 PREVIEW
# --------------------------------------------------
if st.session_state.top3 is not None:
    st.divider()
    st.subheader("🏆 Top 3 NGOs Preview")
    
    for idx, (_, row) in enumerate(st.session_state.top3.iterrows(), 1):
        with st.container(border=True):
            col_icon, col_info = st.columns([1, 5])
            
            with col_icon:
                if idx == 1:
                    st.markdown("🥇")
                elif idx == 2:
                    st.markdown("🥈")
                else:
                    st.markdown("🥉")
            
            with col_info:
                st.markdown(f"### {row['ngo_name']}")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Distance", f"{round(row['distance'], 2)} km")
                col_b.metric("Acceptance Rate", f"{int(row['accept_rate']*100)}%")
                col_c.metric("Avg Response", f"{row['avg_response_time']} min")
