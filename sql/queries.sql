-- =============================================================================
-- FitnessData — analysis queries (Phase 2)
--
-- Dialect: SQLite. Run against data/fitness.db, which is built by
-- notebooks/02_sql_setup.ipynb. These are the same five queries executed there,
-- extracted so they can be run standalone:
--
--     sqlite3 data/fitness.db < sql/queries.sql
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1 — Personal records: the top estimated 1RM per exercise
--
-- The subquery finds the maximum estimate per exercise; the join back to `sets`
-- retrieves the full detail of the set that produced it (weight, reps, date).
-- -----------------------------------------------------------------------------
SELECT
    s.exercise_name,
    ROUND(s.estimated_1rm, 1)  AS personal_record_kg,
    s.weight_kg,
    s.reps,
    DATE(s.date)               AS date
FROM sets s
INNER JOIN (
    SELECT exercise_name, MAX(estimated_1rm) AS max_1rm
    FROM sets
    GROUP BY exercise_name
) pr ON s.exercise_name = pr.exercise_name
     AND s.estimated_1rm = pr.max_1rm
ORDER BY personal_record_kg DESC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- Q2 — Monthly volume trend (RQ1)
--
-- How did total training volume develop month by month over the six years?
-- -----------------------------------------------------------------------------
SELECT
    strftime('%Y-%m', date)        AS month,
    COUNT(DISTINCT workout_id)     AS workouts,
    ROUND(SUM(total_volume_kg), 0) AS total_volume_kg
FROM workouts
GROUP BY month
ORDER BY month;


-- -----------------------------------------------------------------------------
-- Q3 — Most trained exercises
--
-- `workouts_performed` counts distinct sessions rather than raw sets: an exercise
-- done for 5 sets in one session should not outrank one done in 20 sessions.
-- -----------------------------------------------------------------------------
SELECT
    exercise_name,
    COUNT(*)                     AS total_sets,
    COUNT(DISTINCT workout_id)   AS workouts_performed,
    ROUND(AVG(weight_kg), 1)     AS avg_weight_kg,
    ROUND(MAX(estimated_1rm), 1) AS best_1rm_kg
FROM sets
GROUP BY exercise_name
ORDER BY workouts_performed DESC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- Q4 — Yearly training frequency and session profile (RQ4)
--
-- Note: `avg_per_week` divides by a flat 52 weeks, so the first and last calendar
-- year are understated (the data starts in May 2020 and ends in May 2026).
-- -----------------------------------------------------------------------------
SELECT
    strftime('%Y', date)           AS year,
    COUNT(*)                       AS total_workouts,
    ROUND(COUNT(*) / 52.0, 1)      AS avg_per_week,
    ROUND(AVG(duration_min), 1)    AS avg_duration_min,
    ROUND(AVG(total_volume_kg), 0) AS avg_volume_kg
FROM workouts
GROUP BY year
ORDER BY year;


-- -----------------------------------------------------------------------------
-- Q5 — Strength progression for a single lift (RQ2)
--
-- Top 3 working sets per calendar year by estimated 1RM, using a window function.
-- Change the exercise_name filter to inspect any other lift.
-- -----------------------------------------------------------------------------
SELECT
    year,
    DATE(date)              AS date,
    weight_kg,
    reps,
    ROUND(estimated_1rm, 1) AS estimated_1rm_kg
FROM (
    SELECT
        strftime('%Y', date) AS year,
        date,
        weight_kg,
        reps,
        estimated_1rm,
        ROW_NUMBER() OVER (
            PARTITION BY strftime('%Y', date)
            ORDER BY estimated_1rm DESC
        ) AS rn
    FROM sets
    WHERE exercise_name = 'Bench Press (Barbell)'
)
WHERE rn <= 3
ORDER BY year, rn;
