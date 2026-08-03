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

Raw data: ~23,000 rows · 849 workouts · semicolon-delimited · one row per set
After cleaning: **17,397 working sets · 756 workouts · ~8,837 tonnes lifted**

Reference data (Phase 6 only): [721 Weight Training Workouts](https://www.kaggle.com/datasets/joep89/weightlifting/data) by joep89 (Kaggle) — another lifter's 3-year training log, same one-row-per-set shape, used for a frequency/progression comparison, not a Strong export.

---

## Research Questions

The analysis is built around five questions, stated up front in `01_cleaning.ipynb` and answered
explicitly in `03_statistics.ipynb` §10:

| # | Question | Answered in |
|---|---|---|
| RQ1 | How did total training volume develop over the six years? | `03_statistics` §4 |
| RQ2 | How did strength (estimated 1RM) develop per key exercise, and how fast? | `03_statistics` §5, §7 |
| RQ3 | Does training more often in a month go together with a higher 1RM that month? | `03_statistics` §6 |
| RQ4 | What temporal patterns exist — frequency, weekday habits, consistency? | `03_statistics` §3, §9 |
| RQ5 | How does this compare to external reference points? | `04_comparison`, dashboard |

Headline answers: volume shows **no reliable long-term trend** (p = 0.10); strength gains are
significant for 2 of 6 key lifts (Chest Dip +2.9 kg/year, Overhead Press +2.0 kg/year); training
frequency and monthly 1RM are **not** positively correlated at monthly resolution.

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
│   ├── 03_statistics.ipynb     # Phase 3: Stats, correlation, trend models, conclusions
│   └── 04_comparison.ipynb     # Phase 6: Comparison against a reference lifter
├── sql/
│   ├── schema.sql              # Table definitions
│   └── queries.sql             # Analysis queries
├── powerbi/                    # Power BI dashboard (.pbix)
├── streamlit_app/              # Streamlit dashboard (Phase 5)
│   ├── app.py                  # Entry point / Overview page
│   ├── pages/                  # Strength Progression, Volume & Frequency, Statistics, Standards, Comparison
│   └── requirements.txt
└── README.md
```

---

## Phases

### Phase 1 — Data Cleaning & Feature Engineering (Python / Pandas)
- Document a missing-value strategy (structural nulls — no imputation)
- Check duplicates: 2,695 in the raw file, but only **2** among real working sets
- Filter out non-set rows (`W` warmups, `D` drop sets, `Rest Timer`, `Note`) — each with a stated reason
- Parse dates, fix data types
- Calculate **estimated 1RM** per set (Epley formula: `weight × (1 + reps / 30)`)
- Calculate **volume** per set (`weight × reps`)
- Diagnose outliers visually *before* removing them (rep boxplot on a log axis; per-exercise weight boxplots)
- Aggregate per workout, then apply a quality filter (45–100 min, ≥ 15 sets) that is justified with
  distributions, an exclusion breakdown, and a sensitivity check (r = 0.988 vs. unfiltered)
- Export to `data/clean/`

### Phase 2 — SQL Analysis (SQLite)
- Load cleaned data into a local `fitness.db`
- Tables: `workouts`, `sets`, `exercises`
- Example queries: personal records per exercise, monthly volume, most-trained exercises

### Phase 3 — Statistics
- Descriptive statistics and distributions (histograms + boxplots)
- Trend analysis: is training volume growing over 6 years?
- Correlation matrix over workout variables, plus per-exercise correlation **with p-values**
- Linear trend models (OLS): slope in kg/year, R², significance, 95% confidence band
- Answers to RQ1–RQ4, followed by conclusions, limitations and recommendations

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
- Comparison: the Phase 6 analysis made interactive — frequency charts, a per-exercise progression overlay, and a peak-timing table across all shared lifts

### Phase 6 — Comparative Analysis
No bodyweight/age is available for other lifters, so this phase skips absolute-strength comparisons and
instead looks at training frequency patterns and the *shape* of strength progression over time, against
a reference lifter's dataset: [721 Weight Training Workouts](https://www.kaggle.com/datasets/joep89/weightlifting/data) by joep89 (Kaggle).

- Training frequency: workouts/week distribution, weekday training pattern
- Progression shape: exercises with enough sets on both sides, in two tiers — solid (≥ 100 sets) and limited-data (30–99 sets, labeled as such) — each lifter's estimated 1RM indexed to their own peak and aligned by weeks since their first logged set, comparing trajectory shape, not absolute numbers

---

## Setup

```bash
pip install pandas numpy matplotlib seaborn scipy jupyter
```

Open the notebooks in order starting with `notebooks/01_cleaning.ipynb`; each one depends on the
output of the previous (`01 → 02 → 03 → 04`).

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
