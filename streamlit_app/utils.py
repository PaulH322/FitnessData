"""Shared data loading and lookups for the Streamlit dashboard.

Reuses the Phase 1 cleaned CSVs directly — no re-derivation of cleaning logic.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "clean"

# Strong's export has no muscle-group column — exercise names are mapped by hand.
# Compound lifts are assigned to their primary mover (e.g. Deadlift -> Back,
# per Strong's own default categorization; Close-Grip Bench -> Arms, triceps-focused).
MUSCLE_GROUPS = {
    # Chest
    "Bench Press (Barbell)": "Chest",
    "Incline Bench Press (Barbell)": "Chest",
    "Incline Bench Press (Dumbbell)": "Chest",
    "Incline Bench Press (Smith Machine)": "Chest",
    "Incline Chest Press (Machine)": "Chest",
    "Chest Press (Machine)": "Chest",
    "Chest Fly": "Chest",
    "Chest Dip": "Chest",
    "Cable Crossover": "Chest",
    "Push Up": "Chest",
    "Push Up (Band)": "Chest",
    "Pullover (Dumbbell)": "Chest",
    "Pullover (Machine)": "Chest",
    # Back
    "Bent Over One Arm Row (Dumbbell)": "Back",
    "Bent Over Row (Band)": "Back",
    "Bent Over Row (Barbell)": "Back",
    "Lat Pulldown (Cable)": "Back",
    "Lat Pulldown (Machine)": "Back",
    "Lat Pulldown (Single Arm)": "Back",
    "Lat Pulldown - Underhand (Band)": "Back",
    "Lat Pulldown - Underhand (Cable)": "Back",
    "Seated Row (Cable)": "Back",
    "Seated Row (Machine)": "Back",
    "Iso-Lateral Row (Machine)": "Back",
    "T Bar Row": "Back",
    "Pull Up": "Back",
    "Wide Pull Up": "Back",
    "Archer Pull": "Back",
    "Face Pull (Cable)": "Back",
    "Deadlift (Barbell)": "Back",
    "Deadlift (Dumbbell)": "Back",
    "Romanian Deadlift (Barbell)": "Back",
    "Stiff Leg Deadlift (Dumbbell)": "Back",
    "Sumo Deadlift (Barbell)": "Back",
    "Shrug (Barbell)": "Back",
    "Shrug (Dumbbell)": "Back",
    "Shrug (Machine)": "Back",
    "Back Extension": "Back",
    "schlitten ziehen": "Back",
    # Legs
    "Bulgarian Split Squat": "Legs",
    "Bulgarien Split SMITH": "Legs",
    "Calf Press on Leg Press": "Legs",
    "Front Squat (Barbell)": "Legs",
    "Glute Kickback (Machine)": "Legs",
    "Goblet Squat (Kettlebell)": "Legs",
    "Hack Squat": "Legs",
    "Hack Squat (Barbell)": "Legs",
    "Hip Abductor (Machine)": "Legs",
    "Hip Adductor (Machine)": "Legs",
    "Hip Thrust (Barbell)": "Legs",
    "Leg Extension (Machine)": "Legs",
    "Leg Press": "Legs",
    "Lunge (Dumbbell)": "Legs",
    "Lying Leg Curl (Machine)": "Legs",
    "Pendulum Squat": "Legs",
    "Seated Calf Raise (Plate Loaded)": "Legs",
    "Seated Leg Curl (Machine)": "Legs",
    "Seated Leg Press (Machine)": "Legs",
    "Single Leg Press": "Legs",
    "Split Squat Dumbbell": "Legs",
    "Squat (Barbell)": "Legs",
    "Squat (Smith Machine)": "Legs",
    "Standing Calf Raise (Machine)": "Legs",
    "Standing Leg Curl": "Legs",
    "Kettlebell Swing": "Legs",
    # Shoulders
    "Arnold Press (Dumbbell)": "Shoulders",
    "Front Raise (Barbell)": "Shoulders",
    "Lateral Raise (Cable)": "Shoulders",
    "Lateral Raise (Dumbbell)": "Shoulders",
    "Lateral Raise (Machine)": "Shoulders",
    "Overhead Press (Dumbbell)": "Shoulders",
    "Overhead Press (Smith Machine)": "Shoulders",
    "Reverse Fly (Dumbbell)": "Shoulders",
    "Reverse Fly (Machine)": "Shoulders",
    "Seated Overhead Press (Dumbbell)": "Shoulders",
    "Shoulder Press (Machine)": "Shoulders",
    "Strict Military Press (Barbell)": "Shoulders",
    "Handstand Push Up": "Shoulders",
    "Upright Row (Barbell)": "Shoulders",
    "Upright Row (Cable)": "Shoulders",
    "Upright Row (Dumbbell)": "Shoulders",
    # Arms
    "Bicep Curl (Barbell)": "Arms",
    "Bicep Curl (Cable)": "Arms",
    "Bicep Curl (Dumbbell)": "Arms",
    "Bicep Curl (Machine)": "Arms",
    "Hammer Curl (Dumbbell)": "Arms",
    "Incline Curl (Dumbbell)": "Arms",
    "Preacher Curl (Barbell)": "Arms",
    "Preacher Curl (Dumbbell)": "Arms",
    "Preacher Curl (Machine)": "Arms",
    "Reverse Cable Curl": "Arms",
    "Wrist Curl Cable": "Arms",
    "Skullcrusher (Barbell)": "Arms",
    "Triceps Dip": "Arms",
    "Triceps Extension": "Arms",
    "Triceps Extension (Cable)": "Arms",
    "Triceps Extension (Dumbbell)": "Arms",
    "Triceps Extension (Machine)": "Arms",
    "Triceps Extensions Stange": "Arms",
    "Triceps Pushdown (Cable - Straight Bar)": "Arms",
    "Bench Press - Close Grip (Barbell)": "Arms",
    # Core
    "Ab Wheel": "Core",
    "Cable Crunch": "Core",
    "Cross Body Crunch": "Core",
    "Crunch": "Core",
    "Crunch (Machine)": "Core",
    "Knee Raise (Captain's Chair)": "Core",
}


def muscle_group(exercise_name: str) -> str:
    return MUSCLE_GROUPS.get(exercise_name, "Other")


@st.cache_data
def load_sets() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "clean_sets.csv", parse_dates=["date"])
    df["muscle_group"] = df["exercise_name"].map(muscle_group)
    return df


@st.cache_data
def load_summary() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "workout_summary.csv", parse_dates=["date"])


PLOTLY_CONFIG = {"displayModeBar": False}


def disable_zoom(fig):
    """Locks pan/zoom so charts stay static for portfolio viewing."""
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig
