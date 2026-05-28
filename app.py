import streamlit as st
import pandas as pd
import numpy as np
import joblib
import sqlite3
from datetime import datetime

# ==========================================
# 0. DATABASE / TELEMETRY LAYER (SQL)
# ==========================================
DB_FILE = "grid_telemetry.db"

def init_db():
    """Initializes the database and creates the telemetry table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            target_node TEXT,
            temperature REAL,
            hour INTEGER,
            month TEXT,
            day_of_week TEXT,
            exam_mode_active INTEGER,
            predicted_load REAL
        )
    """)
    conn.commit()
    conn.close()

def log_prediction(node, temp, hr, mo, day, exam, prediction):
    """Logs system inputs and outputs to the SQL database for audit trails."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO telemetry_logs 
        (timestamp, target_node, temperature, hour, month, day_of_week, exam_mode_active, predicted_load)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), node, temp, hr, mo, day, int(exam), round(prediction, 2)))
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="NIT Delhi Smart Grid EMS", 
    page_icon="⚡", 
    layout="wide"
)

st.markdown(
    """
    <style>
    * { font-family: 'Times New Roman', Times, serif !important; }
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 15px;
    }
    .metric-title { font-size: 14px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 28px; font-weight: bold; color: #1a1a1a; margin-top: 5px; }
    </style>
    """,
    unsafe_allow_html=True
)

# Load the Prediction Engine (Note: We still need the .pkl brain to calculate the numbers!)
@st.cache_resource
def load_model():
    return joblib.load("campus_energy_brain.pkl")

brain = load_model()

# ==========================================
# 2. HEADER BLOCK
# ==========================================
header_col1, header_col2 = st.columns([1, 12])
with header_col1:
    logo_url = "https://nitdelhi.ac.in/wp-content/uploads/2020/07/nitdelhi-logo-1.png"
    st.image(logo_url, width=90)
with header_col2:
    st.markdown("<h1 style='margin-bottom: 0px; padding-bottom: 0px;'>National Institute of Technology, Delhi</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6c757d; font-size: 16px; margin-top: 5px;'>Smart Grid Management System & Structural Load Forecaster</p>", unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 10px; margin-bottom: 30px;'>", unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR CONTROLS
# ==========================================
st.sidebar.markdown("### 🎛️ Grid Environment Controls")

temp_input = st.sidebar.slider("Ambient Temperature (°C)", min_value=10.0, max_value=50.0, value=28.0, step=0.5)
hour_input = st.sidebar.slider("Simulation Hour (24h)", min_value=0, max_value=23, value=12)

month_dict = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}
month_select = st.sidebar.selectbox("Analysis Month", list(month_dict.keys()))
month_input = month_dict[month_select]

day_dict = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
}
day_select = st.sidebar.selectbox("Day of Week", list(day_dict.keys()))
day_input = day_dict[day_select]
is_weekend_input = 1 if day_input >= 5 else 0

st.sidebar.markdown("### 📝 Academic Modifiers")
is_exam_season = st.sidebar.toggle("Activate Mid-Sem / End-Sem Exam Mode", value=False)

# ==========================================
# 4. INFRASTRUCTURE LOGIC MATRIX
# ==========================================
building_profiles_base = {
    "Admin Block": {"type": "admin", "details": "Centralized AC System", "base_mult": 1.4},
    "Academic Block": {"type": "academic", "details": "Professors Cabins & Active Library", "base_mult": 0.8},
    "Sagar Residency": {"type": "residential_faculty", "details": "Faculty Housing (4 BHK Complex)", "base_mult": 0.6},
    "Shivalik Boys Hostel": {"type": "hostel", "details": "9-Floor High-Density Men's Residence", "base_mult": 1.8},
    "Yamuna Girls Hostel": {"type": "hostel", "details": "7-Floor Women's Residence", "base_mult": 1.4},
    "Dhauladhar Boys Hostel": {"type": "hostel", "details": "7-Floor Men's Residence", "base_mult": 1.4},
    "Mini Campus": {"type": "lecture_hall", "details": "Core Lecture Complex & Faculty Cubicles", "base_mult": 1.1}
}

def calculate_multiplier(b_type, h, is_weekend, exam_mode):
    for name, profile in building_profiles_base.items():
        if profile["type"] == b_type:
            mult = profile["base_mult"]
            break
    if b_type == "admin":
        if is_weekend: return 0.15
        elif not (9 <= h <= 18): return 0.3
    elif b_type == "academic":
        if exam_mode: mult += 1.2
        elif not (8 <= h <= 20): return 0.2
    elif b_type == "residential_faculty":
        if 6 <= h <= 8 or 18 <= h <= 23: mult += 0.3
    elif b_type == "hostel":
        if 23 <= h or h <= 5: mult += 0.4
        elif 9 <= h <= 17 and not is_weekend: mult *= 0.5
    elif b_type == "lecture_hall":
        if not (9 <= h <= 17) or is_weekend: return 0.1
    return mult

# ==========================================
# 5. CORE WORKSPACE
# ==========================================
main_col1, main_col2 = st.columns([2, 3])

with main_col1:
    st.markdown("### 🏢 Infrastructure Selection")
    options_list = ["Overall Campus Grid"] + list(building_profiles_base.keys())
    selected_building = st.selectbox("Target Infrastructure Node", options_list)
    
    # Run Base AI Inference
    input_features = pd.DataFrame([{
        "Hour": hour_input, "Month": month_input, "DayOfWeek": day_input,
        "IsWeekend": is_weekend_input, "Temperature": temp_input
    }])
    ai_base_prediction = brain.predict(input_features)[0]
    
    if selected_building == "Overall Campus Grid":
        final_building_load = 0
        for b_name, data in building_profiles_base.items():
            m = calculate_multiplier(data["type"], hour_input, is_weekend_input, is_exam_season)
            final_building_load += (ai_base_prediction * m)
        details_text = "Aggregation of all 7 core structural campus grid nodes."
        status_notes = "Aggregated load metrics online. Monitoring cumulative substation strain."
    else:
        b_meta = building_profiles_base[selected_building]
        m = calculate_multiplier(b_meta["type"], hour_input, is_weekend_input, is_exam_season)
        final_building_load = ai_base_prediction * m
        details_text = b_meta["details"]
        if b_meta["type"] == "admin" and is_weekend_input:
            status_notes = "Administrative shutdown active. Centralized chillers powered down."
        elif b_meta["type"] == "academic" and is_exam_season:
            status_notes = "Exam Season Active. 24/7 Library operations causing a severe spike."
        else:
            status_notes = "System operating within standard structural boundaries."

    # 🌟 SQL TELEMETRY TRIGGER 🌟
    # Every single time a user adjustments parameters, log the session state into the SQL DB
    log_prediction(selected_building, temp_input, hour_input, month_select, day_select, is_exam_season, final_building_load)

    # UI Card Layout
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Simulated Grid Draw ({selected_building})</div>
            <div class="metric-value">{round(final_building_load, 2)} kWh</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write(f"ℹ️ **Node Specifications:** {details_text}")
    if "spike" in status_notes or "strain" in status_notes:
        st.warning(f"🚨 {status_notes}")
    elif "shutdown" in status_notes or "closed" in status_notes:
        st.error(f"📉 {status_notes}")
    else:
        st.info(f"🟢 {status_notes}")

with main_col2:
    st.markdown("### 📈 Real-Time 24-Hour Building Load Curve")
    hours_axis = list(range(24))
    hourly_sim_trend = []
    
    for h in hours_axis:
        loop_features = pd.DataFrame([{
            "Hour": h, "Month": month_input, "DayOfWeek": day_input, "IsWeekend": is_weekend_input,
            "Temperature": temp_input if abs(h - hour_input) > 4 else temp_input + (2 if 11 <= h <= 15 else -2)
        }])
        loop_base_pred = brain.predict(loop_features)[0]
        
        if selected_building == "Overall Campus Grid":
            total_hour_load = 0
            for b_name, data in building_profiles_base.items():
                m_loop = calculate_multiplier(data["type"], h, is_weekend_input, is_exam_season)
                total_hour_load += (loop_base_pred * m_loop)
            hourly_sim_trend.append(total_hour_load)
        else:
            m_loop = calculate_multiplier(building_profiles_base[selected_building]["type"], h, is_weekend_input, is_exam_season)
            hourly_sim_trend.append(loop_base_pred * m_loop)
    
    chart_dataframe = pd.DataFrame({'Hour of Day': hours_axis, 'Projected Load (kWh)': hourly_sim_trend}).set_index('Hour of Day')
    st.line_chart(chart_dataframe, height=260)

# ==========================================
# 6. ADMIN TELEMETRY VIEWER LAYER
# ==========================================
st.markdown("---")
st.subheader("🕵️‍♂️ System Telemetry Audit Log (Live SQL Injection)")
st.write("This section mimics corporate observability dashboards (like Datadog or Azure Monitor), displaying real-time data writes to our relational database.")

# Read directly from the SQL database to display to the interviewer
conn = sqlite3.connect(DB_FILE)
df_logs = pd.read_sql_query("SELECT * FROM telemetry_logs ORDER BY id DESC LIMIT 5", conn)
conn.close()

if not df_logs.empty:
    st.dataframe(df_logs, use_container_width=True)