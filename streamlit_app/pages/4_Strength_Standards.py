import plotly.graph_objects as go
import streamlit as st

from utils import PLOTLY_CONFIG, disable_zoom, load_sets

st.set_page_config(page_title="FitnessData — Strength Standards", layout="wide")

BODYWEIGHT_KG = 79

# Reference values: strengthlevel.com community standards at 80 kg body weight
# (the nearest published bracket to BODYWEIGHT_KG), men, in kg.
# Pull Ups / Dips standards are added weight (belt), consistent with how Strong
# logs these two exercises (weight_kg = added weight, not total body weight).
STANDARDS = {
    "Pull Ups (added weight)": {
        "exercise": "Pull Up",
        "thresholds": {"Beginner": -2, "Novice": 14, "Intermediate": 33, "Advanced": 54, "Elite": 75},
    },
    "Incline Dumbbell Bench Press (1RM, per dumbbell)": {
        "exercise": "Incline Bench Press (Dumbbell)",
        "thresholds": {"Beginner": 22, "Novice": 29, "Intermediate": 39, "Advanced": 50, "Elite": 62},
    },
    "Dips (added weight)": {
        "exercise": "Chest Dip",
        "thresholds": {"Beginner": 5, "Novice": 26, "Intermediate": 52, "Advanced": 81, "Elite": 111},
    },
    "Romanian Deadlift (1RM)": {
        "exercise": "Romanian Deadlift (Barbell)",
        "thresholds": {"Beginner": 65, "Novice": 92, "Intermediate": 125, "Advanced": 163, "Elite": 203},
    },
}

# Gray for "below Beginner", then one color per level from Beginner (red) to Elite (green).
BAND_COLORS = ["#e5e7eb", "#fecaca", "#fed7aa", "#fef08a", "#bbf7d0", "#4ade80"]


def classify(value: float, thresholds: dict) -> str:
    level = "Below Beginner"
    for name, threshold in thresholds.items():
        if value >= threshold:
            level = name
    return level


def bullet_chart(user_value: float, thresholds: dict) -> go.Figure:
    names = list(thresholds.keys())
    bounds = list(thresholds.values())

    floor = min(0, bounds[0], user_value)
    ceiling = bounds[-1] + (bounds[-1] - floor) * 0.15
    edges = [floor] + bounds + [ceiling]
    labels = ["Below Beginner"] + names

    fig = go.Figure()
    for label, base, width, color in zip(
        labels, edges[:-1], [b - a for a, b in zip(edges[:-1], edges[1:])], BAND_COLORS
    ):
        if width <= 0:
            continue
        fig.add_trace(
            go.Bar(
                x=[width],
                y=[""],
                base=[base],
                orientation="h",
                marker_color=color,
                name=label,
                hovertemplate=f"{label}<extra></extra>",
            )
        )
    fig.add_shape(type="line", x0=user_value, x1=user_value, y0=-0.4, y1=0.4, line=dict(color="#111827", width=3))
    fig.add_annotation(
        x=user_value,
        y=0.45,
        text=f"You: {user_value:.1f} kg",
        showarrow=False,
        yanchor="bottom",
        font=dict(size=12, color="#111827"),
        bgcolor="#ffffff",
        bordercolor="#111827",
        borderwidth=1,
        borderpad=3,
    )
    fig.update_layout(
        barmode="stack",
        height=130,
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title="kg",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, traceorder="normal"),
    )
    fig.update_xaxes(range=[floor, ceiling])
    fig.update_yaxes(showticklabels=False)
    return disable_zoom(fig)


st.title("Strength Standards")
st.caption(
    f"Your best lifts compared against strengthlevel.com's community standards "
    f"for men at 80 kg body weight — the closest published bracket to your {BODYWEIGHT_KG} kg."
)

sets_df = load_sets()

for label, config in STANDARDS.items():
    ex_df = sets_df[sets_df["exercise_name"] == config["exercise"]]
    if ex_df.empty:
        continue
    user_value = ex_df["estimated_1rm"].max()
    level = classify(user_value, config["thresholds"])

    st.subheader(label)
    st.plotly_chart(bullet_chart(user_value, config["thresholds"]), width="stretch", config=PLOTLY_CONFIG)
    st.caption(f"Your level: **{level}**")
