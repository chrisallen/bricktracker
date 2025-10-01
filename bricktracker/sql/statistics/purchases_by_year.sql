-- Purchases by Year Statistics
-- Shows statistics grouped by purchase year (when you bought the sets)

SELECT
    strftime('%Y', datetime("bricktracker_sets"."purchase_date", 'unixepoch')) AS "purchase_year",
    COUNT("bricktracker_sets"."id") AS "total_sets",
    COUNT(DISTINCT "bricktracker_sets"."set") AS "unique_sets",
    SUM("rebrickable_sets"."number_of_parts") AS "total_parts",
    ROUND(AVG("rebrickable_sets"."number_of_parts"), 0) AS "avg_parts_per_set",
    -- Financial statistics per purchase year
    COUNT(CASE WHEN "bricktracker_sets"."purchase_price" IS NOT NULL THEN 1 END) AS "sets_with_price",
    ROUND(SUM("bricktracker_sets"."purchase_price"), 2) AS "total_spent",
    ROUND(AVG("bricktracker_sets"."purchase_price"), 2) AS "avg_price_per_set",
    ROUND(MIN("bricktracker_sets"."purchase_price"), 2) AS "min_price",
    ROUND(MAX("bricktracker_sets"."purchase_price"), 2) AS "max_price",
    -- Release year statistics for sets purchased in this year
    MIN("rebrickable_sets"."year") AS "oldest_set_year",
    MAX("rebrickable_sets"."year") AS "newest_set_year",
    ROUND(AVG("rebrickable_sets"."year"), 0) AS "avg_set_release_year",
    -- Problem statistics per purchase year
    COALESCE(SUM("problem_stats"."missing_parts"), 0) AS "missing_parts",
    COALESCE(SUM("problem_stats"."damaged_parts"), 0) AS "damaged_parts",
    -- Minifigure statistics per purchase year
    COALESCE(SUM("minifigure_stats"."minifigure_count"), 0) AS "total_minifigures",
    -- Diversity statistics per purchase year
    COUNT(DISTINCT "rebrickable_sets"."theme_id") AS "unique_themes",
    COUNT(DISTINCT "bricktracker_sets"."purchase_location") AS "unique_purchase_locations",
    -- Monthly statistics within the year
    COUNT(DISTINCT strftime('%m', datetime("bricktracker_sets"."purchase_date", 'unixepoch'))) AS "months_with_purchases"
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
LEFT JOIN (
    SELECT
        "bricktracker_minifigures"."id",
        SUM("bricktracker_minifigures"."quantity") AS "minifigure_count"
    FROM "bricktracker_minifigures"
    GROUP BY "bricktracker_minifigures"."id"
) "minifigure_stats" ON "bricktracker_sets"."id" = "minifigure_stats"."id"
WHERE "bricktracker_sets"."purchase_date" IS NOT NULL
GROUP BY strftime('%Y', datetime("bricktracker_sets"."purchase_date", 'unixepoch'))
ORDER BY "purchase_year" DESC