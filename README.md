# Personal Fitness Analytics

A project analyzing 6 years of personal strength training data (850 workouts, May 2020 – May 2026) exported from the [Strong](https://www.strong.app/) app.

**Live dashboard: [paul-haubold-fitness.streamlit.app](https://paul-haubold-fitness.streamlit.app)**

---

## Dataset

Source: Strong app CSV export (`data/raw/strong_userdata.csv`)

| Column | Description |
|---|---|
| `Workout #` | Unique workout ID |
| `Date` | Timestamp of workout |
| `Workout Name` | User-defined workout label |
| `Duration (sec)` | Total workout duration |
| `Exercise Name` | Name of the exercise |
| `Set Order` | Set number, or `W` / `Rest Timer` / `Note` |
| `Weight (kg)` | Weight used |
| `Reps` | Repetitions performed |
| `RPE` | Rate of Perceived Exertion (rarely filled) |

Raw data: ~23,000 rows · 850 workouts · semicolon-delimited · one row per set

Reference data (Phase 6 only): [721 Weight Training Workouts](https://www.kaggle.com/datasets/joep89/weightlifting/data) by joep89 (Kaggle) — another lifter's 3-year training log, same one-row-per-set shape, used for a frequency/progression comparison, not a Strong export.

---

## Project Structure

```
FitnessData/
├── data/
│   ├── raw/                    # Original Strong export — do not modify
│   │   └── weightlifting_721_workouts.csv  # Reference lifter (Phase 6), from Kaggle
│   └── clean/                  # Processed output CSVs
│       ├── clean_sets.csv      # Filtered, typed, feature-enriched sets
│       ├── workout_summary.csv # One row per workout (aggregated)
│       └── reference_sets.csv  # Cleaned reference lifter data (Phase 6)
├── notebooks/
│   ├── 01_cleaning.ipynb       # Phase 1: Data cleaning & feature engineering
│   ├── 02_sql_setup.ipynb      # Phase 2: SQLite DB setup & queries
│   ├── 03_statistics.ipynb     # Phase 3: Descriptive stats & trend analysis
│   └── 04_comparison.ipynb     # Phase 6: Comparison against a reference lifter
├── sql/
│   ├── schema.sql              # Table definitions
│   └── queries.sql             # Analysis queries
├── powerbi/                    # Power BI dashboard (.pbix)
├── streamlit_app/              # Streamlit dashboard (Phase 5)
│   ├── app.py                  # Entry point / Overview page
│   ├── pages/                  # Strength Progression, Volume & Frequency, Statistics
│   └── requirements.txt
└── README.md
```

---

## Phases

### Phase 1 — Data Cleaning & Feature Engineering (Python / Pandas)
- Filter out non-set rows (`W` warmups, `Rest Timer`, `Note`)
- Parse dates, fix data types
- Calculate **estimated 1RM** per set (Epley formula: `weight × (1 + reps / 30)`)
- Calculate **volume** per set (`weight × reps`)
- Aggregate per workout: total volume, total sets, duration in minutes
- Export to `data/clean/`

### Phase 2 — SQL Analysis (SQLite)
- Load cleaned data into a local `fitness.db`
- Tables: `workouts`, `sets`, `exercises`
- Example queries: personal records per exercise, monthly volume, most-trained exercises

### Phase 3 — Statistics
- Descriptive statistics: workout duration, volume per session
- Trend analysis: is training volume growing over 6 years?
- Correlation: does training frequency relate to 1RM development?

### Phase 4 — Dashboard (Power BI / Excel)
- Weekly training heatmap
- Strength progression for key lifts (Bench Press, Pull Up, ...)
- Volume trends over time

### Phase 5 — Streamlit Dashboard
Interactive companion to the Power BI dashboard, live at [paul-haubold-fitness.streamlit.app](https://paul-haubold-fitness.streamlit.app).

- Overview: total workouts, total volume, most-trained muscle group, current week streak, training calendar
- Strength progression: 1RM development per exercise, personal record highlighted with date
- Volume & frequency: monthly volume, weekday × hour training heatmap, top 10 exercises by volume
- Statistics: workout duration distribution, training frequency vs. 1RM correlation
- Strength standards: four key lifts (Pull Ups, Incline Dumbbell Bench Press, Dips, Romanian Deadlift) benchmarked against [strengthlevel.com](https://strengthlevel.com/strength-standards) community standards at 80 kg body weight

### Phase 6 — Comparative Analysis
No bodyweight/age is available for other lifters, so this phase skips absolute-strength comparisons and
instead looks at training frequency patterns and the *shape* of strength progression over time, against
a reference lifter's dataset: [721 Weight Training Workouts](https://www.kaggle.com/datasets/joep89/weightlifting/data) by joep89 (Kaggle).

- Training frequency: workouts/week distribution, weekday training pattern
- Progression shape: exercises with enough sets on both sides, in two tiers — solid (≥ 100 sets) and limited-data (30–99 sets, labeled as such) — each lifter's estimated 1RM indexed to their own peak and aligned by weeks since their first logged set, comparing trajectory shape, not absolute numbers

---

## Setup

```bash
pip install pandas matplotlib seaborn jupyter
```

Open notebooks in order starting with `notebooks/01_cleaning.ipynb`.

To run the Streamlit dashboard locally:

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

---

## Key Metric: Estimated 1RM

The **Epley formula** estimates the theoretical one-rep maximum from any set:

```
1RM = weight × (1 + reps / 30)
```

This makes strength comparable across different rep ranges and trackable over time.
