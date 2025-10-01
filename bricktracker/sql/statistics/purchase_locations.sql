-- Purchase Location Statistics
-- Shows statistics grouped by purchase location

SELECT
    "bricktracker_sets"."purchase_location" AS "location_id",
    "bricktracker_metadata_purchase_locations"."name" AS "location_name",
    COUNT("bricktracker_sets"."id") AS "set_count",
    COUNT(DISTINCT "bricktracker_sets"."set") AS "unique_set_count",
    SUM("rebrickable_sets"."number_of_parts") AS "total_parts",
    ROUND(AVG("rebrickable_sets"."number_of_parts"), 0) AS "avg_parts_per_set",
    -- Financial statistics per purchase location
    COUNT(CASE WHEN "bricktracker_sets"."purchase_price" IS NOT NULL THEN 1 END) AS "sets_with_price",
    ROUND(SUM("bricktracker_sets"."purchase_price"), 2) AS "total_spent",
    ROUND(AVG("bricktracker_sets"."purchase_price"), 2) AS "avg_price",
    ROUND(MIN("bricktracker_sets"."purchase_price"), 2) AS "min_price",
    ROUND(MAX("bricktracker_sets"."purchase_price"), 2) AS "max_price",
    -- Date range statistics
    MIN("bricktracker_sets"."purchase_date") AS "first_purchase",
    MAX("bricktracker_sets"."purchase_date") AS "latest_purchase",
    -- Problem statistics per purchase location
    COALESCE(SUM("problem_stats"."missing_parts"), 0) AS "missing_parts",
    COALESCE(SUM("problem_stats"."damaged_parts"), 0) AS "damaged_parts",
    -- Minifigure statistics per purchase location
    COALESCE(SUM("minifigure_stats"."minifigure_count"), 0) AS "total_minifigures"
FROM "bricktracker_sets"
INNER JOIN "rebrickable_sets" ON "bricktracker_sets"."set" = "rebrickable_sets"."set"
LEFT JOIN "bricktracker_metadata_purchase_locations" ON "bricktracker_sets"."purchase_location" = "bricktracker_metadata_purchase_locations"."id"
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
WHERE "bricktracker_sets"."purchase_location" IS NOT NULL
GROUP BY "bricktracker_sets"."purchase_location", "bricktracker_metadata_purchase_locations"."name"
ORDER BY "set_count" DESC, "location_name" ASC