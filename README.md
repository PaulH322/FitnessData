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

---

## Project Structure

```
FitnessData/
├── data/
│   ├── raw/                    # Original Strong export — do not modify
│   └── clean/                  # Processed output CSVs
│       ├── clean_sets.csv      # Filtered, typed, feature-enriched sets
│       └── workout_summary.csv # One row per workout (aggregated)
├── notebooks/
│   ├── 01_cleaning.ipynb       # Phase 1: Data cleaning & feature engineering
│   ├── 02_sql_setup.ipynb      # Phase 2: SQLite DB setup & queries
│   └── 03_statistics.ipynb     # Phase 3: Descriptive stats & trend analysis
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
Public, interactive companion to the Power BI dashboard, deployed on [Streamlit Community Cloud](https://paul-haubold-fitness.streamlit.app) — auto-redeploys on every push to `master`.

- **Overview**: total workouts, total volume, most-trained muscle group, current week streak, GitHub-style training calendar
- **Strength Progression**: 1RM development per exercise (dropdown filter), personal record highlighted with date
- **Volume & Frequency**: monthly volume, weekday × hour training heatmap, top 10 exercises by volume
- **Statistics Deep Dive**: workout duration distribution, training frequency vs. 1RM correlation

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

This allows comparing strength across different rep ranges and tracking progress over time.
