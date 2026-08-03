-- =============================================================================
-- FitnessData — SQLite schema (Phase 2)
--
-- The database is built from the Phase 1 output CSVs by notebooks/02_sql_setup.ipynb,
-- which lets pandas create the tables via to_sql(). This file documents the intended
-- relational design explicitly and can be used to create an empty database by hand:
--
--     sqlite3 fitness.db < sql/schema.sql
--
-- Source of truth for the data itself: data/clean/clean_sets.csv
--                                      data/clean/workout_summary.csv
-- =============================================================================

-- One row per training session (aggregated from the set level).
-- Only sessions that pass the Phase 1 quality filter are stored:
--   duration between 45 and 100 minutes AND at least 15 working sets.
CREATE TABLE IF NOT EXISTS workouts (
    workout_id          INTEGER PRIMARY KEY,
    date                TIMESTAMP NOT NULL,
    workout_name        TEXT,
    duration_min        REAL,
    total_sets          INTEGER NOT NULL,
    total_volume_kg     REAL    NOT NULL,
    peak_estimated_1rm  REAL,
    unique_exercises    INTEGER
);

-- Lookup table derived from the sets: one row per distinct exercise.
CREATE TABLE IF NOT EXISTS exercises (
    exercise_name  TEXT PRIMARY KEY,
    total_sets     INTEGER NOT NULL,
    first_seen     TIMESTAMP,
    last_seen      TIMESTAMP
);

-- One row per working set. Warmups ('W'), drop sets ('D'), rest timers and
-- notes are removed in Phase 1 and never reach this table.
--   volume_kg     = weight_kg * reps
--   estimated_1rm = Epley: weight_kg * (1 + reps / 30), or weight_kg when reps = 1
--
-- Note: the notebook loads this table with pandas `to_sql(..., index=False)`, which
-- creates no surrogate key. A set is identified by (workout_id, exercise_name,
-- set_order); SQLite's implicit rowid serves as the physical key.
CREATE TABLE IF NOT EXISTS sets (
    workout_id     INTEGER NOT NULL,
    date           TIMESTAMP NOT NULL,
    exercise_name  TEXT    NOT NULL,
    set_order      INTEGER,
    weight_kg      REAL    NOT NULL,
    reps           INTEGER NOT NULL,
    rpe            REAL,
    volume_kg      REAL    NOT NULL,
    estimated_1rm  REAL    NOT NULL,
    FOREIGN KEY (workout_id)    REFERENCES workouts (workout_id),
    FOREIGN KEY (exercise_name) REFERENCES exercises (exercise_name)
);

-- Indexes for the access patterns used in queries.sql:
-- filtering sets by exercise, and grouping either table by date.
CREATE INDEX IF NOT EXISTS idx_sets_exercise ON sets (exercise_name);
CREATE INDEX IF NOT EXISTS idx_sets_date     ON sets (date);
CREATE INDEX IF NOT EXISTS idx_sets_workout  ON sets (workout_id);
CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts (date);
