-- Theme Distribution Statistics
-- Shows statistics grouped by theme

SELECT
    "rebrickable_sets"."theme_id",
    COUNT("bricktracker_sets"."id") AS "set_count",
    COUNT(DISTINCT "bricktracker_sets"."set") AS "unique_set_count",
    SUM("rebrickable_sets"."number_of_parts") AS "total_parts",
    ROUND(AVG("rebrickable_sets"."number_of_parts"), 0) AS "avg_parts_per_set",
    MIN("rebrickable_sets"."year") AS "earliest_year",
    MAX("rebrickable_sets"."year") AS "latest_year",
    -- Financial statistics per theme
    COUNT(CASE WHEN "bricktracker_sets"."purchase_price" IS NOT NULL THEN 1 END) AS "sets_with_price",
    ROUND(SUM("bricktracker_sets"."purchase_price"), 2) AS "total_spent",
    ROUND(AVG("bricktracker_sets"."purchase_price"), 2) AS "avg_price",
    -- Problem statistics per theme
    COALESCE(SUM("problem_stats"."missing_parts"), 0) AS "missing_parts",
    COALESCE(SUM("problem_stats"."damaged_parts"), 0) AS "damaged_parts"
FROM "bricktracker_sets"
INNER JOIN "rebrickable_sets" ON "bricktracker_sets"."set" = "rebrickable_sets"."set"
LEFT JOIN (
    SELECT
        "bricktracker_parts"."id",
        SUM("bricktracker_parts"."missing") AS "missing_parts",
        SUM("bricktracker_parts"."damaged") AS "damaged_parts"
    FROM "bricktracker_parts"
    GROUP BY "bricktracker_parts"."id"
) "problem_stats" ON "bricktracker_sets"."id" = "problem_stats"."id"
GROUP BY "rebrickable_sets"."theme_id"
ORDER BY "set_count" DESC, "rebrickable_sets"."theme_id" ASC