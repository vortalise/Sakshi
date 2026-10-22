import json
from pathlib import Path
from datetime import date
import pandas as pd
import streamlit as st

st.set_page_config(page_title="EcoTrack", page_icon="🌱", layout="centered")
DATA_FILE = Path(__file__).with_name("ecotrack_data.json")
CATEGORIES = ["Transport", "Electricity", "Waste", "Green Action"]
GREEN_ACTIONS = ["Trees Planted", "Trees Watered", "Recycling Activities", "Reusable Bag Uses"]

st.markdown("""
<style>
.block-container {max-width: 760px; padding-top: 1.2rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.25); padding: 12px; border-radius: 12px;}
.stButton button, .stDownloadButton button {width: 100%; min-height: 2.8rem;}
</style>
""", unsafe_allow_html=True)


def load_activities():
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_activities(items):
    DATA_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

if "activities" not in st.session_state:
    st.session_state.activities = load_activities()
activities = st.session_state.activities

st.title("🌱 EcoTrack")
st.caption("Personal environmental activity tracker")
st.info("Add activities, review your progress, and download your records. Eco scores are simple points, not scientific measurements of environmental impact.")

with st.expander("➕ Add an activity", expanded=not activities):
    activity_kind = st.selectbox("Activity type", ["Transport", "Electricity", "Waste", "Green action"])
    with st.form("add_activity", clear_on_submit=True):
        activity_date = st.date_input("Date", value=date.today())
        if activity_kind == "Transport":
            transport_type = st.selectbox("Transport method", ["Walk", "Bike", "Bus", "Train", "Car", "Other"])
            value = st.number_input("Distance travelled (km)", min_value=0.0, step=0.5)
            label, unit, category = transport_type, "km", "Transport"
        elif activity_kind == "Electricity":
            value = st.number_input("Electricity used (kWh)", min_value=0.0, step=0.5)
            label, unit, category = "Electricity Usage", "kWh", "Electricity"
        elif activity_kind == "Waste":
            value = st.number_input("Waste generated (kg)", min_value=0.0, step=0.1)
            label, unit, category = "Waste Generated", "kg", "Waste"
        else:
            label = st.selectbox("Green action", GREEN_ACTIONS)
            value = st.number_input("Quantity", min_value=1, step=1)
            unit, category = "count", "Green Action"
        submitted = st.form_submit_button("Save activity")
        if submitted:
            item = {"date": activity_date.isoformat(), "category": category, "type": label, "value": value, "unit": unit}
            activities.append(item)
            save_activities(activities)
            st.session_state.activities = activities
            st.success("Activity saved.")
            st.rerun()

# Summary and chart
counts = {cat: sum(1 for a in activities if a.get("category") == cat) for cat in CATEGORIES}
eco_score = sum({"Transport": 5, "Electricity": 2, "Waste": 3, "Green Action": 5}.get(a.get("category"), 0) for a in activities)
col1, col2 = st.columns(2)
col1.metric("Activities recorded", len(activities))
col2.metric("Eco score", f"{eco_score} points")

st.subheader("Activity overview")
if activities:
    chart_data = pd.DataFrame({"Category": CATEGORIES, "Records": [counts[c] for c in CATEGORIES]}).set_index("Category")
    st.bar_chart(chart_data)
    st.dataframe(chart_data.reset_index(), hide_index=True, use_container_width=True)
else:
    st.write("No activities recorded yet. Add your first activity above.")

st.subheader("Your activity records")
if activities:
    df = pd.DataFrame(activities)
    # Keep columns predictable even if older records lack newer fields.
    for col in ["date", "category", "type", "value", "unit"]:
        if col not in df.columns:
            df[col] = ""
    st.dataframe(df[["date", "category", "type", "value", "unit"]].sort_values("date", ascending=False), hide_index=True, use_container_width=True)
    csv = df[["date", "category", "type", "value", "unit"]].to_csv(index=False).encode("utf-8-sig")
    st.download_button("Download records as CSV", data=csv, file_name="ecotrack_report.csv", mime="text/csv")
    if st.button("Clear all records", type="secondary"):
        st.session_state.confirm_clear = True
    if st.session_state.get("confirm_clear", False):
        st.warning("This permanently clears all records stored by this app instance.")
        c1, c2 = st.columns(2)
        if c1.button("Confirm clear", type="primary"):
            st.session_state.activities = []
            save_activities([])
            st.session_state.confirm_clear = False
            st.rerun()
        if c2.button("Cancel"):
            st.session_state.confirm_clear = False
            st.rerun()
else:
    st.caption("Once you add records, you can download them as a CSV file and open it in a spreadsheet app.")

with st.expander("Green suggestions"):
    st.markdown("- Walk or cycle for short trips when practical.\n- Use public transport when available.\n- Switch off unused lights and appliances.\n- Separate recyclable waste according to local rules.\n- Plant trees and care for them.\n- Carry a reusable shopping bag.")

st.divider()
st.caption("Prototype note: this version saves data to a local JSON file on the server. Free cloud hosting may restart or replace that file, so it is not suitable for important long-term records without connecting persistent storage.")
