"""
Aharam Setu - Home Dashboard
Smart Food Rescue System for faster and reliable food redistribution.
"""

import streamlit as st

from core import get_ngo_master_data, init_session_state

st.set_page_config(
    page_title="Aharam Setu",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded"
)
init_session_state()

# Custom CSS for better styling
st.markdown("""
<style>
    /* Overall page background */
    .stApp {
        background-color: #f8f9fa !important;
        color: #1a1a1a !important;
    }
    
    /* Main container */
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
    }
    
    /* Ensure text is visible */
    body, h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #1a1a1a !important;
    }
    
    /* Input field styling - text inputs, selects, textareas */
    input, textarea, select {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 2px solid #d0d0d0 !important;
        border-radius: 0.5rem !important;
    }
    
    input::placeholder {
        color: #999 !important;
    }
    
    /* Selectbox and dropdown styling */
    [data-testid="stSelectbox"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input,
    [data-testid="stTimeInput"] input {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 2px solid #d0d0d0 !important;
    }
    
    /* Popover and dropdown menu */
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
    
    /* Main title styling */
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 1.2rem;
        color: #333 !important;
        margin-bottom: 2rem;
    }
    
    /* Metric cards styling */
    [data-testid="metric-container"] {
        background: white !important;
        border-radius: 0.75rem;
        padding: 1.5rem !important;
        border: 2px solid #e0e0e0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    }
    
    [data-testid="metric-container"] h3,
    [data-testid="metric-container"] p,
    [data-testid="metric-container"] span,
    [data-testid="metric-container"] div {
        color: #1a1a1a !important;
    }
    
    /* Container styling */
    [data-testid="stContainer"] {
        background-color: white !important;
    }
    
    /* Tab styling */
    [data-testid="stTabs"] {
        background: white !important;
        border-radius: 0.75rem;
        padding: 1.5rem !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    /* Divider */
    hr {
        border-color: #ddd !important;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🍱 Aharam Setu</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Smart Food Rescue System for faster and reliable food redistribution.</div>', unsafe_allow_html=True)

# --------------------------------------------------
# QUICK STATS
# --------------------------------------------------
st.markdown("### 📊 Quick Stats")
stat_col1, stat_col2, stat_col3 = st.columns(3, gap="large")

with stat_col1:
    st.metric(
        label="🏢 Registered NGOs",
        value=len(get_ngo_master_data()),
        delta="Active partners",
    )

with stat_col2:
    st.metric(
        label="✅ Completed Rescues",
        value=len(st.session_state.completed_rescues),
        delta="Lives impacted" if len(st.session_state.completed_rescues) > 0 else "Start rescuing",
    )

with stat_col3:
    st.metric(
        label="📝 Interaction Records",
        value=len(st.session_state.history_df),
        delta="Training data points",
    )

# --------------------------------------------------
# WORKFLOW OVERVIEW
# --------------------------------------------------
st.markdown("### 🌍 How It Works")
with st.container(border=True):
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown("#### 1️⃣ Submit Food")
        st.caption("Food Provider submits details & location")
        st.markdown("📦 Type • 🕐 Expiry • 📍 Location")
    
    with col2:
        st.markdown("#### 2️⃣ AI Ranking")
        st.caption("System ranks top NGOs")
        st.markdown("🤖 Distance • 📊 History • ✅ Reliability")
    
    with col3:
        st.markdown("#### 3️⃣ Live Tracking")
        st.caption("NGO updates status")
        st.markdown("🚚 Status • ⏱️ Time • 📍 Location")
    
    with col4:
        st.markdown("#### 4️⃣ Completion")
        st.caption("Admin monitors & retrains")
        st.markdown("📈 Metrics • 🔄 Retrain • 📊 Logs")

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------
st.markdown("### 🧭 Navigate to Dashboards")
nav_col1, nav_col2, nav_col3 = st.columns(3, gap="large")

with nav_col1:
    with st.container(border=True):
        st.markdown("#### 🍱 Food Provider")
        st.caption("Submit excess food & find NGOs")
        st.markdown("- Add food details\n- Set pickup location\n- Get top 3 matches")

with nav_col2:
    with st.container(border=True):
        st.markdown("#### 🚚 NGO Dashboard")
        st.caption("Manage rescue operations")
        st.markdown("- View ranked NGOs\n- Update status\n- Complete rescues")

with nav_col3:
    with st.container(border=True):
        st.markdown("#### ⚙️ Admin Panel")
        st.caption("Monitor & optimize system")
        st.markdown("- Model metrics\n- Retrain ML model\n- View all logs")

# --------------------------------------------------
# RECENT ACTIVITY
# --------------------------------------------------
st.divider()
st.markdown("### ⚡ System Status")

col_status1, col_status2, col_status3 = st.columns(3, gap="large")

with col_status1:
    model_trained = st.session_state.model_accuracy > 0
    status_text = "✅ Trained" if model_trained else "⏳ Pending"
    status_color = "🟢" if model_trained else "🟡"
    st.metric(
        label=f"{status_color} Model Status",
        value=status_text,
        help="Model training requires 5+ interaction records"
    )

with col_status2:
    acceptance_rate = (
        (st.session_state.history_df["accepted"].sum() / len(st.session_state.history_df) * 100)
        if len(st.session_state.history_df) > 0
        else 0
    )
    rate_display = f"{acceptance_rate:.1f}%" if acceptance_rate > 0 else "N/A"
    st.metric(
        label="📈 Acceptance Rate",
        value=rate_display,
        help="% of rescues accepted by NGOs"
    )

with col_status3:
    avg_distance = (
        st.session_state.history_df["distance"].mean()
        if len(st.session_state.history_df) > 0
        else 0
    )
    distance_display = f"{avg_distance:.1f} km" if avg_distance > 0 else "N/A"
    st.metric(
        label="🗺️ Avg Distance",
        value=distance_display,
        help="Average distance to ranked NGOs"
    )

# --------------------------------------------------
# STATISTICS & REPORTS
# --------------------------------------------------
st.divider()
st.markdown("### 📈 Impact Statistics & Reports")

# India Food Waste Statistics
report_tab1, report_tab2 = st.tabs(["🇮🇳 Food Waste Crisis", "📊 System Performance"])

with report_tab1:
    st.markdown("#### 🌍 Food Waste in India - Crisis Overview")
    
    # Major stats about food waste in India
    india_col1, india_col2, india_col3, india_col4 = st.columns(4, gap="medium")
    
    with india_col1:
        with st.container(border=True):
            st.markdown("### 78M")
            st.caption("Tonnes of food waste\ngenerated annually")
            st.markdown("*Ranking 2nd globally*")
    
    with india_col2:
        with st.container(border=True):
            st.markdown("### ₹92,000 Cr")
            st.caption("Economic value of\nwasted food")
            st.markdown("*₹1 lakh crore loss*")
    
    with india_col3:
        with st.container(border=True):
            st.markdown("### 55 kg")
            st.caption("Household waste\nper capita annually")
            st.markdown("*Per person loss*")
    
    with india_col4:
        with st.container(border=True):
            st.markdown("### 14%")
            st.caption("Population that\nremains underfed")
            st.markdown("*Despite abundance*")
    
    st.divider()
    
    st.markdown("#### 📊 Key Sources of Food Waste")
    
    source_col1, source_col2, source_col3 = st.columns(3, gap="large")
    
    with source_col1:
        with st.container(border=True):
            st.markdown("#### 🏠 Households")
            st.markdown("**~60%** of total waste")
            st.caption("Poor storage, over-purchasing, plate waste")
    
    with source_col2:
        with st.container(border=True):
            st.markdown("#### 🍽️ Food Services")
            st.markdown("**~28%** of total waste")
            st.caption("Hotels, restaurants, catering events")
    
    with source_col3:
        with st.container(border=True):
            st.markdown("#### 🏬 Retail")
            st.markdown("**~12%** of total waste")
            st.caption("Supermarkets, small shops")
    
    st.divider()
    
    st.markdown("#### 🔴 Major Causes of Food Waste")
    
    cause_col1, cause_col2, cause_col3 = st.columns(3, gap="medium")
    
    with cause_col1:
        st.markdown("**🛒 Purchasing Issues**")
        st.markdown("- Over-purchasing\n- Bulk buying patterns\n- Seasonal fluctuations")
    
    with cause_col2:
        st.markdown("**🌡️ Storage Problems**")
        st.markdown("- Poor storage conditions\n- Lack of refrigeration\n- Pest & spoilage")
    
    with cause_col3:
        st.markdown("**🎉 Event Dynamics**")
        st.markdown("- Wedding overestimation\n- Guest no-shows\n- Buffet waste")

with report_tab2:
    st.markdown("#### 📊 Aharam Setu System Performance")
    
    # Calculate impact metrics
    total_rescues = len(st.session_state.completed_rescues)
    total_meals_estimate = sum(
        int(detail.get("num_meals", 0)) 
        for detail in (st.session_state.food_details,) 
        if isinstance(detail, dict)
    ) if total_rescues > 0 else 0
    
    accepted_count = int(
        st.session_state.history_df["accepted"].sum() 
        if len(st.session_state.history_df) > 0 else 0
    )
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4, gap="medium")
    
    with perf_col1:
        with st.container(border=True):
            st.markdown("### 🎯")
            st.markdown(f"**{len(st.session_state.history_df)}**")
            st.caption("Total Interactions\nProcessed")
    
    with perf_col2:
        with st.container(border=True):
            st.markdown("### ✅")
            st.markdown(f"**{accepted_count}**")
            st.caption("Successful\nMatches")
    
    with perf_col3:
        with st.container(border=True):
            st.markdown("### 🏆")
            success_rate = (
                (accepted_count / len(st.session_state.history_df) * 100)
                if len(st.session_state.history_df) > 0 else 0
            )
            st.markdown(f"**{success_rate:.1f}%**")
            st.caption("Success\nRate")
    
    with perf_col4:
        with st.container(border=True):
            st.markdown("### 🤖")
            accuracy = f"{st.session_state.model_accuracy * 100:.1f}%"
            st.markdown(f"**{accuracy}**")
            st.caption("Model\nAccuracy")
    
    st.divider()
    
    st.markdown("#### 📈 System Insights")
    
    insight_col1, insight_col2 = st.columns(2, gap="large")
    
    with insight_col1:
        st.markdown("**🔍 NGO Performance**")
        
        ngo_data = get_ngo_master_data()
        best_ngo = ngo_data.loc[ngo_data["accept_rate"].idxmax()]
        worst_ngo = ngo_data.loc[ngo_data["accept_rate"].idxmin()]
        
        st.markdown(f"""
        - **Most Reliable:** {best_ngo['ngo_name']} ({int(best_ngo['accept_rate']*100)}% acceptance)
        - **Fastest Response:** {ngo_data.loc[ngo_data['avg_response_time'].idxmin(), 'ngo_name']} ({ngo_data['avg_response_time'].min()} min)
        - **Total Active NGOs:** {len(ngo_data)}
        - **Avg Acceptance Rate:** {int(ngo_data['accept_rate'].mean()*100)}%
        """)
    
    with insight_col2:
        st.markdown("**🎯 Site Coverage**")
        
        if len(st.session_state.history_df) > 0:
            avg_dist = st.session_state.history_df["distance"].mean()
            min_dist = st.session_state.history_df["distance"].min()
            max_dist = st.session_state.history_df["distance"].max()
            
            st.markdown(f"""
            - **Average Coverage:** {avg_dist:.2f} km
            - **Min Distance:** {min_dist:.2f} km
            - **Max Distance:** {max_dist:.2f} km
            - **Coverage Area:** City-wide multi-location support
            """)
        else:
            st.info("⏳ Data will appear after first rescue")

# --------------------------------------------------
# KEY FEATURES
# --------------------------------------------------
st.divider()
st.markdown("### ✨ Key Features")

feat_col1, feat_col2, feat_col3 = st.columns(3, gap="large")

with feat_col1:
    with st.container(border=True):
        st.markdown("#### 🗺️ Interactive Map")
        st.caption("Smart location selection")
        st.markdown("- Click on map to select pickup location\n- Browser geolocation fallback\n- Real-time distance calculation")

with feat_col2:
    with st.container(border=True):
        st.markdown("#### 🤖 ML-Based Ranking")
        st.caption("Intelligent NGO matching")
        st.markdown("- RandomForest predictions\n- Distance-based ranking\n- Historical acceptance learning")

with feat_col3:
    with st.container(border=True):
        st.markdown("#### 📱 Live Status Tracking")
        st.caption("Real-time operation updates")
        st.markdown("- Accept/Reject feedback\n- Status progression tracking\n- Completion logging")

st.divider()
st.info("💡 **Getting Started:** Use the left sidebar to navigate to the Food Provider Dashboard and submit your first food rescue request!")
