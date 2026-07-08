import numpy as np
import plotly.graph_objects as go
import streamlit as st

from utils import load_summary

st.set_page_config(page_title="FitnessData — Statistics Deep Dive", page_icon="🔬", layout="wide")

st.title("🔬 Statistics Deep Dive")

summary_df = load_summary()

st.subheader("Workout Duration Distribution")
fig_hist = go.Figure(go.Histogram(x=summary_df["duration_min"], nbinsx=40, marker_color="#3b82f6"))
fig_hist.update_layout(
    xaxis_title="Duration (min)",
    yaxis_title="Workouts",
    height=400,
    margin=dict(l=40, r=20, t=20, b=40),
)
st.plotly_chart(fig_hist, width="stretch")

col1, col2, col3 = st.columns(3)
col1.metric("Median Duration", f"{summary_df['duration_min'].median():.0f} min")
col2.metric("Mean Duration", f"{summary_df['duration_min'].mean():.0f} min")
col3.metric("Std. Dev.", f"{summary_df['duration_min'].std():.0f} min")

st.subheader("Training Frequency vs. Strength (Monthly)")
monthly = (
    summary_df.assign(month=summary_df["date"].dt.to_period("M"))
    .groupby("month")
    .agg(frequency=("workout_id", "count"), avg_peak_1rm=("peak_estimated_1rm", "mean"))
    .reset_index()
)

x = monthly["frequency"].to_numpy(dtype=float)
y = monthly["avg_peak_1rm"].to_numpy(dtype=float)
corr = np.corrcoef(x, y)[0, 1]
slope, intercept = np.polyfit(x, y, 1)
trend_x = np.array([x.min(), x.max()])
trend_y = slope * trend_x + intercept

fig_scatter = go.Figure()
fig_scatter.add_trace(
    go.Scatter(x=x, y=y, mode="markers", name="Month", marker=dict(color="#3b82f6", size=9))
)
fig_scatter.add_trace(
    go.Scatter(x=trend_x, y=trend_y, mode="lines", name="Trend", line=dict(color="#f59e0b", dash="dash"))
)
fig_scatter.update_layout(
    xaxis_title="Workouts per Month",
    yaxis_title="Avg. Peak Estimated 1RM (kg)",
    height=450,
    margin=dict(l=40, r=20, t=20, b=40),
)
st.plotly_chart(fig_scatter, width="stretch")
st.caption(f"Pearson correlation: r = {corr:.2f} (based on {len(monthly)} months)")
