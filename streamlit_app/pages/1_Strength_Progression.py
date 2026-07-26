import plotly.graph_objects as go
import streamlit as st

from utils import PLOTLY_CONFIG, disable_zoom, load_sets

st.set_page_config(page_title="FitnessData — Strength Progression", layout="wide")

st.title("Strength Progression")
st.caption("Estimated 1RM (Epley formula), best set per session.")

sets_df = load_sets()

exercises = sorted(sets_df["exercise_name"].unique())
default_exercise = "Squat (Barbell)" if "Squat (Barbell)" in exercises else exercises[0]
selected_exercise = st.selectbox("Exercise", exercises, index=exercises.index(default_exercise))

ex_df = sets_df[sets_df["exercise_name"] == selected_exercise]
daily_best = (
    ex_df.groupby(ex_df["date"].dt.normalize())["estimated_1rm"]
    .max()
    .reset_index()
    .sort_values("date")
)

if daily_best.empty:
    st.info("No sets logged for this exercise.")
else:
    pr_row = daily_best.loc[daily_best["estimated_1rm"].idxmax()]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=daily_best["date"],
            y=daily_best["estimated_1rm"],
            mode="lines+markers",
            name="Estimated 1RM",
            line=dict(color="#3b82f6"),
            marker=dict(size=5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[pr_row["date"]],
            y=[pr_row["estimated_1rm"]],
            mode="markers+text",
            name="PR",
            marker=dict(size=14, color="#f59e0b", symbol="star"),
            text=[f"PR: {pr_row['estimated_1rm']:.1f} kg"],
            textposition="top center",
            showlegend=False,
        )
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Estimated 1RM (kg)",
        height=500,
        margin=dict(l=40, r=20, t=20, b=40),
    )
    st.plotly_chart(disable_zoom(fig), width="stretch", config=PLOTLY_CONFIG)

    col1, col2, col3 = st.columns(3)
    col1.metric("Personal Record", f"{pr_row['estimated_1rm']:.1f} kg", help=f"Set on {pr_row['date'].date()}")
    col2.metric("Sessions Logged", f"{len(daily_best)}")
    col3.metric("Latest Estimated 1RM", f"{daily_best.iloc[-1]['estimated_1rm']:.1f} kg")
