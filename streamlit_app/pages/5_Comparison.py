import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import PLOTLY_CONFIG, REFERENCE_FILE, disable_zoom, load_reference, load_sets

st.set_page_config(page_title="FitnessData — Comparison", layout="wide")

# Same thresholds as notebooks/04_comparison.ipynb — exercises need enough sets on
# both sides before a progression curve says anything.
MIN_SETS = 100
LOW_DATA_MIN = 30

OWN_COLOR = "#3b82f6"
REF_COLOR = "#f59e0b"
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def workouts_per_week(df: pd.DataFrame) -> pd.Series:
    workout_dates = df.groupby("workout_id")["date"].first()
    return workout_dates.dt.to_period("W").value_counts().sort_index()


def weekday_share(df: pd.DataFrame) -> pd.Series:
    counts = df.groupby("workout_id")["day_of_week"].first().value_counts()
    return counts.reindex(DAY_ORDER, fill_value=0) / counts.sum()


def normalized_progression(df: pd.DataFrame, exercise: str) -> pd.Series:
    """Weekly best estimated 1RM for one exercise, as % of that lifter's own peak,
    aligned to weeks since their own first logged set of it."""
    ex = df[df["exercise_name"] == exercise]
    weeks = ((ex["date"] - ex["date"].min()).dt.days // 7).astype(int)
    weekly_best = ex.groupby(weeks)["estimated_1rm"].max()
    return weekly_best / weekly_best.max() * 100


def peak_position_pct(df: pd.DataFrame, exercise: str) -> float:
    """How far into a lifter's own timeline the peak sits, in % of the total span."""
    curve = normalized_progression(df, exercise)
    span = curve.index.max()
    return curve.idxmax() / span * 100 if span else 0.0


st.title("Comparison")
st.caption(
    "Own training data against a reference lifter's log: "
    "[721 Weight Training Workouts](https://www.kaggle.com/datasets/joep89/weightlifting/data) by "
    "joep89 (Kaggle). No body weight or age is known for the reference lifter, so absolute strength "
    "is deliberately left out — only training frequency and the *shape* of progression are compared."
)

if not REFERENCE_FILE.exists():
    st.error(
        "`data/clean/reference_sets.csv` is missing. "
        "Run `notebooks/04_comparison.ipynb` to generate it."
    )
    st.stop()

own = load_sets()
ref = load_reference()

# --- Training frequency ------------------------------------------------------

st.subheader("Training Frequency")

own_weekly = workouts_per_week(own)
ref_weekly = workouts_per_week(ref)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Own workouts/week", f"{own_weekly.mean():.2f}")
col2.metric("Reference workouts/week", f"{ref_weekly.mean():.2f}")
col3.metric("Own span", f"{own['date'].min():%Y} – {own['date'].max():%Y}")
col4.metric("Reference span", f"{ref['date'].min():%Y} – {ref['date'].max():%Y}")

left, right = st.columns(2)

max_week = int(max(own_weekly.max(), ref_weekly.max()))
fig_freq = go.Figure()
for label, series, color in [("Own", own_weekly, OWN_COLOR), ("Reference", ref_weekly, REF_COLOR)]:
    counts = series.value_counts().reindex(range(1, max_week + 1), fill_value=0)
    # Share of weeks, so the two lifters' different data spans stay comparable
    fig_freq.add_trace(
        go.Bar(x=counts.index, y=counts / counts.sum(), name=label, marker_color=color)
    )
fig_freq.update_layout(
    barmode="group",
    xaxis_title="Workouts in a week",
    yaxis_title="Share of weeks",
    height=360,
    margin=dict(l=40, r=20, t=20, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
fig_freq.update_xaxes(dtick=1)
left.plotly_chart(disable_zoom(fig_freq), width="stretch", config=PLOTLY_CONFIG)

fig_dow = go.Figure()
for label, series, color in [
    ("Own", weekday_share(own), OWN_COLOR),
    ("Reference", weekday_share(ref), REF_COLOR),
]:
    fig_dow.add_trace(
        go.Bar(x=[d[:3] for d in DAY_ORDER], y=series.values, name=label, marker_color=color)
    )
fig_dow.update_layout(
    barmode="group",
    xaxis_title="Weekday",
    yaxis_title="Share of workouts",
    height=360,
    margin=dict(l=40, r=20, t=20, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
right.plotly_chart(disable_zoom(fig_dow), width="stretch", config=PLOTLY_CONFIG)

# --- Progression shape -------------------------------------------------------

st.subheader("Progression Shape")
st.caption(
    "Estimated 1RM indexed to each lifter's own peak and aligned to weeks since their own first "
    "logged set — the two datasets are about five years apart, so calendar dates aren't comparable."
)

overlap = pd.DataFrame(
    {
        "own_sets": own["exercise_name"].value_counts(),
        "reference_sets": ref["exercise_name"].value_counts(),
    }
).dropna()
overlap["min_sets"] = overlap[["own_sets", "reference_sets"]].min(axis=1)
overlap = overlap[overlap["min_sets"] >= LOW_DATA_MIN].sort_values("min_sets", ascending=False)

if overlap.empty:
    st.info("No exercises with enough sets in both datasets.")
    st.stop()


def option_label(exercise: str) -> str:
    row = overlap.loc[exercise]
    suffix = " — limited data" if row["min_sets"] < MIN_SETS else ""
    return f"{exercise} (n={int(row['own_sets'])} own / {int(row['reference_sets'])} ref){suffix}"


exercise = st.selectbox(
    "Exercise", overlap.index.tolist(), format_func=option_label, index=0
)

own_curve = normalized_progression(own, exercise)
ref_curve = normalized_progression(ref, exercise)

fig = go.Figure()
fig.add_trace(
    go.Scatter(x=own_curve.index, y=own_curve.values, mode="lines+markers", name="Own",
               line=dict(color=OWN_COLOR), marker=dict(size=4))
)
fig.add_trace(
    go.Scatter(x=ref_curve.index, y=ref_curve.values, mode="lines+markers", name="Reference",
               line=dict(color=REF_COLOR), marker=dict(size=4))
)
fig.update_layout(
    xaxis_title="Weeks since first logged set",
    yaxis_title="% of own peak 1RM",
    height=460,
    margin=dict(l=40, r=20, t=20, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(disable_zoom(fig), width="stretch", config=PLOTLY_CONFIG)

if overlap.loc[exercise, "min_sets"] < MIN_SETS:
    st.warning(
        f"Only {int(overlap.loc[exercise, 'min_sets'])} sets on the thinner side — read this curve "
        "as a rough indication, not a confident trend. A single unusual session can move it."
    )

# --- Peak timing across all shared lifts ------------------------------------

st.subheader("Where the Peak Sits")
st.caption(
    "A peak early in the timeline means the lifter reached their best on that exercise and then held "
    "or declined; a late peak means they were still improving when the data ends."
)

peaks = pd.DataFrame(
    {
        "Exercise": overlap.index,
        "Own peak at": [f"{peak_position_pct(own, ex):.0f}% of own timeline" for ex in overlap.index],
        "Reference peak at": [f"{peak_position_pct(ref, ex):.0f}% of own timeline" for ex in overlap.index],
        "Sets (own / ref)": [
            f"{int(overlap.loc[ex, 'own_sets'])} / {int(overlap.loc[ex, 'reference_sets'])}"
            for ex in overlap.index
        ],
        "Data": np.where(overlap["min_sets"] >= MIN_SETS, "solid", "limited"),
    }
)
st.dataframe(peaks, hide_index=True, width="stretch")
