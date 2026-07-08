import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import load_sets, load_summary

st.set_page_config(page_title="FitnessData — Volume & Frequency", page_icon="📊", layout="wide")

st.title("📊 Volume & Frequency")

sets_df = load_sets()
summary_df = load_summary()

st.subheader("Monthly Volume")
monthly = (
    summary_df.assign(month=summary_df["date"].dt.to_period("M").astype(str))
    .groupby("month")["total_volume_kg"]
    .sum()
    .reset_index()
)
fig_monthly = px.bar(
    monthly,
    x="month",
    y="total_volume_kg",
    labels={"month": "Month", "total_volume_kg": "Volume (kg)"},
)
fig_monthly.update_layout(height=400, margin=dict(l=40, r=20, t=20, b=40))
st.plotly_chart(fig_monthly, width="stretch")

st.subheader("When Do You Train?")
workout_times = summary_df.copy()
workout_times["weekday"] = workout_times["date"].dt.weekday
workout_times["hour"] = workout_times["date"].dt.hour

weekday_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
counts = workout_times.groupby(["weekday", "hour"]).size().reset_index(name="count")
z = [[0] * 24 for _ in range(7)]
for _, row in counts.iterrows():
    z[int(row["weekday"])][int(row["hour"])] = row["count"]

fig_hm = go.Figure(
    go.Heatmap(
        z=z,
        x=list(range(24)),
        y=weekday_labels,
        colorscale="Blues",
        colorbar=dict(title="Workouts"),
    )
)
fig_hm.update_layout(
    xaxis_title="Hour of Day",
    yaxis_title="Weekday",
    height=350,
    margin=dict(l=60, r=20, t=20, b=40),
)
st.plotly_chart(fig_hm, width="stretch")

st.subheader("Top 10 Exercises by Total Volume")
top10 = (
    sets_df.groupby("exercise_name")["volume_kg"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .rename(columns={"exercise_name": "Exercise", "volume_kg": "Total Volume (kg)"})
)
top10["Total Volume (kg)"] = top10["Total Volume (kg)"].round(0).astype(int)
st.dataframe(top10, hide_index=True, width="stretch")
