-- Statistics Overview Query
-- Provides statistics for BrickTracker dashboard

SELECT
    -- Basic counts
    (SELECT COUNT(*) FROM "bricktracker_sets") AS "total_sets",
    (SELECT COUNT(DISTINCT "bricktracker_sets"."set") FROM "bricktracker_sets") AS "unique_sets",
    (SELECT COUNT(*) FROM "rebrickable_sets" WHERE "rebrickable_sets"."set" IN (SELECT DISTINCT "set" FROM "bricktracker_sets")) AS "unique_rebrickable_sets",

    -- Parts statistics
    (SELECT COUNT(*) FROM "bricktracker_parts") AS "total_part_instances",
    (SELECT SUM("bricktracker_parts"."quantity") FROM "bricktracker_parts") AS "total_parts_count",
    (SELECT COUNT(DISTINCT "bricktracker_parts"."part") FROM "bricktracker_parts") AS "unique_parts",
    (SELECT SUM("bricktracker_parts"."missing") FROM "bricktracker_parts") AS "total_missing_parts",
    (SELECT SUM("bricktracker_parts"."damaged") FROM "bricktracker_parts") AS "total_damaged_parts",

    -- Minifigures statistics
    (SELECT COUNT(*) FROM "bricktracker_minifigures") AS "total_minifigure_instances",
    (SELECT SUM("bricktracker_minifigures"."quantity") FROM "bricktracker_minifigures") AS "total_minifigures_count",
    (SELECT COUNT(DISTINCT "bricktracker_minifigures"."figure") FROM "bricktracker_minifigures") AS "unique_minifigures",

    -- Financial statistics
    (SELECT COUNT(*) FROM "bricktracker_sets" WHERE "purchase_price" IS NOT NULL) AS "sets_with_price",
    (SELECT ROUND(SUM("purchase_price"), 2) FROM "bricktracker_sets" WHERE "purchase_price" IS NOT NULL) AS "total_cost",
    (SELECT ROUND(AVG("purchase_price"), 2) FROM "bricktracker_sets" WHERE "purchase_price" IS NOT NULL) AS "average_cost",
    (SELECT ROUND(MIN("purchase_price"), 2) FROM "bricktracker_sets" WHERE "purchase_price" IS NOT NULL) AS "minimum_cost",
    (SELECT ROUND(MAX("purchase_price"), 2) FROM "bricktracker_sets" WHERE "purchase_price" IS NOT NULL) AS "maximum_cost",

    -- Storage and location statistics
    (SELECT COUNT(DISTINCT "storage") FROM "bricktracker_sets" WHERE "storage" IS NOT NULL) AS "storage_locations_used",
    (SELECT COUNT(DISTINCT "purchase_location") FROM "bricktracker_sets" WHERE "purchase_location" IS NOT NULL) AS "purchase_locations_used",
    (SELECT COUNT(*) FROM "bricktracker_sets" WHERE "storage" IS NOT NULL) AS "sets_with_storage",
    (SELECT COUNT(*) FROM "bricktracker_sets" WHERE "purchase_location" IS NOT NULL) AS "sets_with_purchase_location"