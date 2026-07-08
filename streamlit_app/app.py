import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import load_sets, load_summary

st.set_page_config(page_title="FitnessData — Overview", page_icon="🏋️", layout="wide")


def compute_week_streak(dates: pd.Series) -> int:
    weeks = sorted(set(dates.dt.to_period("W")))
    if not weeks:
        return 0
    streak = 1
    current = weeks[-1]
    for week in reversed(weeks[:-1]):
        if week == current - 1:
            streak += 1
            current = week
        else:
            break
    return streak


def calendar_heatmap(dates_with_volume: pd.DataFrame, year: int) -> go.Figure:
    """GitHub-style contribution calendar for one year."""
    jan1 = pd.Timestamp(year=year, month=1, day=1)
    dec31 = pd.Timestamp(year=year, month=12, day=31)
    all_days = pd.DataFrame({"date": pd.date_range(jan1, dec31, freq="D")})

    daily = dates_with_volume.groupby(dates_with_volume["date"].dt.normalize())["volume_kg"].sum()
    all_days["volume_kg"] = all_days["date"].map(daily).fillna(0)

    all_days["week"] = ((all_days["date"] - jan1).dt.days + jan1.weekday()) // 7
    all_days["weekday"] = all_days["date"].dt.weekday  # Monday = 0

    n_weeks = all_days["week"].max() + 1
    z = [[None] * n_weeks for _ in range(7)]
    hover = [[""] * n_weeks for _ in range(7)]
    for _, row in all_days.iterrows():
        w, d = int(row["week"]), int(row["weekday"])
        z[d][w] = row["volume_kg"]
        hover[d][w] = f"{row['date'].date()}<br>{row['volume_kg']:.0f} kg"

    fig = go.Figure(
        go.Heatmap(
            z=z,
            text=hover,
            hoverinfo="text",
            colorscale=[[0, "#ebedf0"], [0.01, "#c6e48b"], [0.4, "#7bc96f"], [0.7, "#239a3b"], [1, "#196127"]],
            showscale=False,
            xgap=3,
            ygap=3,
        )
    )
    fig.update_yaxes(
        tickmode="array",
        tickvals=[0, 1, 2, 3, 4, 5, 6],
        ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        autorange="reversed",
    )
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(height=220, margin=dict(l=40, r=10, t=10, b=10))
    return fig


sets_df = load_sets()
summary_df = load_summary()

st.title("🏋️ FitnessData — Overview")
st.caption("6 years of personal strength training data, exported from Strong.")

total_workouts = len(summary_df)
total_volume_t = summary_df["total_volume_kg"].sum() / 1000
top_muscle_group = (
    sets_df.groupby("muscle_group")["volume_kg"].sum().sort_values(ascending=False).index[0]
)
week_streak = compute_week_streak(summary_df["date"])
last_workout = summary_df["date"].max()
days_since_last = (pd.Timestamp.now().normalize() - last_workout.normalize()).days

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Workouts", f"{total_workouts:,}")
col2.metric("Total Volume", f"{total_volume_t:,.1f} t")
col3.metric("Most-Trained Muscle Group", top_muscle_group)
col4.metric("Current Week Streak", f"{week_streak} wk", help="Consecutive weeks with at least one workout, ending at the last logged session.")

st.caption(f"Last logged workout: {last_workout.date()} ({days_since_last} days ago)")

st.subheader("Training Calendar")
years = sorted(summary_df["date"].dt.year.unique(), reverse=True)
selected_year = st.selectbox("Year", years, index=0)
st.plotly_chart(calendar_heatmap(sets_df, selected_year), width="stretch")
