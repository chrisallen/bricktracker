SELECT COUNT(*) as count
FROM "bricktracker_sets"
INNER JOIN "rebrickable_sets" ON "bricktracker_sets"."set" = "rebrickable_sets"."set"
WHERE "rebrickable_sets"."theme_id" = {{ theme_id }}