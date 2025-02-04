UPDATE "bricktracker_sets"
SET "storage" = :value
WHERE "bricktracker_sets"."id" IS NOT DISTINCT FROM :set_id
