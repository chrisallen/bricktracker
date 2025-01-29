UPDATE "bricktracker_sets"
SET "theme" = :theme
WHERE "bricktracker_sets"."id" IS NOT DISTINCT FROM :id
